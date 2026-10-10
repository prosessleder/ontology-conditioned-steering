# Controlling Incompatible Magic

**Ontology-Conditioned Activation Steering in a Fantasy Landscape**

A research-protocol preprint and reproducible pilot for one question: can residual activation steering improve a small language model's reasoning within a formal world, and remain useful when that world changes?

**Status:** research-protocol preprint; not peer reviewed. Model-performance experiments are pending. The code, simulator, and hook tests are executable. The protocol studies controlled ontology-version transitions, explicit unknown concepts, and over-suppression.

## Manuscript and reproducibility package

- [LaTeX manuscript source](paper.tex) and [readable manuscript](paper.md)
- [Typeset manuscript PDF](output/pdf/controlling-incompatible-magic.pdf)
- [Source archive](publication/ontology-conditioned-steering-v0.1.0-source.zip) and [checksums](publication/SHA256SUMS)
- [Bibliography](references.bib)
- [Hypotheses](research/hypotheses.md) and [experimental protocol](experiment/protocol.md)

Author: Tim O'Brien, [ORCID 0009-0001-2589-347X](https://orcid.org/0009-0001-2589-347X), with no affiliation. The manuscript is licensed under CC BY 4.0. Deposition metadata is provided in [.zenodo.json](.zenodo.json); no Zenodo record or DOI has been created.

## Experimental world

The Seven Laws of Magic define finite energy, class-bound operations, material conservation, bounded heat and local transformation. [V1](experiment/ontology-v1.md) leaves local rewind undefined. [V2](experiment/ontology-v2.md) introduces a tightly bounded anchor-and-rewind operation. General time travel remains explicitly prohibited in both.

A symbolic evaluator checks structured outputs and executes plans. Correct classification alone cannot count as operational success on a feasible task; the generated legal plan must achieve the goal. Undefined concepts are not silently treated as prohibitions.

The default pilot has 720 cases, 240 per split, and nine structural families. Only three test families make uncertainty intervals exploratory. A larger independently authored suite is needed before confirmatory generalization claims. Primary contrastive extraction uses 48 ordinary train pairs with identical response text across ontology versions; the extended 60-pair pool is exploratory.

## Run the software checks

Python 3.11-3.13 is supported. The dependency lock was resolved with Python 3.12 on macOS ARM64. Model dependencies are optional for generating/evaluating the benchmark.

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip install -e . --no-deps
.venv/bin/python -m pytest -q
```

For a minimal installation without model weights or PyTorch:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -e .
PYTHONPATH=src .venv/bin/python -m ontology_steering.dataset --output data/generated
```

See [dataset design](experiment/dataset-design.md) and [evaluation definitions](experiment/evaluation.md). Generating data uses only the Python standard library. The command emits train/dev/test cases, pairs-common.jsonl, the exploratory pairs.jsonl, and a manifest.

## Run the prospective model study

The initial model is Qwen2.5-1.5B-Instruct at an immutable revision in [the pilot configuration](configs/pilot.json). The runtime uses PyTorch decoder-block forward hooks on Apple MPS, modifying the final prompt position and each generated-token residual. It is additive steering, not concept erasure, logit bias, or output filtering. The full target weights were not downloaded for this release's validation.

Generate the benchmark, fit train-only primary vectors, and run a small development smoke:

```bash
.venv/bin/ontology-steering dataset --out data/generated
.venv/bin/ontology-steering collect --data data/generated --pairs data/generated/pairs-common.jsonl --out vectors/common.json
.venv/bin/ontology-steering run --data data/generated --split dev --condition C --limit 12 --out runs/smoke-C.jsonl
```

The first model command downloads weights. Record throughput from the smoke before budgeting the full study. Complete development selection, test freezing, version controls, and analysis commands are in [the implementation plan](experiment/implementation-plan.md). Test inference requires a frozen development selection, matching hashes, and a complete test set. Run output files are created exclusively to prevent accidental overwrites.

For evaluator-only use, provide JSONL records of the form `{"id": "case-id", "response": "raw model text"}`:

```bash
PYTHONPATH=src .venv/bin/python -m ontology_steering.evaluate --cases data/generated/test.jsonl --responses responses.jsonl --output evaluated.jsonl
```

The primary comparison is the exact structured C prompt with versus without a current-version direction. Random, stale, and zero interventions diagnose specificity and utility loss. Prompt retrieval, grammar-constrained generation, CAST/K-CAST, and symbolic filtering are proposed additional competitors; no measurements for them are implied.

## Build the publication files

The canonical manuscript is `paper.tex`, using Elsevier's standard `elsarticle` single-column preprint class with numbered citations. The source is self-contained, including its bibliography. The class and supporting packages are supplied by TeX Live or another LaTeX distribution. Template use does not imply submission to an Elsevier journal. `paper.md` is a readable companion and should be synchronized when the manuscript changes.

Open `paper.tex` in a LaTeX editor for source editing and preview, or export the publication PDF with Python 3 and an installed `pdflatex`. The build helper runs LaTeX until references are resolved and writes the PDF to `output/pdf/controlling-incompatible-magic.pdf`.

```bash
python scripts/build_pdf.py
git add .
python scripts/build_source_archive.py
```

The source archive uses tracked files only and excludes run outputs, model weights, credentials, the PDF, and the archive itself. Rebuild it after any source change. Check publication/SHA256SUMS against the uploaded files.

Code, configuration, scripts, and tests use [MIT](LICENSE-CODE). Manuscript, benchmark data, ontology specifications, and prose documentation use [CC BY 4.0](LICENSE). Third-party papers and model weights retain their own licenses.
