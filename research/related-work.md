# Adversarial related-work audit

**Cutoff:** 9 October 2026. **Evidence status:** literature review and proposed experiment; no model results from this repository. Searches, access gaps, and source metadata are recorded in [search-log.md](search-log.md); complete citations are in [references.md](../references.md).

## Verdict before experiments

The broad idea is **not new**: contrastive activation steering, context-dependent interventions, steering away from prior-knowledge interference in formal reasoning, knowledge-graph-guided selective behavior, activation-based knowledge updates, and synthetic fictional-world reasoning all have direct predecessors. A fantasy setting supplies an evaluation environment, not an originality argument. The present difference-of-means intervention is an application of existing methods.

A defensible candidate contribution is a reproducible **evaluation protocol** linking an executable causal world specification to contrastive training examples and testing a controlled change in compatibility: local rewind moves from unknown in V1 to narrowly permitted in V2, while general time travel remains explicitly prohibited. The study measures joint task success and adherence, composition held out from vector construction, and damage caused by a stale vector. We did not locate an inspected paper matching that full combination. This is a bounded search observation, not evidence of firstness. It is possible for every component to be known while the benchmark combination remains useful. Novelty of the combination still requires independent expert review and broader citation tracing.

## Highest-risk predecessors

| Work | Existing contribution that threatens novelty | Remaining difference to investigate |
|---|---|---|
| [R06: content-effect steering](https://ojs.aaai.org/index.php/AAAI/article/view/40617) | Static and conditional interventions improve formal reasoning despite misleading semantic plausibility. | Multi-step resource-sensitive plans and an explicit version transition. |
| [R07: SELECT](https://aclanthology.org/2025.naacl-long.353/) | Structured benign concept hierarchies/compositions determine targets of conditional activation control. | Causal feasibility rather than abstention from concept categories. |
| [R32: SPIKE](https://openreview.net/pdf/69c979c667564ad900737b8c64ed13022ec74bfd.pdf) | Changed KG triples produce activation updates with locality and unseen-triple evaluation. | Rule-level capability changes with prohibited/unknown/permitted semantics. |
| [R33: mental-space routing](https://arxiv.org/abs/2607.10248) | Causal interventions select fictional, counterfactual, belief, and temporal contexts, including rule-derived conclusions. | Compliance and useful planning under an evolving action model. |
| [R30: ontology-vector proposal](https://www.ayurvedicpoint.it/images/pdf/EC_LLM_V2.pdf) | Explicitly proposes contrastive vectors between incompatible ontological frames. | An executable benchmark and a causal experiment; the cited passage is a proposal. |
| [R05: CAST](https://arxiv.org/abs/2409.05907) | Programs selective behavior from condition and behavior vectors. | No invention of conditional steering can be claimed here. |
| [R14: PASTA](https://arxiv.org/abs/2311.02262), [R09: DIRECTER](https://arxiv.org/abs/2603.06745) | Emphasize supplied instructions or new context using internal inference-time controls. | Determine whether a contrastive direction helps beyond stronger attention to ontology text. |
| [R35: KG-guided style steering](https://link.springer.com/chapter/10.1007/978-981-92-1468-6_42) | A symbolic KG shapes contrastive activation extraction and preserves factual fields. | Causal rule reasoning, without repairing output values after generation. |

These are competing explanations and baselines, not just references to cite. A gain could come from generic instruction following, answer-label preference, reduced willingness to propose actions, or task-format control rather than changed compatibility reasoning.

## CounterSteer: verified inspiration and limits

[R01](https://arxiv.org/html/2609.36570v1) is a **single-author** Mark Russinovich preprint, submitted 29 September 2026. Its per-model behavioral contrasts produce difference-of-means directions, screened and causally/capability tested. Deployment subtracts scaled directions with norm preservation at block outputs, over tool-result tokens during prefill. Reported five-model results span 8B–106B: held-out attack success 0.21–1.00 before versus 0.00–0.17 after; parameter manipulation remains partly resistant and content reasoning can incur costs. These are the author's results, not independently reproduced here. Tool-span protection neither establishes ontology reasoning nor guarantees internal concept removal.

The useful methodological lesson is to distinguish a readable correlate from a causal lever and to reject apparent success purchased through loss of useful action. This repository borrows that evaluation principle. Its final-prompt/current-token addition differs from CounterSteer's span-limited prefill rotation.

## Foundational methods and what they actually change

| Source | Mechanism and relevance |
|---|---|
| [R02: CAA](https://aclanthology.org/2024.acl-long.828/) | Averages residual-stream activation differences over behavioral pairs, then adds a scaled vector during inference. This is the direct methodological predecessor of the planned experiment. ACL uses the name Nina Rimsky; earlier arXiv metadata uses Nina Panickssery. |
| [R03: ActAdd](https://arxiv.org/abs/2308.10248) | Contrasts prompt activations and injects their difference, enabling control of output properties without weight optimization. Prompt-pair addition itself is established. The original and expanded conference versions have different titles. |
| [R04: RepE](https://arxiv.org/abs/2310.01405) | Uses population-level representations to read and control high-level phenomena. Concept-guided direction extraction is an existing top-down strategy; a human ontology does not automatically align with a causal model feature. |
| [R05: CAST](https://arxiv.org/abs/2409.05907) | Condition vectors gate behavior-vector application from activation patterns; conditions can be composed and reversed. Reconfiguration of activation-control rules and domain-specific selective behavior predate this study. |
| [R15: ITI](https://arxiv.org/abs/2306.03341) | Identifies truth-correlated directions at selected attention heads and shifts head activations. Truthfulness/helpfulness trade-offs illustrate why targeted compliance and general utility require separate measurements. |
| [R16: function vectors](https://arxiv.org/abs/2310.15213), [R17: task vectors](https://aclanthology.org/2023.findings-emnlp.624/) | Extract reusable task representations from in-context demonstrations. A direction can change task execution or output mapping, so ontology compatibility must not be inferred merely from a changed answer distribution. |
| [R14: PASTA](https://arxiv.org/abs/2311.02262) | Reweights attention toward user-specified spans at profiled heads. It is a natural alternative for emphasizing ontology rules, using a different intervention from residual addition. |
| [R09: DIRECTER](https://arxiv.org/abs/2603.06745) | Scales instruction-token keys in the KV cache and uses output plausibility to adapt steering. It explicitly tackles oversteering and instruction adherence; a strong attention-based competitor should be considered in follow-up work. |

For unit direction d, additive steering changes h to h + αd. Negative α reverses the translation; it does **not** remove h's existing component along d. Orthogonal projection changes h to h − (h·d)d; partial projection introduces its own multiplier. SAE feature suppression changes an encoded feature coefficient and reconstruction, while clamping fixes a feature value. Logit interventions edit the output distribution; constrained decoding excludes tokens; final-output filters reject completed text. These operations need distinct names, injection sites, and controls. A linear probe predicts a label; prediction alone does not establish that the direction causally controls reasoning.

## Closest reasoning and structured-knowledge work

[R06](https://arxiv.org/html/2505.12189) separates syllogistic validity from plausibility and evaluates CAA, CAST, and a kNN-based variant, K-CAST. It already studies activation-based mitigation of semantic interference. The current extension concerns causal planning and ontology evolution; no comparable benefit is established here.

[R07](https://aclanthology.org/2025.naacl-long.353.pdf) builds SELECT from benign YAGO concepts and compositions. Its conditional activation baseline uses concept and refusal vectors, testing specificity and descendant/composition generalization alongside prompts and fine-tuning. This anticipates structured control targets and over-suppression evaluation. Selective abstention differs from computing a feasible plan.

[R32](https://openreview.net/pdf/69c979c667564ad900737b8c64ed13022ec74bfd.pdf), SPIKE, describes a learned KG alignment module and circuit injection of updated-minus-initial representations. It anticipates structured-change interventions. Evidence comes from indexed anonymous primary text; direct full-text access and final authors/status verification were blocked. The access limit warrants caution, but preserves the novelty threat.

[R08](https://arxiv.org/html/2603.20795v1), MEGA, studies successful and failed knowledge edits and learns scope-gated activation transport at attribution-informed attention-residual sites. Its factual-edit evaluation includes generalization and locality. Ontology adaptation is related to knowledge editing, but changing a world's allowed transitions is broader than changing one factual association.

[R33](https://arxiv.org/abs/2607.10248) reports low-rank causal routing across mental-space types and interventions on rule-derived conclusions. Its distinction between a reported value and a consequence inferred from that value is especially relevant: consistent prose is not sufficient evidence of consistent reasoning. The planned evaluator should score final states and goals independently of verbal explanations.

[R34](https://aclanthology.org/2026.eacl-long.125/) compares geometric shifts and learned abstraction for multilingual syllogistic reasoning. This reinforces that content-invariance and generalization across linguistic forms are established questions, while showing why English-only paraphrase evidence has a limited scope.

[R35](https://link.springer.com/chapter/10.1007/978-981-92-1468-6_42) uses typed KG placeholders before extracting contrastive style directions and restores factual entities after generation. [R10](https://arxiv.org/abs/2608.20393) similarly combines typed knowledge engineering with style steering. They anticipate structured knowledge plus activation-control systems, but their factual restoration is an external output operation, not proof that hidden-state interventions enforce causal rules. R35 was inspected at abstract level because its full chapter is subscription content.

[R30](https://www.ayurvedicpoint.it/images/pdf/EC_LLM_V2.pdf), §7.2, proposes contrastive ontology-framing prompts and residual addition of a “process-relational ontology vector.” This is a prior conceptual proposal for ontology-oriented steering, independent of whether its broader claims are convincing. The passage does not report the proposed causal intervention experiment. The current paper should neither ignore this predecessor nor endorse claims about internal metaphysics based only on output diagnostics.

## Erasure, model editing, and feature-level alternatives

[R11](https://arxiv.org/abs/2306.03819), LEACE, supplies a minimal affine map with a guarantee against linear prediction under its distributional and loss assumptions. [R12](https://arxiv.org/abs/2004.07667), INLP, iterates classifier fitting and nullspace projection. Neither guarantee means a concept is absent from every nonlinear computation or later layer. A one-direction projection is not automatically a LEACE eraser.

[R13](https://arxiv.org/abs/2406.11717) gives a causal directional example for refusal, including addition and ablation. It does not establish that arbitrary multi-rule ontology compatibility is represented by one similarly stable direction. Refusal vectors are also a confound here: universally saying no can improve a violation metric while destroying valid task performance.

[R22](https://arxiv.org/abs/2202.05262), ROME, and [R23](https://arxiv.org/abs/2210.07229), MEMIT, alter model weights to update factual associations. Their specificity/generalization evaluations are relevant, but permanent edits and transient inference hooks differ in persistence, model state, and experiment design. Repeated ontology versions need not imply permanent knowledge deletion.

[R27](https://arxiv.org/abs/2406.04093) studies sparse-autoencoder scaling and feature-quality metrics. SAE features can provide finer candidate interventions, yet an available dictionary, its model/layer match, and reconstruction artifacts are substantial prerequisites. Training a new large SAE is outside a small weekend study. A feature labeled “magic” would require causal validation and valid-magic controls before being used to suppress incompatibility.

## Fictional worlds and stronger non-steering alternatives

[R18](https://arxiv.org/abs/2210.01240), PrOntoQA, generates synthetic first-order world models, including fictional contexts, and parses generated reasoning into proofs. [R19](https://aclanthology.org/2021.findings-acl.317/), ProofWriter, evaluates implications, proofs, and abduction over natural-language theories. [R20](https://arxiv.org/abs/2311.15930), WorldSense, disentangles abstract arrangements from surface vocabulary. These defeat a first synthetic-world or first symbolic-reasoning-evaluator claim. Resource accounting and version transitions are evaluation extensions to document explicitly.

[R21](https://deepmind.google/research/publications/9266/) demonstrates content effects across reasoning tasks. It motivates testing conflicting priors but does not show that the current synthetic fantasy model will exhibit measurable interference. An unsteered pilot must establish that premise rather than assume it.

[R24](https://aclanthology.org/2023.findings-emnlp.248/), Logic-LM, translates problems into symbolic form, uses a deterministic solver, and repairs formalizations. [R31](https://arxiv.org/abs/2602.03439) compiles ontologies into executable tools for constrained KG construction. They are strong alternatives when the practical goal is consistency. A symbolic oracle is an evaluation reference here; giving the model oracle answers changes the system and is a separate condition.

[R25](https://arxiv.org/abs/2406.03746) combines domain-KG construction with staged KG/LLM alignment; it is a trained knowledge-infusion approach rather than the proposed frozen-model contrastive intervention. Retrieval of correct rules, structured prompting, and lightweight fine-tuning remain practical competitors. A weekend scope may defer fine-tuning, but must not claim steering outperforms an untested competitor.

[R26](https://aclanthology.org/2021.emnlp-main.779/), PICARD, rejects inadmissible tokens during incremental parsing. Syntactic JSON validity and semantic plan legality are different outcomes. Any grammar mask, semantic action mask, solver repair, or completed-output rejection must be disclosed and evaluated separately from activation steering.

[R36](https://cs191.stanford.edu/projects/Tey,Joseph_CS191W.pdf) already applies SAE interventions and contrastive vectors to fantasy style and magical themes. It is an undated Stanford project report with a small style-transfer evaluation, not an ontology-compliance experiment. Its existence further rules out relying on fantasy aesthetics as novelty.

## Evaluation threats and required responses

[R29](https://arxiv.org/abs/2407.12404v8) finds substantial variation and prompt-dependent failures of steering. [R37](https://arxiv.org/abs/2505.22637) connects reliability to agreement among training activation differences. Report per-family effects, harms, and uncertainty; a favorable aggregate can conceal reverse effects.

[R28](https://arxiv.org/abs/2309.16042) shows patching conclusions depend on corruption and metric choices. Use patching only for scoped diagnostic hypotheses; a successful insertion or ablation does not identify an entire ontology circuit.

[R38](https://arxiv.org/abs/2607.25270) holds intervention fixed while changing activation sources and finds execution-boundary states especially consequential. Teacher-forced compatible/incompatible completions are a baseline extraction policy, not a validated choice. Freeze token readout, then test a boundary-readout ablation on development data rather than searching after test outcomes.

[R39](https://arxiv.org/abs/2608.22985) freezes interventions while changing answer encodings and finds extraction-index effects in some settings. Counterbalance candidate labels during construction, evaluate row/order and label remappings without refitting, and measure open-ended plan execution. Higher accuracy under one mapping does not establish semantic control.

Other decisive threats are inherited training familiarity with test rules, leakage through scenario IDs, template overlap, answer length or refusal cues, prompt asymmetry between steered and unsteered arms, unbalanced prohibited/valid tasks, hidden oracle use, and post-test hyperparameter choice. All can explain apparent success without ontology-specific reasoning improvement.

## Claim–evidence matrix

| Candidate claim | Evidence against broad novelty | Permitted statement now | Required evidence later |
|---|---|---|---|
| New activation-steering algorithm | R02–R05 | Apply established contrastive addition. | A genuinely distinct intervention, algorithmic comparison. |
| First structured-specification-derived steering | R07, R32, R35 | Structured compilation is a benchmark construction choice. | Broader review and comparison, not wording alone. |
| First suppression of prior-knowledge interference | R06, R21, R34 | Extend content-effect questions to a causal fantasy world. | Controlled prior-conflict factor with matched tasks. |
| First fictional ontology reasoning study | R18–R20, R33 | Release a new operational world and evaluator. | Evidence for a useful evaluation gap. |
| Steering adapts to changing conceptual worlds | R08, R23, R32 | Test a specified compatibility transition. | Matched/stale vector comparisons and valid-new-ability retention. |
| Internal incompatible concepts are removed | R11–R13 do not imply this here | Measure behavior under specified interventions. | Stronger internal and distributional evidence; no blanket claim. |
| Directions control semantics, not labels | R38–R39 | Treat semantic control as an empirical question. | Label remapping, paraphrase, and executed-plan agreement. |
| Practical advantage over prompting | No repository model results | Compare matched ontology prompt with and without steering. | Held-out positive effect with utility noninferiority. |
| Guaranteed containment | No supporting evidence | Report observed error rates with uncertainty. | This experiment cannot establish a universal guarantee. |
| Novel benchmark combination | No exact inspected match; bounded search | A candidate protocol contribution. | Independent expert review, further citation tracing, useful empirical analysis. |

## Reviewer-style objections the paper must survive

1. **“This is CAA on a new dataset.”** Agree about the intervention; justify the diagnostic value of controlled compatibility changes and composition tests.
2. **“This is SELECT with a fantasy skin.”** Show executable causal effects, resource constraints, useful plans, and a narrowly permitted new ability rather than category abstention.
3. **“K-CAST already fixes content effects.”** Cite it centrally and limit the extension to operational worlds and revision-specific damage.
4. **“SPIKE already compiles changing KGs into interventions.”** Cite the inspected anonymous source, resolve metadata before an archival novelty claim, and avoid claiming structured-change steering itself.
5. **“The vector just prefers VALID.”** Require balanced answer encodings, frozen remapping tests, multi-step plan execution, and label-free paraphrases.
6. **“The model refuses everything.”** Require valid-task retention and joint success, including newly legal temporal cases.
7. **“You selected the best layer on test.”** Freeze model, extraction, validation selection, and paired test comparisons before test generation.
8. **“The oracle solves the task.”** Keep symbolic evaluation outside the model input in the primary arms; identify retrieval or solver-assisted arms separately.

The study remains scientifically useful if steering fails: it can locate the boundary where one low-rank behavioral direction does not generalize to multi-rule, changing specifications. A null result is informative only after implementation no-op checks, a steerable positive control, adequate unsteered performance, and uncertainty assessment rule out trivial failure modes.
