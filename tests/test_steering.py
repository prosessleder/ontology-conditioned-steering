import math
from types import SimpleNamespace

import pytest

from ontology_steering.steering import (add_direction, capture_last_token,
                                      estimate_direction, random_direction)


def test_paired_estimator_and_scale():
    vector = estimate_direction([[3., 4.], [3., 4.]], [[0., 4.], [0., 4.]])
    assert vector["direction"] == [1., 0.]
    assert vector["activation_scale"] == 4.5
    assert vector["difference_norm"] == 3.
    with pytest.raises(ValueError, match="Degenerate"):
        estimate_direction([[1.]], [[1.]])
    with pytest.raises(ValueError, match="Nonfinite"):
        estimate_direction([[float("nan")]], [[1.]])


def test_random_is_reproducible_norm_matched_control():
    a = random_direction(16, 9)
    assert a == random_direction(16, 9)
    assert a != random_direction(16, 10)
    assert math.sqrt(sum(x * x for x in a)) == pytest.approx(1.)


def tiny_qwen(device="cpu", dtype="float32"):
    torch = pytest.importorskip("torch")
    transformers = pytest.importorskip("transformers")
    torch.manual_seed(123)
    config = transformers.Qwen2Config(vocab_size=32, hidden_size=16, intermediate_size=32,
                                     num_hidden_layers=2, num_attention_heads=2,
                                     num_key_value_heads=1, max_position_embeddings=64,
                                     attention_dropout=0., eos_token_id=None)
    config._attn_implementation = "eager"
    model = transformers.Qwen2ForCausalLM(config).to(device=device, dtype=getattr(torch, dtype)).eval()
    inputs = {"input_ids": torch.tensor([[3, 4, 5]], device=device),
              "attention_mask": torch.ones((1, 3), dtype=torch.long, device=device)}
    return torch, model, inputs


@pytest.mark.parametrize("device,dtype", [("cpu", "float32"), ("mps", "float32"), ("mps", "float16")])
def test_real_qwen_hooks_propagate_and_zero_preserves_generation(device, dtype):
    torch = pytest.importorskip("torch")
    if device == "mps" and not torch.backends.mps.is_available():
        pytest.skip("MPS unavailable")
    from ontology_steering.runner import generate_tokens
    torch, model, inputs = tiny_qwen(device, dtype)
    config = {"max_new_tokens": 3, "do_sample": False}
    baseline, _ = generate_tokens(model, inputs, config, 11)
    with add_direction(model, 0, [1.] + [0.] * 15, 0, 1.) as trace:
        zero, _ = generate_tokens(model, inputs, config, 11)
    assert zero == baseline
    assert [t["sequence_length"] for t in trace] == [3, 1, 1]
    assert [t["position"] for t in trace] == [2, 0, 0]
    with torch.inference_mode(), capture_last_token(model, [0]) as original:
        baseline_logits = model(**inputs, use_cache=False).logits
    with torch.inference_mode(), add_direction(model, 0, [1.] + [0.] * 15, 1., 1.), \
            capture_last_token(model, [0]) as changed:
        changed_logits = model(**inputs, use_cache=False).logits
    assert changed[0][0] - original[0][0] == pytest.approx(1., abs=1e-3 if dtype == "float16" else 1e-6)
    assert changed[0][1:] == pytest.approx(original[0][1:], abs=1e-6)
    assert torch.equal(baseline_logits[:, :-1, :], changed_logits[:, :-1, :])
    assert not torch.equal(baseline_logits[:, -1, :], changed_logits[:, -1, :])
    assert len(model.model.layers[0]._forward_hooks) == 0


def test_hook_cleanup_on_failure_and_tuple_output():
    torch = pytest.importorskip("torch")
    class Layer(torch.nn.Module):
        def forward(self, h):
            return h, "preserved"
    model = SimpleNamespace(model=SimpleNamespace(layers=[Layer()]))
    h = torch.zeros((1, 3, 2))
    with add_direction(model, 0, [1., 0.], .5, 2.):
        result, extra = model.model.layers[0](h)
    assert extra == "preserved"
    assert result[0].tolist() == [[0., 0.], [0., 0.], [1., 0.]]
    assert h.sum().item() == 0
    with pytest.raises(RuntimeError):
        with add_direction(model, 0, [1., 0.], .5, 2.):
            raise RuntimeError("intentional")
    assert not model.model.layers[0]._forward_hooks


