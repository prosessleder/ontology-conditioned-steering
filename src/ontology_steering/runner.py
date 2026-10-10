"""Batch-one Qwen runner with explicit residual hooks and complete provenance."""
from __future__ import annotations

from contextlib import nullcontext
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
import platform
from pathlib import Path
import re
import subprocess
import time

from .prompts import endpoint_text, ontology_for, render_prompt
from .steering import (add_direction, capture_last_token, estimate_direction, hash_value,
                       random_direction, read_jsonl, sha256_file, write_json)


def source_hashes(root):
    return {str(p.relative_to(root)): sha256_file(p)
            for p in sorted((Path(root) / "src").rglob("*.py"))}


def design_hashes(root):
    root = Path(root)
    paths = sorted((root / "experiment").glob("*.md")) + [root / "research" / "hypotheses.md"]
    return {str(p.relative_to(root)): sha256_file(p) for p in paths if p.is_file()}


def load_model(config):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    if not re.fullmatch(r"[0-9a-f]{40}", config["model_revision"]):
        raise ValueError("Model revision must be an immutable 40-character commit")
    device = config.get("device", "mps")
    if device == "mps" and not torch.backends.mps.is_available():
        raise RuntimeError("MPS unavailable; select device=cpu explicitly for a documented pilot")
    dtype = getattr(torch, config.get("dtype", "float16"))
    torch.manual_seed(1729)
    tokenizer = AutoTokenizer.from_pretrained(config["model_id"], revision=config["model_revision"])
    model = AutoModelForCausalLM.from_pretrained(
        config["model_id"], revision=config["model_revision"], torch_dtype=dtype,
        attn_implementation="eager", trust_remote_code=False).to(device).eval()
    return model, tokenizer


def provenance(config, model, tokenizer, root):
    from huggingface_hub import try_to_load_from_cache
    cached = try_to_load_from_cache(config["model_id"], "config.json", revision=config["model_revision"])
    artifacts = {}
    if isinstance(cached, str):
        snapshot = Path(cached).parent
        artifacts = {p.name: sha256_file(p) for p in sorted(snapshot.iterdir())
                     if p.is_file() and p.suffix in (".json", ".safetensors", ".model", ".txt")}
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root,
                                         stderr=subprocess.DEVNULL, text=True).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        commit = None
    return {"model_id": config["model_id"], "model_revision": config["model_revision"],
            "model_artifact_sha256": artifacts,
            "model_config": model.config.to_dict(),
            "chat_template_sha256": hash_value(tokenizer.chat_template),
            "versions": {name: importlib.metadata.version(name)
                         for name in ("torch", "transformers", "tokenizers", "safetensors", "huggingface-hub")},
            "python": platform.python_version(), "platform": platform.platform(),
            "device": config.get("device", "mps"), "dtype": config.get("dtype", "float16"),
            "attention_implementation": "eager", "git_commit": commit,
            "source_sha256": source_hashes(root), "config": config,
            "environment": {key: os.environ.get(key) for key in
                            ("PYTORCH_ENABLE_MPS_FALLBACK", "PYTORCH_MPS_HIGH_WATERMARK_RATIO")}}


def encode(tokenizer, text, model, config):
    inputs = tokenizer(text, add_special_tokens=False, return_tensors="pt")
    n = int(inputs["input_ids"].shape[1])
    limit = min(config.get("max_context_tokens", 4096), model.config.max_position_embeddings)
    if n + config.get("max_new_tokens", 384) > limit:
        raise ValueError(f"Context budget exceeded ({n} input tokens); never silently truncate ontology")
    return {k: v.to(model.device) for k, v in inputs.items()}


def generate_tokens(model, inputs, config, seed):
    """Cached autoregressive loop makes the intervention's token locations explicit."""
    import torch
    generator = torch.Generator(device="cpu").manual_seed(seed)
    eos = getattr(model.generation_config, "eos_token_id", None)
    eos = set(eos if isinstance(eos, list) else [eos])
    emitted, past = [], None
    input_ids = inputs["input_ids"]
    mask = inputs["attention_mask"]
    stopped = "max_new_tokens"
    with torch.inference_mode():
        for step in range(config.get("max_new_tokens", 384)):
            output = model(input_ids=input_ids, attention_mask=mask, past_key_values=past,
                           use_cache=True, logits_to_keep=1)
            logits = output.logits[0, -1, :].float()
            if config.get("do_sample", False):
                temperature = config.get("temperature", 0.7)
                if temperature <= 0:
                    raise ValueError("Sampling temperature must be positive")
                probs = torch.softmax(logits.cpu() / temperature, dim=-1)
                token = int(torch.multinomial(probs, 1, generator=generator).item())
            else:
                token = int(logits.argmax().item())
            emitted.append(token)
            if token in eos:
                stopped = "eos"
                break
            past = output.past_key_values
            input_ids = torch.tensor([[token]], device=model.device)
            mask = torch.cat([mask, mask.new_ones((1, 1))], dim=1)
    return emitted, stopped


