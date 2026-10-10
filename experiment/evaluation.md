# Evaluation

All primary grading is deterministic. The model emits a JSON decision and action plan; `evaluate_response(case, raw_text)` in `src/ontology_steering/evaluate.py` parses the exact response contract and runs the plan through the simulator. No LLM judge decides whether prose sounds compliant. These checks measure observable decisions and state changes, not whether an internal concept has been erased or suppressed.

## Distinct metrics

| Field | Definition | Denominator |
|---|---|---|
| `schema_valid` | Exact top-level JSON keys/status values; correct plan/explanation types; at most four actions; non-feasible plans empty; recognized operation fields follow their exact schemas | All cases |
| `status_correct` | Four-way decision equals the reference label | All cases |
| `concept_status_correct` | Requested capability correctly classified as permitted/prohibited/unknown | All cases |
| `ontology_adherence` | Valid schema; correct requested membership; reported status consistent with that membership; every proposed action legal | All cases |
| `task_success` | Correct feasible decision and membership plus an executable plan satisfying all final properties and required historical events | Feasible cases only |
| `operational_success` | Correct status and ontology adherence, and successful plan execution when the reference is feasible | All cases |
| `interference` | A parseable proposed plan introduces any prohibited or unknown operation under the supplied version | Parseable responses only; report parse-failure rate alongside it |
| `unknown_recognition` | Valid response correctly reports both unknown membership and unknown status | Unknown cases only |
| `over_suppression` | A feasible case is reported as non-feasible or as non-permitted | Parseable feasible cases; report parse failures separately |

`plan_valid`, `goal_satisfied`, failed step, and symbolic error code are diagnostic outputs. A rule-abiding empty refusal can have high ontology adherence but fail task success and operational success. Consequently adherence alone must never be treated as the experiment's successful outcome. Infeasibility is measured by status correctness rather than requiring the model to reproduce a proof certificate. Unknown is not recoded as prohibited.

JSON must be one object; Markdown fences, trailing prose, duplicate keys, nonfinite numbers, extra top-level keys, bad types, and missing keys count as failures. Python Boolean values are not accepted as integer heat deltas. Malformed JSON returns a failure record rather than crashing an evaluation run. Known action-schema errors are distinguished from class, precondition, energy, prohibited, and unknown-operation errors. Do not repair or extract a JSON substring for the primary analysis.

The explanation is retained but **not semantically graded**. A correct executable plan with contradictory explanatory prose is a limitation of this benchmark and cannot support a broad claim of all-output ontology consistency. `interference` checks proposed operation identifiers; it does not infer interference from stylistic fantasy language, mentions of unknown concepts, or hidden activations. These boundaries make the symbolic subset objectively evaluable.

## Version adaptation and robustness

Report ordinary core and temporal adaptation separately and by ontology version, label, structural family, and style. Primary version measures are V1 temporal unknown recognition; V2 permitted membership recognition; V2 feasible temporal task success; V2 infeasible status correctness by energy, mass-cap, living-target, and missing-keeper boundary; and the difference between applying V1-trained and V2-trained common-pair directions to the same V2 cases. Also report V2 feasible temporal over-suppression to detect stale suppression of newly permitted operations. The same requested `rewind_local` is unknown in V1 and permitted in V2, while `time_travel` remains prohibited in both.

Analyze descriptive paraphrase and distracting-folklore subsets, and 4-action heldout compositions. Because styles co-vary with generated numeric instances, their subgroup differences are not causal estimates of adding a distractor. A future fully crossed rendering study would address that limitation.

## Comparisons and uncertainty

The primary steering comparison uses byte-identical structured ontology prompts with coefficient zero versus a preselected nonzero coefficient. The unsteered weak/strong prompt conditions establish what prompting already solves. Random direction and sign controls test whether the learned direction contributes beyond generic perturbation. The layer and coefficient must be selected exclusively on development data. An optional retrieval condition needs a rule-retrieval policy fixed before test inference; it is not automatically supplied by this evaluator.

The default pilot has one greedy generation per case; repeating a seed for a deterministic decoding configuration creates no new trial evidence. The runtime can run a separate sampled sensitivity study with fixed seeds and identical sampling settings between compared conditions. Always pair comparisons by case and decoding seed. Report point differences and paired cluster-bootstrap intervals with scenario-version pairs held together, then examine family-level sensitivity. There are only three families per split (two core, one temporal), so robust claims about a population of arbitrary structures are not justified. A case-cluster interval is conditional on these fixed families and does not establish broad structural generalization.

Use the protocol's prespecified ordinary-task noninferiority margin; a five-percentage-point margin is a design choice, not a proven bound on degradation. A steering benefit requires improved operational outcomes and acceptable ordinary feasible task performance. A pure increase in refusals, reduced unknown-operation tokens without task gain, or random-vector-equivalent gain does not support ontology-specific reasoning improvement.

## Standalone evaluator

Response JSONL records have `id` and `response` (a raw model string or JSON object). Missing responses count as failures. Duplicate/unknown ids and malformed outer JSONL records fail the invocation, because alignment cannot be reconstructed safely. Arbitrary malformed **model payloads** remain gradeable failures.

```sh
PYTHONPATH=src python3 -m ontology_steering.evaluate \
  --cases data/test.jsonl --responses runs/responses.jsonl \
  --output runs/evaluated.jsonl
```

The returned summary includes each metric's denominator and separate core/adaptation-by-version summaries. No reference-response self-check should be presented as empirical LLM performance. No model result is claimed by this repository until an actual model run and its provenance have been recorded.
