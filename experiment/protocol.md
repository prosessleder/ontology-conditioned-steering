# Prospective experimental protocol

## Objective and unit of analysis

Measure the incremental effect of residual activation addition on operational consistency with an explicit, changing causal ontology. The model is a participant solving fictional tasks. The simulator is the reference semantics. This is an independent study of model behavior; Bounded Agency, organizational governance, and access-control architecture are outside its experimental scope.

Case IDs are paired across conditions. Related instances, numerical variants, and V1/V2 versions stay in a single split. Scenario families are held out structurally. The primary inferential unit is the family, not an individual generated token or repeated paraphrase. The default pilot has 720 cases (240 per split), 48 primary train-only contrast pairs (24 per version), plus a 60-pair exploratory extended pool, and nine structural families (three per split). Only three independent test clusters make all first-run intervals exploratory; expand independently designed families or replicate before confirmatory claims.

## Intervention, fixed before test

Use Qwen/Qwen2.5-1.5B-Instruct at the immutable revision recorded in configs/pilot.json. The primary runtime is PyTorch/Transformers with MPS on Apple Silicon, batch size one, unquantized weights. CPU provides a fallback. MLX is a plausible later performance port, but ordinary MLX inference is not evidence that this particular hook implementation works there.

For training pair i and decoder block l, collect the final response-token block output h(i,l,+) from a compatible structured response and h(i,l,-) from its incompatible matched response, using the same world, question, and ontology context. Compute:

    d_l = mean_i [h(i,l,+) - h(i,l,-)]
    v_l = d_l / ||d_l||_2
    s_l = mean_{i,sign} ||h(i,l,sign)||_2
    h'_l = h_l + alpha * s_l * v_l

Reject zero/nonfinite directions. A vector's sign is defined as compatible minus incompatible. The coefficient is nonnegative in the primary grid; negative steering is exploratory. The mean training norm makes alpha a fractional perturbation scale, not a literal percent change in output behavior.

Apply the intervention to the last prompt position in prefill and to the single current token in each cached decode forward. No update is applied to other prompt positions. Teacher-forced collection and generation use different token locations; this transfer assumption is a limitation tested by actual outputs, not proven by the extraction step. All layers use zero-based block-output indices, not embedding indices.

This is addition of a learned direction. It is not orthogonal projection, concept erasure, sparse-feature suppression, weight editing, logit modification, or final-output filtering. No learned input gate is implemented: the supplied ontology version explicitly selects a stored direction.

## Conditions

| ID | Context | Activation treatment | Purpose |
| --- | --- | --- | --- |
| A | No ontology, same state/task/schema | None | Prior-world behavior; descriptive only |
| B | Plain full ontology | None | Ordinary prompt grounding |
| C | Structured full ontology and response contract | None | Strong prompt comparator |
| C+V | Exactly C | Current-version direction | Primary incremental steering comparison |
| C+old | Exactly C in V2 | Stale V1 direction | Newly valid concept suppression |
| C+random | Exactly C | Norm-matched random direction | Nonspecific perturbation control |
| C+zero | Exactly C | alpha=0 | Dev-grid and hook/no-op implementation control |

Optional D retrieves rule clauses rather than replacing C in the primary comparison. If implemented, relevance retrieval must depend only on the presented task/state; never use gold labels or simulator feasibility as a retrieval oracle. A C+V effect relative only to A or B is insufficient to isolate steering.

## Training, development, and freezing

1. Generate data deterministically; validate disjoint family assignments, answer schema, paired-version membership, and simulator gold plans. Record dataset hashes and generator commit.
2. Construct contrastive pairs from train only. Use pairs-common.jsonl for the primary experiment: 24 ordinary pairs per version, with identical response and mutation text across version twins. The 60-pair extended pool is exploratory because V2 alone includes temporal feasible examples; it changes sample size and composition. Record pair hashes, response length distributions, lexical differences, and invalid-action types. Derive V1 and V2 vectors independently.
3. Evaluate dev candidates at block outputs 6, 13, 20 of the 28-block model and alpha in {0, .025, .05, .1, .2}. The primary selection criterion is family-macro operational success subject to at most 5 percentage-point loss in ordinary feasible-task success and unknown recognition versus C on dev. Prefer the smaller coefficient in ties. Keep alpha=0 if no admissible positive candidate improves the objective.
4. Save a frozen selection record with model/dataset/vector/config hashes, all candidate scores, rejection reasons, and selected parameters. Lock it before generating test outputs. Record any later deviation as exploratory.
5. Run greedy held-out test evaluation once for the frozen comparison. Run stochastic secondary trials with seeds 11, 29, 47 only if time permits, retaining the same cases and frozen steering choice. Replicates do not create new independent families.
6. For H3, both current and stale direction comparisons must use the current version's selected layer and a common alpha/scale. Report a supplementary raw training-scale comparison if used; magnitude differences must not be attributed solely to version information.