def collect_vectors(config, dataset_dir, destination, root, *, pair_file=None):
    import torch
    train_path = Path(dataset_dir) / "train.jsonl"
    pair_path = Path(pair_file) if pair_file else Path(dataset_dir) / "pairs-common.jsonl"
    cases = {r["id"]: r for r in read_jsonl(train_path)}
    pairs = read_jsonl(pair_path)
    if not pairs or any(p["split"] != "train" for p in pairs):
        raise ValueError("Vector construction accepts only nonempty train contrastive pairs")
    model, tokenizer = load_model(config)
    all_data, endpoint_audit = {}, []
    for pair in pairs:
        case = cases[pair["scenario_id"]]
        if case["split"] != "train" or pair["family_id"] != case["family_id"]:
            raise ValueError("Contrastive pair crosses training family/split")
        version = pair["ontology_version"]
        if version != case["ontology_version"]:
            raise ValueError("Contrastive pair version mismatch")
        ontology = ontology_for(version, root)
        for side in ("compatible", "incompatible"):
            text = endpoint_text(tokenizer, case, ontology, pair[f"{side}_response"])
            inputs = encode(tokenizer, text, model, config)
            with torch.inference_mode(), capture_last_token(model, config["layers"]) as captured:
                model(**inputs, use_cache=False, logits_to_keep=1)
            endpoint_audit.append({"pair_id": pair["id"], "scenario_id": case["id"], "side": side,
                                   "corruption_type": pair.get("corruption_type"),
                                   "context": text, "input_ids": inputs["input_ids"][0].cpu().tolist()})
            for layer, value in captured.items():
                group = all_data.setdefault((version, layer), {"compatible": [], "incompatible": []})
                group[side].append(value)
    vectors = {f"{version}:{layer}": dict(estimate_direction(data["compatible"], data["incompatible"]),
                                         ontology_version=version, layer=layer,
                                         direction_kind="paired-compatible-minus-incompatible")
               for (version, layer), data in all_data.items()}
    result = {"schema_version": 1, "vectors": vectors,
              "provenance": provenance(config, model, tokenizer, root),
              "train_sha256": sha256_file(train_path), "pairs_sha256": sha256_file(pair_path),
              "ontology_sha256": {v: sha256_file(Path(root) / "experiment" / f"ontology-{v}.md")
                                  for v in ("v1", "v2")},
              "training_family_ids": sorted({p["family_id"] for p in pairs}),
              "pair_ids": [p["id"] for p in pairs], "endpoint_audit": endpoint_audit,
              "estimator": "unit-normalized mean paired residual difference",
              "scale": "mean endpoint residual L2 norm across both sides of train pairs",
              "extraction_location": "zero-based decoder layer output, final response token, before final RMSNorm"}
    write_json(destination, result)
    return {"vector_file": str(destination), "vectors": len(vectors), "pairs": len(pairs)}


def condition_name(condition, layer=None, alpha=None, random_seed=None):
    if condition == "random":
        return f"random:r{random_seed}:l{layer}:a{alpha:g}"
    return f"{condition}:l{layer}:a{alpha:g}" if condition in ("current", "stale") else condition