def test_freeze_and_test_run_policy_end_to_end(tmp_path, monkeypatch):
    """Exercise the CLI freeze and real tiny-model loop without pretrained weights."""
    import json
    from argparse import Namespace
    from ontology_steering import runner
    from ontology_steering.cli import freeze
    from ontology_steering.dataset import reference_response, write_dataset
    from ontology_steering.evaluate import evaluate_response
    from ontology_steering.steering import read_jsonl, sha256_file, write_json
    torch, model, _ = tiny_qwen()
    experiment = tmp_path / "experiment"
    experiment.mkdir()
    for version in ("v1", "v2"):
        (experiment / f"ontology-{version}.md").write_text(version + " test ontology")
    data = tmp_path / "data"
    write_dataset(data, per_family=1)
    config = {"model_id": "test/tiny", "model_revision": "a" * 40, "device": "cpu",
              "dtype": "float32", "layers": [0], "alphas": [0], "seeds": [11],
              "max_context_tokens": 64, "max_new_tokens": 3}
    vector_path = tmp_path / "vectors.json"
    write_json(vector_path, {"provenance": config, "training_family_ids": ["heat_shape"],
                            "ontology_sha256": {v: sha256_file(experiment / f"ontology-{v}.md") for v in ("v1", "v2")},
                            "vectors": {f"{v}:0": {"direction": [1.] + [0.] * 15,
                                                   "activation_scale": 1., "ontology_version": v}
                                        for v in ("v1", "v2")}})
    dev_path = tmp_path / "dev-outputs.jsonl"
    with dev_path.open("w") as handle:
        for case in read_jsonl(data / "dev.jsonl"):
            evaluation = evaluate_response(case, reference_response(case))
            evaluation["operational_success"] = True
            for condition in ("C", "current:l0:a0"):
                record = {"id": case["id"], "family_id": case["family_id"], "ontology_version": case["ontology_version"],
                          "split": "dev", "seed": 11, "condition": condition, "alpha": 0, "layer": 0,
                          "expected_status": case["expected_status"], "requested_concept": case["requested_concept"],
                          "evaluation": evaluation, "prompt_baseline": "C", "prompt_sha256": "same",
                          "provenance": {"config": config, "dataset_sha256": sha256_file(data / "dev.jsonl"),
                                         "vectors_sha256": sha256_file(vector_path), "source_sha256": {}}}
                handle.write(json.dumps(record) + "\n")
    selection = tmp_path / "frozen.json"
    freeze(Namespace(dev=[dev_path], vectors=vector_path, data=data, root=tmp_path,
                     out=selection, secondary_config=[]), config)
    class Tokenizer:
        def apply_chat_template(self, messages, **kwargs):
            return json.dumps(messages)
        def __call__(self, text, **kwargs):
            return {"input_ids": torch.tensor([[3, 4, 5]]), "attention_mask": torch.ones((1, 3), dtype=torch.long)}
        def decode(self, ids, **kwargs):
            return "{}"  # Deliberately invalid; confirms grader records failures.
    monkeypatch.setattr(runner, "load_model", lambda config: (model, Tokenizer()))
    monkeypatch.setattr(runner, "provenance", lambda *args: {"config": config, "source_sha256": {}})
    with pytest.raises(ValueError, match="frozen dev selection"):
        runner.run_condition(config, data, "test", "current", tmp_path / "bad.jsonl", tmp_path,
                             vector_file=vector_path, layer=0, alpha=.1, selection_file=selection)
    output = tmp_path / "outputs.jsonl"
    runner.run_condition(config, data, "test", "current", output, tmp_path,
                         vector_file=vector_path, layer=0, alpha=0., selection_file=selection)
    rows = read_jsonl(output)
    assert len(rows) == len(read_jsonl(data / "test.jsonl"))
    assert all(r["context"] and r["input_ids"] and r["output_ids"] for r in rows)
    assert all(len(r["hook_trace"]) == 3 for r in rows)
    assert all(r["evaluation"]["operational_success"] is False for r in rows)
    with pytest.raises(FileExistsError):
        runner.run_condition(config, data, "test", "current", output, tmp_path,
                             vector_file=vector_path, layer=0, alpha=0., selection_file=selection)
