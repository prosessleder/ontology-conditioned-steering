# Hypotheses and permitted conclusions

Release status: prospective protocol, 2026-10-09. This document is a versioned analysis plan, not a claim of external preregistration. Freeze a commit and the selected configuration before generating test outputs.

## H1: Incremental operational consistency

Compared with the identical structured ontology prompt C, C plus a version-matched activation direction improves family-macro operational success on held-out scenario families. A point estimate alone is insufficient: report a paired family-cluster bootstrap 95% interval for the difference, full per-family results, and failures. Count malformed responses as failures. Also report executable feasible-task success and illegal/undefined action incidence; status accuracy alone is not ontology adherence.

Evidence favoring H1 requires a positive primary difference with its interval excluding zero, alongside the utility safeguards below. The small number of independent scenario families limits confidence; a nominal interval is not a confirmatory population-wide inference.

## H2: Preservation of legitimate reasoning

Ordinary feasible-task success and unknown-concept recognition should each decline by no more than 5 percentage points relative to C. These are proposed practical margins, not established acceptable losses. Dev selection uses point-estimate safeguards; final inference must report paired intervals for the losses. A test estimate inside a margin does not establish noninferiority if its uncertainty crosses the margin. V2 temporal feasible-task success is a separate outcome so rejecting temporal magic cannot masquerade as improved compliance.

## H3: Version sensitivity

On the same V2 cases, compare the V2 direction with the stale V1 direction while holding the V2 prompt, model, layer, and intervention magnitude fixed. Version-matched vectors should outperform stale vectors on newly permitted local rewind while retaining V2's restrictions. Also compare each against unsteered C. A V2 vector beating a stale vector but failing to beat C only establishes recovery from the stale intervention's damage.

Report the implemented V2 current/stale comparison and C baseline. A full V1/V2 context-by-vector cross matrix is a follow-up because the starter runner only exposes stale V1-on-V2, not V2-on-V1. The temporal held-out stratum has one family; describe its rates without treating a degenerate family bootstrap as generalization evidence. Test legality-boundary edits separately from paraphrases and familiar temporal vocabulary. This design tests selecting separately learned version-specific vectors; it does not implement automatic vector updating or a universal ontology compiler.

## H4: Representation specificity

The learned direction should exceed norm-matched random controls on the same prompt and task. Three fixed random seeds provide a diagnostic, not a complete distribution of all random directions. A useful probe, if fitted, is only evidence of linear decodability; actual generation interventions supply the behavioral causal test. Lexically matched and role-reversed contrast pairs are required before attributing gains to compatibility rather than syntax or refusal.

## H5: Robustness and generalization

Improvements should persist on held-out rule compositions, controlled paraphrases, distracting lore, and temporal boundary cases. The initial code provides structural family holdouts, matched ontology versions, and three fixed wording styles (direct, paraphrase, distractor). Broader independently authored lexical suites are follow-ups; no robustness effect has been measured.

## Null and negative interpretations

- C already succeeds: the experiment has a ceiling and cannot establish added value from steering.
- No direction generalizes: the measured representation/pooling/layer may be inadequate; this does not disprove all nonlinear interventions.
- Status improves but executable planning fails: improved surface labeling, not demonstrated reasoning improvement.
- Ordinary or newly permitted tasks fail: over-suppression or a utility tradeoff.
- Random controls match the learned vector: nonspecific perturbation or unstable estimation.
- V2 and stale vectors behave alike: insufficient version specificity at the tested intervention sites.
- Effects appear only after tuning on test cases: invalid confirmatory evidence; disclose as exploratory and construct a new holdout.

The paper does not claim eradication of internal concepts, guaranteed containment, general factual correctness, or a new activation-steering algorithm.
