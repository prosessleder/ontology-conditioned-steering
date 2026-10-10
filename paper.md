# Controlling Incompatible Magic: Ontology-Conditioned Activation Steering in a Fantasy Landscape

**Tim O'Brien**

ORCID: [0009-0001-2589-347X](https://orcid.org/0009-0001-2589-347X)

Research protocol preprint - Version 0.1.0 - 9 October 2026

Not peer reviewed

**License: CC BY 4.0.** Copyright 2026 Tim O'Brien. [License terms](https://creativecommons.org/licenses/by/4.0/).

## Abstract

Language models operating within a specified conceptual world may substitute familiar mechanisms for those permitted by the supplied rules. This research protocol investigates whether contrastive activation steering improves operational consistency with a causal ontology beyond structured prompting, and whether an intervention remains useful when the ontology changes. We define a synthetic fantasy world with class-restricted actions, finite energy, conserved object identity, and bounded transformations. Two versions differ in the availability of a narrowly constrained local rewind operation. A deterministic benchmark contains 720 cases across nine scenario families and distinguishes permitted but infeasible actions from prohibited and undefined capabilities. Version-specific steering directions will be estimated from matched training responses and evaluated against identical prompt-only, stale-direction, zero-coefficient, and norm-matched random controls. The primary outcome combines correct classification with legal goal-reaching execution; secondary outcomes measure task performance, unknown-concept recognition, and suppression of newly valid temporal plans. Hyperparameters will be selected on development data and fixed before held-out evaluation. The pilot has only three independent test families, so its uncertainty estimates will be exploratory. Model-performance experiments have not yet been conducted. The protocol provides a controlled test of the benefits and limitations of activation steering under changing causal rules, without assuming that improved output consistency implies removal of internal concepts.

**Keywords:** activation steering; ontology; causal reasoning; conceptual interference; ontology evolution

## 1. Introduction

A language model's broad knowledge can conflict with the rules of a particular operating world. In a fantasy simulation, for example, an agent might be allowed to heat and reshape clay using finite energy but be unable to create matter or travel through time. A fluent solution using an unavailable mechanism would be inconsistent with the simulation even if that mechanism is familiar from other fiction. The target of evaluation is therefore consistency with an explicit specification, rather than factual truth about the physical world.

Prompting supplies the specification but leaves its interpretation to the model. The model must distinguish capability membership from applicability, combine action preconditions, track resources, and determine whether a plan achieves its goal. Activation steering offers an additional intervention: modifying selected hidden states during inference while preserving the same prompt. Contrastive methods provide a simple way to estimate a direction from examples of compatible and incompatible behavior [1-3].

Ontology evolution creates a particular challenge. A direction that discourages an unavailable capability may continue to discourage it after the rules permit a constrained version. We study this possibility using two versions of an executable causal world. In the first version, local rewind is undefined. In the second, it becomes available under explicit restrictions; general time travel remains prohibited. Successful adaptation requires retaining useful temporal reasoning while respecting those restrictions.

The study asks whether ontology-conditioned activation addition improves held-out operational consistency beyond a strong structured prompt, whether it preserves ordinary task performance, and whether a current-version direction reduces the cost of applying a stale intervention. Its contribution is an evaluation design for these questions. The intervention builds on existing contrastive steering methods, and the fictional setting serves as a controlled experimental environment.

## 2. Related work

Contrastive Activation Addition estimates behavioral directions from paired responses and adds them to residual activations [1]. Activation Addition and representation engineering similarly use internal representations for inference-time behavioral control [2,3]. Conditional Activation Steering selects whether to apply a behavioral direction using activation-based conditions [4]. The present method uses explicit ontology-version selection rather than a learned conditional gate.

Content-effect steering addresses interference between semantic plausibility and formal validity in reasoning [5]. SELECT evaluates abstention techniques over knowledge-graph concepts, including their specificity and generalization [6]. These studies motivate separate measurements of correct reasoning and over-suppression. Our task extends this evaluation focus to executable plans with action costs, causal preconditions, and a controlled change in capability membership.

CounterSteer constructs directions from paired behavioral episodes and applies subtraction to tool-result activations during prefill [7]. Its security setting and token schedule differ from the current study, but its paired interventions and capability checks motivate evaluating useful behavior alongside error reduction. Knowledge editing [8] and structured knowledge injection, including SPIKE [9], address changing factual information. Ontology-framing steering has also been proposed [10], and causal interventions have been used to investigate routing among fictional and other mental spaces [11]. These approaches establish relevant precedents for representation control under supplied or changing conceptual context.

Synthetic-world reasoning is studied in PrOntoQA, ProofWriter, and WorldSense [12-14]. The present world adds finite-resource action execution and a version transition that separates unknown, prohibited, and newly permitted capabilities. The intended distinction is the joint evaluation of these properties, rather than the use of fantasy content itself.

Activation-source selection and answer-encoding studies show that an extracted direction need not control the semantic property suggested by its examples [15,16]. Accordingly, we include plan-execution outcomes and contrast pairs with both changed and preserved operation vocabulary. Structured prompting is the main practical comparator. Retrieval, conditional steering, grammar-constrained generation, and symbolic plan verification remain relevant alternatives for subsequent comparisons.

## 3. Methods

### 3.1 Research questions and hypotheses

The primary hypothesis is that a version-matched direction increases operational success relative to the identical structured ontology prompt without steering. Three secondary hypotheses concern preservation of ordinary feasible-task performance and unknown-concept recognition, improved V2 temporal performance relative to a stale V1 direction, and specificity relative to norm-matched random directions. Generalization will be examined across held-out action compositions and three fixed wording styles.

A five-percentage-point loss margin will be used to screen development candidates for ordinary feasible-task success and unknown recognition. This is a practical pilot tolerance rather than an established acceptable loss. Test estimates and uncertainty will be reported separately from this development screen.

### 3.2 Causal world and task definition

An ontology version specifies a capability registry, entity types, action schemas, preconditions, costs, and transition rules. A state contains actors and objects. Actors have a class and nonnegative integer energy. Objects have an identifier, kind (solid or water), material, integer mass from 1 to 3, location on the chain A-B-C-D, integer temperature from -4 to 8, shape, and a Boolean living attribute. Solids have shape raw, tile, or bowl; water has shape fluid.

The world is organized around seven constraints: explicit capability membership; conserved identity and substance; class-bound actions; nonrenewable energy; bounded heat; local transformation; and version-specific temporal scope. No operation creates, removes, splits, merges, transmutes, or changes the mass or living status of an object. Every registered action requires a nonliving target, an actor of the appropriate class, and sufficient energy. Costs are deducted before state changes. Failed actions have no effect.

Table 1 defines the available operations. The discrete energy and temperature units are simulation variables, not a claim about physical thermodynamics.

**Table 1. Action semantics.** Ordinary actions are available in both versions; temporal actions are available only in V2. Here m denotes object mass.

| Operation | Actor class | Preconditions and effect | Energy cost |
| --- | --- | --- | --- |
| heat | tender | Nonzero integer temperature change with magnitude at most 4; resulting temperature remains from -4 to 8. Other properties are preserved. | magnitude of change times m |
| shape | mason | Solid at temperature 2-5; change to a different raw, tile, or bowl form. | 2m |
| move_water | weaver | Water at temperature 1-4; move exactly one adjacent location on A-B-C-D. | 2m |
| anchor (V2) | keeper | Record one nonliving solid of mass at most 2; no active or previously consumed anchor. | 2 |
| rewind_local (V2) | keeper | Same keeper and target as the anchor; restore the recorded object after exactly one or two uninterrupted heat/shape actions on that target. Consume the anchor. | 3 |

Capability membership has three values. In V1, heat, shape, and move_water are permitted; anchor and rewind_local are unknown. V2 additionally permits the two temporal operations. Both versions explicitly prohibit create_matter, resurrect, mind_control, teleport, and time_travel. Every other capability is unknown. An unknown capability is undefined rather than implicitly prohibited. A permitted capability may nevertheless be infeasible in a particular state.

V2 permits at most one anchor and one rewind in an episode. A third intervening action, an action of another type, or an action on another target invalidates the anchor. Rewind restores the object's physical snapshot but does not restore actor energy or remove recorded events. These restrictions define local restoration rather than general time travel.

Each task presents an initial state, requested capability, and goal. Goals may specify final object properties and minimum counts of historical actions. Plans contain at most four actions. If the requested capability is permitted, the model must determine whether a legal plan reaches the goal. Otherwise it must identify the capability as prohibited or unknown and return an empty plan. The response is a JSON object with four fields: status (feasible, infeasible, prohibited, or unknown), concept_status (permitted, prohibited, or unknown), plan, and explanation.

For example, consider a nonliving solid of mass 1 at temperature 0, a keeper with energy 5, and a tender with energy 2. In V2, anchor, heat by 2, and rewind_local can restore the initial temperature while leaving the keeper and tender energy spent. A goal requiring both a heat event and a rewind event distinguishes this plan from ordinary cooling. The same requested rewind capability is unknown in V1.

### 3.3 Benchmark construction

The deterministic generator produces 720 cases: 576 ordinary core cases and 144 temporal-adaptation cases. Nine structural families are assigned wholly to training, development, or test, with three families and 240 cases per split. Both ontology versions and all variants of a case remain in the same split. Training includes heating followed by shaping and warming followed by water movement; held-out structures include multi-object plans and longer transport/restoration compositions.

Core cases balance feasible, infeasible, prohibited, and unknown outcomes. Temporal cases comprise 72 V1 unknown requests paired with 36 V2 feasible and 36 V2 infeasible requests. V2 infeasibility varies across insufficient keeper energy, excessive object mass, living targets, and absence of a keeper. Reference feasible plans are checked by the symbolic executor. Infeasible cases use resource or precondition certificates, with independent bounded-search checks in the validation suite.

Each split contains direct, paraphrased, and distracting-lore wording. These styles are repeated across families and tied to instance generation rather than fully crossed with every state. They support a limited wording-robustness analysis, not independent linguistic replication.

The primary extraction pool contains 48 training pairs, 24 per version, drawn from ordinary feasible cases. Version twins have identical response text and corruption, so only their ontology context differs. Four negative types are equally represented: replacing an operation with a prohibited capability, replacing it with an unknown capability, substituting a wrong-class actor while preserving the operation, and reversing action order to violate preconditions. Compatible and incompatible responses retain the same status and membership fields.

An exploratory 60-pair pool adds V2 temporal examples, yielding 24 V1 and 36 V2 pairs. Its effects may reflect changed sample size and composition as well as ontology information. Gold classifications and plans are excluded from model evaluation prompts. Training examples determine directions; development examples determine intervention parameters; test answers are generated only after selection is fixed.

### 3.4 Activation intervention

The initial model is Qwen2.5-1.5B-Instruct, pinned to revision 989aa7980e4cf806f80c7fef2b1adb7bc71aa306. For each version v and decoder-block output l, paired structured responses are teacher-forced under the same task and ontology prompt. Let h_i^+(v,l) and h_i^-(v,l) denote residual outputs at the final response token for the compatible and incompatible endpoints. With n_v pairs, the estimator is:

    d(v,l) = (1/n_v) sum_i [h_i^+(v,l) - h_i^-(v,l)]
    u(v,l) = d(v,l) / ||d(v,l)||_2
    s(v,l) = (1/(2n_v)) sum_i [||h_i^+(v,l)||_2 + ||h_i^-(v,l)||_2]
    h' = h + alpha s(v,l) u(v,l)

Zero or nonfinite directions are rejected. The training activation scale s makes the magnitude of the added vector proportional to the mean endpoint norm. The direction is added at the last prompt position during prefill and at the current token during cached decoding; other prompt positions are unchanged. The ontology version selects a separately estimated direction.

Candidate decoder outputs are zero-based layers 6, 13, and 20 of the 28-block model. Coefficients are 0, 0.025, 0.05, 0.1, and 0.2. This is additive residual steering with fixed model weights. Projection, sparse-feature suppression, weight editing, logit modification, and output filtering are separate interventions. The transfer from a teacher-forced response endpoint to prompt and generation positions is an assumption evaluated through behavior.

### 3.5 Experimental conditions and parameter selection

Table 2 specifies the comparisons. Every condition receives the same task state and output contract. The primary contrast uses byte-identical structured prompts with and without the current-version direction.

**Table 2. Experimental conditions.** The zero-coefficient condition is included in development selection and implementation validation.

| Condition | Ontology context | Activation treatment | Purpose |
| --- | --- | --- | --- |
| A | Absent | None | Descriptive prior-world behavior |
| B | Full rules | None | Ordinary ontology prompting |
| C | Full rules plus structured checks | None | Primary prompt baseline |
| C+V | Identical to C | Current-version direction | Incremental steering effect |
| C+old | V2, identical to C | V1 direction | Cost of stale steering |
| C+random | Identical to C | Random unit direction | Perturbation specificity |
| C+zero | Identical to C | Zero coefficient | Development and implementation control |

One shared layer and coefficient will be selected across versions by maximizing development family-macro operational success. Selection requires ordinary feasible-task success and unknown recognition to decline by no more than five percentage points relative to C, evaluated separately within each version. Ties favor the smaller coefficient, then the earlier layer. Zero remains eligible if no positive intervention improves the constrained objective.

The selected configuration, candidate scores, model revision, source, ontology, dataset, and vector hashes will be recorded before test generation. Primary decoding will be greedy. Secondary sampling will use temperature 0.7 and seeds 11, 29, and 47 with the same intervention parameters; sampled and greedy outcomes will be analyzed separately.

The stale comparison applies the V1 direction in V2 using the selected layer, coefficient, and V2 training activation scale. Current, stale, and random interventions therefore have matched added-vector norms on V2. Random controls use three predefined draws, seeded 314159, 271828, and 161803 with the layer index added. A reverse V2-on-V1 intervention is outside the initial comparison.

### 3.6 Outcomes and statistical analysis

The primary outcome is operational success. Every case requires valid response syntax and correct status and concept membership. Feasible cases additionally require a legal action sequence and goal completion; infeasible, prohibited, and unknown cases require an empty plan. This prevents indiscriminate refusal from counting as success on feasible tasks.

Secondary outcomes are schema validity, status accuracy, concept-membership accuracy, feasible-task success, prohibited/undefined action incidence, unknown recognition, and false rejection of feasible tasks. Newly permitted temporal success will be reported separately. Explanatory prose is not semantically certified by the executor, and mentioning an incompatible concept is not treated as an executable violation.

Malformed responses remain failures in primary and applicable accuracy/task denominators. Action interference and false-rejection classification are unavailable when parsing fails; their rates will use evaluable responses and will be accompanied by parsing coverage. Unknown-concept recognition will distinguish echo_matter, which occurs in training negatives, from unseen undefined names and the V1 rewind transition.

Outcomes will be paired by case, version, and generation seed. Within-family averages will then receive equal weight across families. The primary contrast is C+V minus C. A paired percentile bootstrap will resample entire families 10,000 times with seed 1729, preserving version twins and repeated trials within each cluster. Micro averages, denominators, all family effects, and uncertainty will also be reported.

There are only three independent test families. Intervals are exploratory, and the temporal feasible subset has only one family; it cannot support an informative family-cluster interval. Temporal results will therefore be descriptive within-family rates. Numeric variants and repeated seeds do not increase structural independence. The pilot sample size is chosen for local feasibility rather than a powered confirmatory test. Secondary contrasts and robustness analyses will be treated as exploratory. Utility-preservation estimates will be reported with uncertainty; passing the development screen alone will not establish noninferiority.

### 3.7 Implementation and study status

The implementation uses PyTorch 2.9.0 and Transformers 4.57.1 with decoder-block forward hooks, batch size one, a 4,096-token context limit, and a 384-token output limit. Apple Metal (MPS) is the target device on an M4 Max with 48 GiB unified memory; CPU execution is available as an explicitly recorded alternative. Randomly initialized tiny-model tests verify hook positions, zero-coefficient equivalence, downstream effects, cleanup, and cached generation. Symbolic tests validate the reference semantics and dataset construction.

The pretrained-model experiment has not yet been conducted. A development-only technical pilot will measure output-format failures, runtime, and memory before the full parameter grid. Software tests do not establish steering effectiveness. No measured adherence, adaptation, utility, or throughput result is reported here. This versioned analysis plan has not been externally preregistered.

## 4. Discussion

The protocol separates several explanations for apparent improvement. Higher classification accuracy with unchanged executable success would suggest better surface labeling. Lower invalid-action incidence accompanied by loss of feasible-task success would indicate over-suppression. A current-version direction that outperforms the stale direction but does not exceed prompt-only C would indicate recovery from intervention-induced harm rather than an incremental advantage over prompting. A learned direction must also be assessed against random perturbations of the same magnitude.

Several limitations constrain interpretation. The families share operation vocabulary, generator grammar, and fixed wording styles. Only one temporal composition is held out, and several history restrictions are checked by the simulator without corresponding model-evaluation slices. More independently authored structures, temporal near-misses, and a second ontology are needed for broader generalization claims.

Contrast pairs contain correlated lexical, actor, and ordering cues. Preserving operation vocabulary in half the negatives reduces a simple banned-word explanation but does not identify a unique compatibility representation. Final-response extraction may encode completion state or formatting rather than the states needed to generate a plan [15,16]. The primary common-support pool contains no temporal positive examples, making adaptation a test of changed ontology context rather than direct temporal demonstration. The extended pool changes that interpretation.

V2's context is longer and includes different definitions and examples. Differences between version-specific directions may therefore reflect context length, token position, or exemplars in addition to capability semantics. Matched-length contexts and controls for version labels and examples are appropriate follow-up experiments. Stronger conditional steering, retrieval, and symbolic constraints should also be compared before drawing practical conclusions beyond the prompt baseline.

Finally, operational consistency is a behavioral property of the evaluated outputs. It does not demonstrate that incompatible concepts have disappeared from the model's representations or establish reliability for every possible input. A null result would bound the tested extraction policy, intervention sites, and task distribution rather than disprove all representation-level approaches.

## 5. Conclusion

This protocol defines an executable test of activation steering under an evolving causal ontology. Matched prompts, version-paired cases, useful-plan requirements, stale-direction comparisons, and utility measures are intended to distinguish improved operational consistency from refusal, formatting changes, and nonspecific perturbation. The study's initial scope is an exploratory local-model pilot. Empirical conclusions about effectiveness and adaptation require the planned held-out measurements.

## Code and data availability

The ontology specifications, deterministic benchmark generator, evaluator, intervention implementation, dependency lock, and analysis plan are available at https://github.com/prosessleder/ontology-conditioned-steering. Dataset generation uses seed 1729 and 12 instances per family-label setting. Model runs will record prompts, outputs, token identifiers, intervention parameters, and artifact hashes. Generated model outputs and frozen selections will be made available with the experimental report.

## Acknowledgments

AI-assisted tools were used for literature search, manuscript drafting, and software implementation.

## References

[1] Rimsky N, Gabrieli N, Schulz J, Tong M, Hubinger E, Turner A. Steering Llama 2 via Contrastive Activation Addition. Proceedings of ACL; 2024:15504-15522. https://doi.org/10.18653/v1/2024.acl-long.828

[2] Turner AM, Thiergart L, Leech G, Udell D, Vazquez JJ, Mini U, MacDiarmid M. Steering Language Models With Activation Engineering. ICLR; 2025. https://arxiv.org/abs/2308.10248

[3] Zou A, et al. Representation Engineering: A Top-Down Approach to AI Transparency. arXiv:2310.01405; 2023. https://arxiv.org/abs/2310.01405

[4] Lee BW, Padhi I, Ramamurthy KN, Miehling E, Dognin P, Nagireddy M, Dhurandhar A. Programming Refusal with Conditional Activation Steering. ICLR; 2025. https://arxiv.org/abs/2409.05907

[5] Valentino M, Kim G, Dalal D, Zhao Z, Freitas A. Mitigating Content Effects on Reasoning in Language Models Through Fine-Grained Activation Steering. AAAI. 2026;40(39):33314-33322. https://doi.org/10.1609/aaai.v40i39.40617

[6] Vasisht K, Kaur N, Pruthi D. Knowledge Graph Guided Evaluation of Abstention Techniques. NAACL; 2025:6921-6939. https://doi.org/10.18653/v1/2025.naacl-long.353

[7] Russinovich M. CounterSteer: Suppressing Indirect Prompt Injection with Activation Steering. arXiv:2609.36570v1; 2026. https://arxiv.org/abs/2609.36570v1

[8] Meng K, Bau D, Andonian A, Belinkov Y. Locating and Editing Factual Associations in GPT. NeurIPS; 2022. https://arxiv.org/abs/2202.05262

[9] Anonymous. Circuit-level Steering for Personalized Knowledge Injection in Language Models. Anonymous ICLR 2026 submission. https://openreview.net/pdf/69c979c667564ad900737b8c64ed13022ec74bfd.pdf

[10] Morandi A. Epistemological Coherence in Large Language Models: The Compound Problem of Grammatical-Ontological and Epistemological Contamination in AI Knowledge Representation. Author-hosted preprint; 2026. https://www.ayurvedicpoint.it/images/pdf/EC_LLM_V2.pdf

[11] Steele O, Wen J, Han Y. One Mechanism for Many Mental Spaces: A Shared Router over a Value Slot in Language Models. arXiv:2607.10248; 2026. https://arxiv.org/abs/2607.10248

[12] Saparov A, He H. Language Models Are Greedy Reasoners: A Systematic Formal Analysis of Chain-of-Thought. ICLR; 2023. https://arxiv.org/abs/2210.01240

[13] Tafjord O, Dalvi B, Clark P. ProofWriter: Generating Implications, Proofs, and Abductive Statements over Natural Language. Findings of ACL-IJCNLP; 2021:3621-3634. https://doi.org/10.18653/v1/2021.findings-acl.317

[14] Benchekroun Y, et al. WorldSense: A Synthetic Benchmark for Grounded Reasoning in Large Language Models. arXiv:2311.15930; 2023. https://arxiv.org/abs/2311.15930

[15] Ye J, Ran L, Yao Z, Wang C, Jiang Y, Hou L, Li J, Pan L. Where Steering Signals Come From: Activation Source Selection in Activation Steering. arXiv:2607.25270; 2026. https://arxiv.org/abs/2607.25270

[16] Gao Z, Peng S, Wakamiya S, Aramaki E. What Does Activation Steering Control? Attribution Across Answer Encodings and Output-Sensitive Subspaces. arXiv:2608.22985; 2026. https://arxiv.org/abs/2608.22985