def run_condition(config, dataset_dir, split, condition, destination, root, *,
                  vector_file=None, layer=None, alpha=None, selection_file=None,
                  ontology_version=None, limit=None):
    from .evaluate import evaluate_response
    dataset_path = Path(dataset_dir) / f"{split}.jsonl"
    cases = read_jsonl(dataset_path)
    if any(case["split"] != split for case in cases):
        raise ValueError("Dataset file mixes splits")
    if ontology_version:
        cases = [c for c in cases if c["ontology_version"] == ontology_version]
    if condition == "stale":
        cases = [c for c in cases if c["ontology_version"] == "v2"]
    if not cases:
        raise ValueError("No eligible cases")
    vector_payload = json.loads(Path(vector_file).read_text()) if vector_file else None
    if condition in ("current", "stale", "random") and (vector_payload is None or layer is None or alpha is None):
        raise ValueError("Steering requires vector file, layer, alpha")
    if vector_payload and {c["family_id"] for c in cases}.intersection(vector_payload["training_family_ids"]):
        raise ValueError("Evaluation family appears in vector training families")
    if split == "test":
        if selection_file is None:
            raise ValueError("Freeze dev selection before any test runs")
        frozen = json.loads(Path(selection_file).read_text())
        if frozen.get("test_results_seen") is not False:
            raise ValueError("Invalid frozen selection")
        if hash_value(config) not in frozen.get("allowed_config_sha256", [frozen["config_sha256"]]):
            raise ValueError("Test config differs from frozen config")
        if sha256_file(dataset_path) != frozen["test_sha256"]:
            raise ValueError("Test dataset differs from frozen dataset")
        if source_hashes(root) != frozen["source_sha256"]:
            raise ValueError("Test source differs from frozen implementation")
        if design_hashes(root) != frozen["design_sha256"]:
            raise ValueError("Test experimental design differs from frozen protocol")
        for version in ("v1", "v2"):
            if sha256_file(Path(root) / "experiment" / f"ontology-{version}.md") != frozen["ontology_sha256"][version]:
                raise ValueError("Test ontology differs from frozen ontology")
        if vector_payload and sha256_file(vector_file) != frozen["vectors_sha256"]:
            raise ValueError("Test vectors differ from frozen vectors")
        if condition in ("current", "stale", "random") and (layer, alpha) != (
                frozen["selected"]["layer"], frozen["selected"]["alpha"]):
            raise ValueError("Test intervention differs from frozen dev selection")
        if limit is not None:
            raise ValueError("Limited test runs are prohibited; pilot on dev")
    if limit is not None:
        cases = cases[:limit]
    model, tokenizer = load_model(config)
    if vector_payload and (vector_payload["provenance"]["model_id"],
                           vector_payload["provenance"]["model_revision"]) != (
                               config["model_id"], config["model_revision"]):
        raise ValueError("Vector model and run model must match")
    run_provenance = provenance(config, model, tokenizer, root)
    run_provenance.update(dataset_sha256=sha256_file(dataset_path),
                          vectors_sha256=sha256_file(vector_file) if vector_file else None,
                          selection_sha256=sha256_file(selection_file) if selection_file else None)
    destination = Path(destination)
    label = condition_name(condition, layer, alpha, config.get("random_vector_seed", 314159))
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive create prevents accidental repeated measurements being merged as independent data.
    with destination.open("x") as handle:
        for case in cases:
            baseline = condition if condition in ("A", "B", "C") else "C"
            ontology = ontology_for(case["ontology_version"], root)
            messages, prompt = render_prompt(tokenizer, case, baseline, ontology)
            if vector_payload:
                expected_hash = vector_payload["ontology_sha256"][case["ontology_version"]]
                actual_hash = sha256_file(Path(root) / "experiment" / f"ontology-{case['ontology_version']}.md")
                if actual_hash != expected_hash:
                    raise ValueError("Ontology text changed after vector collection")
            inputs = encode(tokenizer, prompt, model, config)
            for seed in config.get("seeds", [11]):
                vector, trace_context, applied_scale, direction = None, nullcontext([]), None, None
                if condition in ("current", "stale", "random"):
                    vector_version = "v1" if condition == "stale" else case["ontology_version"]
                    vector = vector_payload["vectors"][f"{vector_version}:{layer}"]
                    # Stale/current/random interventions have equal added L2 norm on v2.
                    applied_scale = vector_payload["vectors"][f"{case['ontology_version']}:{layer}"]["activation_scale"]
                    direction = vector["direction"]
                    if condition == "random":
                        direction = random_direction(len(direction), config.get("random_vector_seed", 314159) + layer)
                    trace_context = add_direction(model, layer, direction, alpha, applied_scale)
                started = time.monotonic()
                with trace_context as trace:
                    output_ids, stopped = generate_tokens(model, inputs, config, seed)
                text = tokenizer.decode(output_ids, skip_special_tokens=True)
                evaluation = evaluate_response(case, text)
                evaluation["joint_success"] = bool(evaluation["ontology_adherence"] and evaluation["status_correct"])
                evaluation["operational_success"] = bool(evaluation["joint_success"] and (
                    evaluation["task_success"] if case["expected_status"] == "feasible" else True))
                record = {"id": case["id"], "family_id": case["family_id"], "split": split,
                          "ontology_version": case["ontology_version"], "condition": label,
                          "slice": case.get("slice"), "style": case.get("style"), "pair_id": case.get("pair_id"),
                          "boundary_type": case.get("boundary_type"),
                          "prompt_baseline": baseline, "seed": seed, "layer": layer, "alpha": alpha,
                          "vector_version": vector["ontology_version"] if vector else None,
                          "vector_scale": applied_scale,
                          "vector_source_scale": vector["activation_scale"] if vector else None,
                          "direction_sha256": hash_value(direction) if direction is not None else None,
                          "random_vector_seed": config.get("random_vector_seed", 314159) if condition == "random" else None,
                          "messages": messages, "context": prompt,
                          "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                          "input_ids": inputs["input_ids"][0].cpu().tolist(), "output_ids": output_ids,
                          "output": text, "stop_reason": stopped, "hook_trace": trace,
                          "evaluation": evaluation, "expected_status": case["expected_status"],
                          "expected_concept_status": case["expected_concept_status"],
                          "requested_concept": case["requested_concept"],
                          "elapsed_seconds": time.monotonic() - started,
                          "utc_time": datetime.now(timezone.utc).isoformat(), "provenance": run_provenance}
                handle.write(json.dumps(record, sort_keys=True) + "\n")
                handle.flush()
    return {"output_file": str(destination), "cases": len(cases), "condition": label}
