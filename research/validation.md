# Release validation record

Date: 2026-10-09 (America/Los_Angeles). Release: 0.1.0. These are software and artifact checks, not experimental evidence for steering efficacy.

## Executed checks

The final local command `.venv/bin/python -m pytest -q` completed with **31 passed in 6.48 seconds**. Runtime: Python 3.12.13, PyTorch 2.9.0, Transformers 4.57.1 on the M4 Max host with MPS available.

Tests cover symbolic membership, legal transformations, finite energy, conservation, class/precondition violations, irreversible energy under rewind, temporal history/reuse, strict JSON parsing and execution, false refusal, split integrity, version pairing, matched contrast text, all four contrast corruptions, temporal infeasibility certificates, and independent bounded-search checks of scenario families. They also exercise real randomly initialized tiny Qwen models: residual output replacement, intended token sites, zero-coefficient equivalence, downstream logit change, hook cleanup, cached autoregressive generation on CPU and MPS (including float16), frozen dev selection, test-parameter rejection, complete pairing, analysis, and exclusive output-file creation.

The final deterministic generator produced **720 cases**, 240 per split, **48 primary matched contrasts**, and 60 exploratory contrasts. Core labels are balanced: 144 cases per feasible/infeasible/prohibited/unknown status across both versions. Temporal cases total 144: 72 V1 unknown and 36 each V2 feasible/infeasible. Four V2 infeasibility types are present: energy, mass, living target, and missing keeper. The release manifest records exact file and generator hashes; regenerate with seed 1729 and per-family 12.

The manuscript PDF was generated with ReportLab, rendered through Poppler, and visually checked for page flow, legibility, tables, references, and glyphs. The revised PDF contains eight pages. An independent internal manuscript review checked scientific structure and agreement with the implemented protocol. The revision changes manuscript presentation and supporting publication documentation; experimental implementation and test results are unchanged. The source archive and manuscript checksums are in publication/SHA256SUMS. Archive inspection verifies exclusion of credentials, virtual environments, model weights, generated model runs, and temporary images.

Independent internal review is documented in adversarial-review.md. Primary-source literature search is documented in search-log.md. That review is not external peer review or proof of novelty.

## Not executed or established

The pretrained Qwen2.5-1.5B-Instruct checkpoint was **not downloaded or evaluated**. No adherence, planning, version adaptation, utility retention, model speed, or peak-memory measurement is reported. No full dev selection or real test manifest has been frozen. Test fixtures contain synthetic outputs solely to exercise software behavior; they are not benchmark measurements.

The benchmark has three held-out structural families and one temporal family. Single-family analyses return no inferential interval. More numeric instances and repeated seeds do not resolve the independence limit. Broader semantic controls and competitive baselines remain documented follow-ups.

The repository was created as a private draft in the verified `prosessleder` organization and subsequently made public at the author's request. The manuscript license was set to CC BY 4.0 at the author's request. No Zenodo upload or DOI reservation was performed. Author metadata and deposition remain pending author review.
