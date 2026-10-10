# Executable implementation plan

Status: the symbolic evaluator and implementation checks run locally. Pretrained-model steering efficacy, model throughput, and the complete experiment remain unmeasured. Tiny randomly initialized Qwen tests validate the intervention plumbing; they are not evidence of ontology adherence.

## Framework, model, and verified intervention site

The pilot uses **Qwen/Qwen2.5-1.5B-Instruct**, pinned to commit `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`, with PyTorch `2.9.0`, Transformers `4.57.1`, and eager attention. The official model card reports 1.54 billion parameters, 28 decoder layers, and a 32,768-token context window. At float16 the parameters alone require approximately 3.08 GB; this arithmetic excludes caches, activations, and framework overhead. A 48 GB Apple M4 Max is a plausible target, but total memory and speed need a pretrained-model smoke run. [Official model card](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct), [immutable model snapshot](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct/tree/989aa7980e4cf806f80c7fef2b1adb7bc71aa306).

PyTorch supplies the `mps` device and checks for its availability. The runner explicitly moves the model and tensors to the chosen device and errors if MPS is unavailable. CPU runs require an explicit configuration change, which is logged. PyTorch forward hooks can replace module outputs. These are documented capabilities, not assumptions based on ordinary inference support. [MPS documentation](https://docs.pytorch.org/docs/2.9/notes/mps.html), [forward-hook documentation](https://docs.pytorch.org/docs/2.9/generated/torch.nn.Module.html#torch.nn.Module.register_forward_hook).

In the pinned Transformers source, `Qwen2DecoderLayer.forward` returns the hidden tensor after both residual additions; `Qwen2Model` passes that tensor into the next layer and applies its final RMSNorm after all layers. The hook therefore reads and changes the decoder block's residual output, before the final RMSNorm. It does not hook the already normalized `hidden_states[-1]` output. [Pinned Qwen2 implementation](https://github.com/huggingface/transformers/blob/v4.57.1/src/transformers/models/qwen2/modeling_qwen2.py).

MLX is a possible future implementation. It is not used here because this pilot already has documented and tested PyTorch module output replacement. No claim about arbitrary MLX hooks is required.

## Exact estimator and intervention

For each version and zero-based decoder output layer `l`, teacher-force matched compatible and incompatible JSON responses to a common C prompt. Capture the final **response** token, with no appended end-of-turn marker or compatibility label. For `n` train pairs:

`d_l = mean_i(h_l(compatible_i) - h_l(incompatible_i))`

`v_l = d_l / ||d_l||_2`

`s_l = mean_i((||h_l(compatible_i)||_2 + ||h_l(incompatible_i)||_2) / 2)`

Apply `h_l[last] := h_l[last] + alpha * s_l * v_l`. During the initial prompt forward only its final position is changed; with KV caching, each subsequent forward contains one generated token, which is changed. Earlier prompt positions remain untouched. The hook returns a replacement tensor and is removed in a `finally` block. The magnitude of the added vector is `|alpha| * s_l`.

The predefined grid is layers `[6, 13, 20]` and alpha `[0, 0.025, 0.05, 0.1, 0.2]`. Layers approximate 25%, 50%, and 75% of the 28-layer stack. Alpha zero is an eligible outcome, including if nonzero interventions do not improve dev performance.

The primary `pairs-common.jsonl` pool contains only matched ordinary train families with equal counts and identical response endpoints across versions. Only their ontology context changes. With the default dataset there are 24 pairs per version, 48 total. `pairs.jsonl` includes 60 pairs, adding a V2 temporal family, and is an **exploratory estimator sensitivity** because version pair count and composition then differ. Never substitute the extended pool after inspecting test outcomes. Pair construction is intentionally simple; operation vocabulary, action position, tokenization, and final JSON syntax remain possible nuisance features. A successful intervention would not identify a uniquely semantic or internal incompatibility representation. The response endpoint used for extraction also differs from the prompt endpoint at initial intervention, which is a transfer assumption to test.

## Conditions and controls

All conditions share the output JSON instructions. A omits the world rules, B appends the world description, and C wraps the same description in a structured instruction to check class, energy, preconditions, and membership. C and every steered condition use byte-identical prompts for a given case, verified by their prompt SHA-256. No output grammar, refusal filter, logit bias, or answer repair is applied.

Current uses the vector matching the task's ontology version. Stale is evaluated only on V2, using the V1 direction. Stale uses **V2's train activation scale**, so its addition has the same L2 norm as the current V2 intervention. Random uses a normalized Gaussian direction with the current version's activation scale. Random direction draws are predeclared as `314159`, `271828`, and `161803`, with the layer index added to each seed. Each receives a distinct condition label, such as `random:r314159:l13:a0.05`. Report all three controls; do not select the most favorable draw. The V1 stale and V2 current direction cosine can be descriptive, but is not itself a behavioral adaptation result.

The primary decode is greedy with seed 11 recorded. Secondary stochastic checks use CPU categorical sampling at temperature 0.7 and seeds 11, 29, and 47. CPU sampling makes the random generator explicit; it does not guarantee bitwise identical MPS logits across macOS or framework releases. Analyze greedy and sampled outputs separately.

## Installation and local verification

Run from the repository root with Python 3.12 on macOS arm64. `requirements.lock` pins the complete dependency environment with package hashes; it was generated and installed on the target machine.

```sh
uv venv --python python3.12 .venv
uv pip install --python .venv/bin/python --require-hashes -r requirements.lock
uv pip install --python .venv/bin/python --no-deps -e .
.venv/bin/python -m pytest -q
.venv/bin/ontology-steering dataset --out data --seed 1729 --per-family 12
```

The real tiny Qwen tests run decoder hooks and cached generation on CPU and, when available, MPS. They verify that alpha zero preserves greedy output, that the trace has one prefill forward followed by single-token forwards, that an added residual changes downstream logits while earlier prompt positions stay identical, and that hook cleanup occurs on error. An integration test freezes a complete synthetic dev grid, rejects changed test alpha, runs a tiny model through the recorded test loop, grades invalid outputs as failures, and prevents overwriting run files. These checks do not load the pretrained 1.5B weights.

## Train, dev, freeze, test

First run a **dev-only** smoke evaluation to measure end-to-end time and inspect truncation/formatting. Do not inspect test model answers during development. A smoke run still downloads the model weights the first time; the `--limit` flag only limits the number of cases.

```sh
.venv/bin/ontology-steering run --condition C --split dev --limit 4 --out runs/smoke-C.jsonl
.venv/bin/ontology-steering collect --pairs data/pairs-common.jsonl --out runs/vectors.json
.venv/bin/ontology-steering run --condition C --split dev --out runs/dev-C.jsonl
```

Run the complete predefined grid. Do not include the smoke file in selection:

```sh
for layer in 6 13 20; do
  for alpha in 0 0.025 0.05 0.1 0.2; do
    .venv/bin/ontology-steering run --condition current --split dev \
      --vectors runs/vectors.json --layer "$layer" --alpha "$alpha" \
      --out "runs/dev-current-l${layer}-a${alpha}.jsonl"
  done
done
.venv/bin/ontology-steering freeze --vectors runs/vectors.json \
  --dev runs/dev-C.jsonl runs/dev-current-*.jsonl \
  --secondary-config configs/sampling.json configs/random-271828.json configs/random-161803.json \
  --out runs/selection.json
```

Selection maximizes the equal-family-weighted paired dev gain in `operational_success`. This requires correct status, ontology adherence, and, on feasible cases, an executable goal-reaching plan. In each ontology version, ordinary feasible task success and unknown recognition may decline by at most five percentage points relative to C. These are **dev point-estimate screens**, not proof of statistical noninferiority. A tie chooses the smallest absolute alpha, then earliest layer. Freeze requires every predefined candidate and every dev case/seed; limited pilot grids cannot be frozen.

The frozen manifest records the selected layer and alpha; all candidates and their constraint effects; config, vectors, train/dev/test dataset, ontology, dev-output, and implementation hashes; all Markdown experiment specifications and `research/hypotheses.md`; and predeclared secondary configuration hashes. Test commands reject changes to the frozen config, layer, alpha, test dataset, ontology, vector artifact, Python source, or experimental design. The manuscript remains editable so measured results can be reported. This is an audit guard, not a cryptographic guarantee that an operator has never inspected test data.

Read the selected values from `runs/selection.json` into shell variables, then run the primary conditions:

```sh
layer=$(.venv/bin/python -c 'import json; print(json.load(open("runs/selection.json"))["selected"]["layer"])')
alpha=$(.venv/bin/python -c 'import json; print(json.load(open("runs/selection.json"))["selected"]["alpha"])')
for baseline in A B C; do
  .venv/bin/ontology-steering run --condition "$baseline" --split test \
    --selection runs/selection.json --out "runs/test-${baseline}.jsonl"
done
for condition in current stale random; do
  .venv/bin/ontology-steering run --condition "$condition" --split test \
    --vectors runs/vectors.json --layer "$layer" --alpha "$alpha" \
    --selection runs/selection.json --out "runs/test-${condition}.jsonl"
done
for draw in 271828 161803; do
  .venv/bin/ontology-steering run --config "configs/random-${draw}.json" \
    --condition random --split test --vectors runs/vectors.json \
    --layer "$layer" --alpha "$alpha" --selection runs/selection.json \
    --out "runs/test-random-${draw}.jsonl"
done
```

For secondary sampling, use `--config configs/sampling.json` with separate output filenames for C, current, and stale; keep the same frozen layer and alpha. New settings or an extended estimator require a separately declared experiment, rather than modifying this frozen run after test inspection.

## Analysis and reproducibility records

Every JSONL result contains model ID and immutable revision; SHA-256 hashes of cached model/tokenizer files and Python source; installed library versions, OS, device, dtype, attention mode, and git commit; dataset/vector/selection hashes; seed, layer, alpha, vector version and source/applied scale; prompt/messages and token IDs; raw decoded output and generated IDs; stopping reason; hook token trace; runtime; and evaluator outcomes. Vector artifacts additionally contain pair IDs, train family IDs, complete endpoint contexts/token IDs, and estimator provenance. No secrets or environment file contents are recorded.

```sh
.venv/bin/ontology-steering analyze --runs runs/test-C.jsonl runs/test-current.jsonl \
  --treatment "current:l${layer}:a${alpha}" --metric operational_success \
  --resamples 10000 --out runs/primary-analysis.json
.venv/bin/ontology-steering analyze --runs runs/test-C.jsonl runs/test-current.jsonl \
  --treatment "current:l${layer}:a${alpha}" --metric task_success \
  --stratum ordinary-feasible --ontology-version v2 --out runs/task-v2-analysis.json
.venv/bin/ontology-steering analyze --runs runs/test-C.jsonl runs/test-stale.jsonl \
  --treatment "stale:l${layer}:a${alpha}" --metric task_success \
  --stratum temporal-feasible --ontology-version v2 --out runs/stale-temporal-analysis.json
```

Pair outcomes by scenario ID, ontology version, and seed. Average within structural family and give each family equal weight. Bootstrap whole families 10,000 times; both ontology-version twins and repeated sampling seeds stay inside their family cluster. Report separate version and temporal/ordinary strata. Missing or duplicate pairs, changed C prompts, or unmatched model/inference provenance cause analysis errors. Metrics undefined outside a stratum, such as feasible-only task success, require explicit stratum filtering. For malformed answers, interference and over-suppression are unavailable; report schema coverage separately rather than silently treating missing values as successes.

There are only **three held-out test structural families** in this pilot, and only one temporal family. Repeating their numeric variants does not create new independent families. Bootstrap intervals are consequently exploratory and may be misleadingly narrow. With fewer than two families, the analysis returns `ci95: null`, `interval_informative: false`, and an explicit warning, rather than a degenerate interval. Every analysis also provides family-level descriptive rates and effects. Before generalization or confirmatory significance claims, preregister substantially more independent structures and a power/precision analysis. The pilot's useful evidence is its paired effect sizes, failure cases, and version-control behavior.

## Budget and stopping rules

With `per-family=12`, each split has 240 cases. Dev C plus 15 candidates requires 3,840 generations. Primary A/B/C/current plus three random draws and V2-only stale requires 1,800 generations. Secondary sampled C/current/stale requires 1,800 generations. At a 384-token cap the total upper bound is approximately 2.86 million generated tokens, excluding extraction/prefill. **No speed estimate has been measured.** Project wall time from the dev smoke's actual per-case durations before committing to the full weekend run.

If the budget is too large, choose a smaller `per-family` value or a smaller predeclared grid before vector construction and dev selection, regenerate the entire dataset, and publish that choice and its hashes. Do not reduce cases or change conditions in response to test outcomes. Record EOS versus max-token stops and all invalid JSON responses; the evaluator treats failures as failures. An alpha-zero selection or lack of stable direction is an informative null. A positive outcome remains evidence about this model, estimator, dataset, and intervention scope, not guaranteed containment or suppression of internal concepts.