The starter CLI supports generation, vector fitting, dev evaluation, selection freezing, inference, and paired analysis. Commands and limitations are in README.md and implementation-plan.md. The code does not silently execute a complete study merely because this protocol exists.

## Outcomes and uncertainty

Primary outcome: operational success, requiring correct status and ontology adherence, plus executable goal completion on feasible cases, macro-averaged within each family and then across families. Status accuracy is a separate diagnostic. Report case-micro accuracy alongside it. Secondary outcomes include concept status accuracy, parsing success, feasible executable-goal success, illegal and undefined action rates, V2 temporal success, and false rejection of permitted tasks. The conjunction of valid classification and valid goal-reaching execution is the most direct operational task outcome.

Use paired bootstrap resampling of whole families, preserving all versions/conditions/instances in each resample, with 10,000 replicates and a recorded bootstrap seed. Report denominators and intervals. The temporal feasible stratum has one test family: its family bootstrap interval is degenerate and carries no temporal generalization evidence. Report descriptive within-family rates. With few families, intervals are unstable; show every family effect and label the study a pilot. Sampling seeds and numeric variations are nested within families and must not be treated as independent replication. Confirmatory language is withheld until an enlarged family suite or independent replication supports it.

The primary contrast is C+V minus C. Secondary hypotheses and robustness strata are exploratory unless their multiplicity plan is frozen separately. Do not select the best of many test analyses and describe it as the primary result. A nominal bootstrap interval does not compensate for adaptive dataset design or selection.

## Adversarial validity checks

- A word-ban baseline should fail on permitted V2 local rewind and unknown temporal requests, demonstrating why temporal vocabulary alone is not the task.
- Validate temporal age/eligibility, class, resource, one-use, and irreversible-energy boundaries. Include valid temporal plans and temporal near-misses with the same words.
- Compare refusal/empty plans against multi-step goal completion so indiscriminate rejection cannot score as success on feasible tasks.
- Include non-temporal feasible tasks to reveal generic planning degradation.
- Report seen-versus-unseen undefined names separately: echo_matter is also a training negative. Review contrast pairs for surface leakage; role-reverse label names or equalize fields in an exploratory control.
- Compare norm-matched random directions and a zero coefficient; verify only the intended block/positions are modified.
- Audit the evaluator with malformed JSON, extra actions, unknown operations, false infeasibility, and resource violations.
- Keep extraction examples and all answer-bearing fields out of inference prompts. Task state and requested concept are inputs; gold labels and plans are evaluator-only.

## Feasibility and stop rules

The inspected host has 48 GiB unified memory. This is a verified hardware fact, not a measured throughput claim. A 1.5B FP16 parameter tensor occupies roughly 3 GB before runtime/context/cache overhead. Run a 12-case technical smoke first, log throughput and peak memory, then estimate the full wall-clock budget from measured tokens per second. Batch one, bounded output length, and a modest grid are intended to fit a weekend; no runtime guarantee is claimed.

Stop and diagnose on nonfinite activations, unsupported hook shape, dataset leakage, nondeterministic no-op behavior beyond documented numeric differences, or unavailable MPS. Reduce the dev sample or grid before looking at test outcomes and record the change. Do not broaden test tuning after observing failure.

## Reporting and release

Keep raw model records and analysis reports separate from software validation. The current release contains no model-performance results. Archive a source bundle, environment/model revisions, dataset hashes, selected configuration, measured run files, and analysis commands when experiments are complete. Upload this release as a research-protocol preprint if depositing before experiments; a later measured paper must explicitly identify its new version.
