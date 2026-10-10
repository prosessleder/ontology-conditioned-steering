# Controlling Incompatible Magic: Ontology-Conditioned Activation Steering in a Fantasy Landscape

**Tim O'Brien**  
Research protocol preprint, version 0.1.0 - 9 October 2026  
Repository: https://github.com/prosessleder/ontology-conditioned-steering

## Abstract

A language model operating inside a specified conceptual world may substitute familiar but incompatible mechanisms for the rules in its context. We propose a controlled experiment testing whether contrastive residual activation addition improves operational consistency with an explicit causal ontology beyond a strong structured prompt. The benchmark, the Seven Laws of Magic, contains class-restricted actions, nonrenewable resources, conserved object identity, and bounded transformations. Two ontology versions introduce a narrow local rewind capability without permitting general time travel. A symbolic simulator distinguishes unknown concepts, prohibited transformations, and permitted operations whose preconditions may nevertheless be unsatisfied. Separately learned version-specific directions are evaluated against identical prompt-only, stale-vector, zero-intervention, and norm-matched random controls. The protocol measures executable goal completion, classification accuracy, inappropriate action use, and over-suppression of newly valid temporal plans. Prior work already establishes activation steering, conditional control, knowledge-graph-grounded abstention, and mitigation of reasoning content biases. The candidate contribution is therefore a reproducible causal-ontology version-transition protocol rather than a new steering algorithm. This release provides a manuscript, ontology specification, benchmark generator, evaluator, and intervention implementation. Model-performance experiments remain pending; no steering benefit, guaranteed containment, or empirical novelty is claimed.

**Keywords:** activation steering; causal ontology; conceptual interference; synthetic reasoning; ontology evolution; reproducibility

## 1. Introduction

The broad knowledge that makes language models useful can conflict with a narrow operating world. A fantasy simulation might permit heating stone with a finite energy cost while excluding resurrection and leaving dream-binding undefined. A fluent answer that solves a puzzle through resurrection would violate that world even if resurrection is familiar from other fiction. The relevant target is consistency with the supplied specification, not correspondence to facts about the physical world.

An explicit ontology can state entities, classes, actions, relationships, preconditions, costs, and consequences. Supplying these rules in a prompt is a strong baseline. It does not by itself establish that a model will apply them correctly in an unfamiliar combination. Activation steering offers a complementary intervention: alter selected hidden states at inference time while retaining the same rule context. Our research question is whether a formal ontology can supply training examples and version selection for such interventions, improving operational consistency without impairing valid reasoning.

We study a deliberately small original fictional world. The playful setting supplies interpretable counterfactual rules and objective outcomes. Fictional-world evaluation is established practice [R18, R19, R20]; the fantasy theme is not a scientific novelty claim. The distinctive stressor is ontology evolution. A model should reject general time travel in both versions, identify a narrow local rewind as undefined in V1, and use that capability when it becomes permitted in V2. Suppressing every temporal concept would fail this test.

Three artifacts form the proposed contribution: a versioned causal benchmark with explicit epistemic categories, a matched intervention protocol separating status labeling from executable planning, and a reproducible test of stale-vector harm during a capability transition. These are prospective contributions whose empirical usefulness requires measurements. This study is independent of Bounded Agency; governance and delegated decision authority are outside the experiment.

## 2. Prior work and adversarial positioning

Contrastive Activation Addition (CAA) derives behavioral directions from paired responses and changes model activations at inference [R02]. Activation Addition (ActAdd) and representation engineering provide related forms of representation control [R03, R04]. They motivate a simple difference-of-means baseline rather than a claim that the present intervention is algorithmically new.

Conditional Activation Steering (CAST) already selects behavioral interventions from input-dependent activation patterns [R05]. SELECT grounds the evaluation of abstention techniques, including CAST, in a knowledge graph and examines generalization versus specificity [R07]. These precedents defeat a broad claim that this is the first ontology-associated activation-control study. Our implementation selects a stored direction using an explicit version identifier; it does not add a learned CAST gate.

Valentino and colleagues directly investigate interference between content plausibility and formal validity using static and conditional steering [R06]. Their work is the strongest established challenge to framing this experiment as the first removal of prior-knowledge interference from reasoning. Our proposed distinction is multi-action causal plan validity and a controlled capability boundary change. It must be demonstrated rather than inferred from a different theme.

CounterSteer is Mark Russinovich's September 2026 preprint [R01]. It learns behavioral directions from paired episodes and subtracts them over tool-result tokens during prefill, with causal and capability checks. Its indirect prompt-injection findings do not establish ontology-reasoning benefits. We borrow the discipline of checking behavioral benefit and collateral cost, while using a different task and intervention schedule.

The SPIKE submission describes changed knowledge-graph representations injected into model circuits [R32], challenging broad first structured-knowledge-derived activation-update claims. Direct PDF access was blocked; indexed primary text informed the review, with authorship and acceptance unresolved. ROME [R22] also establishes knowledge updating as prior work. Respecting changing action preconditions is a distinct evaluation target, not automatically a new scientific contribution.

Morandi explicitly proposes contrastive ontology-framing vectors [R30], while Steele and colleagues study causal routing among fictional and other mental spaces [R33]. These precedents further constrain an ontology-steering originality claim, although neither establishes this proposed multi-action version-transition evaluation.

Knowledge augmentation, constrained generation, and symbolic verification are competing solutions. A strong full-ontology prompt is the principal practical comparator. Retrieval can reduce context burden but may omit dependencies; grammar-constrained decoding can enforce response syntax without establishing causal validity. A symbolic validator can reject invalid final plans directly. Such an output system may dominate steering on reliability, but answers a different causal question: whether the model's unfiltered generation changes under an internal intervention. Report its system-level utility separately if implemented.

The adversarial review therefore rejects four broad claims: invention of activation steering, first conditional activation control, first use of an ontology or fictional world, and first structured-knowledge update through hidden-state intervention. The remaining candidate is the joint evaluation of causal rule composition, unknown-versus-prohibited handling, and version-induced over-suppression. The search is documented and bounded; failure to find an exact predecessor does not prove novelty. Further related-work evidence must be incorporated before submission to a venue.

## 3. Formal task and ontology

Let an ontology O_v contain a capability registry, entity types, action schemas, preconditions, and transition rules for version v. A state s contains actors, their classes and remaining energy, and objects with identity, material, mass, temperature, shape, and location. A task x includes s, a requested concept, and a goal g. A plan pi is an ordered list of at most four actions. The symbolic executor T_v(s, pi) either produces a final state and trace or identifies the first invalid action.

Concept status is ternary: permitted, prohibited, or unknown. Membership is separate from applicability. A permitted action may be infeasible because the actor lacks energy, the target is out of range, or no allowed plan reaches the goal. Unknown concepts are neither asserted valid nor converted into explicit prohibitions. The public operation registry is closed for execution; its epistemic classification remains open-world. The model can truthfully name an undefined concept without proposing it as an executable action.

The Seven Laws of Magic are operational constraints rather than a list of taboo words:

1. **Declared capabilities.** Explicitly registered operations have defined semantics; explicit impossibilities such as resurrection and general time travel are prohibited; other proposed capabilities are unknown.
2. **Conservation.** Object identity, material, and mass cannot be created, duplicated, or transmuted by these operations.
3. **Class binding.** Tenders heat, masons shape, weavers move water, and keepers perform the V2 temporal operation.
4. **Cost.** Actions debit finite actor energy. No action replenishes that resource.
5. **Bounded heat.** Temperature changes have specified step limits, cost, and admissible target conditions.
6. **Local transformation.** Shaping and water movement have bounded spatial and material conditions; they cannot stand in for arbitrary teleportation or transmutation.
7. **Temporal scope.** V1 has no registered local rewind. V2 permits anchoring one inert solid and restoring its recorded local physical properties after one or two qualifying edits. The rewind consumes energy, does not restore spent energy, and is single-use for the anchor.

The detailed schemas and constants in experiment/ontology-v1.md and ontology-v2.md are authoritative and implemented by the simulator. Unknown V1 local rewind becomes permitted in V2. General time travel remains prohibited. Model cases include temporal infeasibility from insufficient keeper energy, mass above the anchor limit, living targets, or no keeper. The simulator also checks invalid history and one-use boundaries. A permitted V2 rewind can still be infeasible if the anchor is absent, the object is ineligible, the age exceeds the bound, the keeper lacks energy, or a second rewind is attempted.

An illustrative V2 task requires anchoring a stone, heating or reshaping it, and restoring its initial temperature or shape while leaving actor energy spent. In V1, the same requested capability is unknown. A second task asks for a multi-step ordinary transformation using the appropriate classes within a resource budget. Validity depends on composition, ordering, and costs, not the presence of the word "time."

## 4. Hypotheses

H1 predicts higher held-out family-macro operational success for a version-matched intervention than for the identical structured prompt alone. Executable task success and invalid-action incidence must corroborate the interpretation; improved labels alone do not demonstrate improved planning.

H2 predicts preservation of ordinary feasible-task performance and unknown-concept recognition within proposed 5 percentage-point loss margins. These margins express a pilot decision rule, not a scientifically established acceptable degradation. Test intervals must accompany the losses; an estimate inside a margin is not automatically evidence of noninferiority.

H3 predicts that selecting a V2 direction improves newly valid temporal performance relative to applying the stale V1 direction under the same V2 context. Comparison against unsteered C is essential: merely repairing stale-vector damage does not establish value over prompting.

H4 predicts that the learned direction outperforms norm-matched random controls. H5 asks whether effects persist beyond training compositions and surface forms. The starter benchmark implements structural family holdouts, paired version changes, and three fixed wording styles (direct, paraphrase, distracting lore). Independently authored paraphrases and larger rule systems require separate follow-up datasets.

Null results are informative. The ontology prompt may already saturate performance. Compatibility may not occupy a stable linear direction at the chosen readout. A direction may encode generic refusal, output labels, or answer syntax. Steering may improve superficial classification while reducing executable success. Each outcome restricts the tested method; none establishes impossibility for all representation-level interventions.

## 5. Experimental methodology

### 5.1 Data construction and leakage prevention

The deterministic generator creates states, goals, version-paired cases, reference labels, and compatible/incompatible structured-response pairs. Scenario families are assigned wholly to train, development, or test. Numeric variants and both ontology versions remain together. This prevents splitting a scenario's paraphrase or version counterpart across training and evaluation, although all cases share the underlying action vocabulary and generator design.

The default pilot has 720 cases: 576 core cases and 144 temporal-adaptation cases, with 240 cases in each split. It has only nine structural families, three per split and only one temporal family in test. The primary direction uses 48 train-only ordinary contrast pairs, 24 per version with identical response text and corruption across version twins; only ontology context differs. An extended pool of 60 pairs (24 V1, 36 V2) adds V2 temporal examples and is exploratory because pair count and composition differ. Neither pool makes the structural families independent. This is an exploratory pilot; a larger family suite or independent replication is required before confirmatory generalization claims.

Train examples alone determine vectors. Development examples choose layer and magnitude. Held-out test outputs are generated only after selection is frozen. The experiment records dataset and vector hashes and the source commit. Gold labels and solutions are excluded from inference prompts. The model receives the presented state, goal, requested concept, output schema, and condition-specific ontology context.

Contrastive endpoints share a prompt and differ in plan legality. The primary pool controls pair composition across versions; it tests whether changed context alone changes the learned direction. The extended pool tests the addition of temporal examples but cannot isolate version information from changed training composition. Equivalent fields, concise explanations, and similar plan lengths reduce nuisance cues. They cannot eliminate them: the default contrasts balance prohibited-op substitution, unknown-op substitution, wrong-class actor substitution, and reversed action order. Response status fields remain identical. The latter two negatives retain operation vocabulary, reducing a pure banned-word explanation, while action tokens, order, length, and generic invalidity remain confounds. Label-related confounds apply to additional endpoint recipes. Audit pair differences and run field/label reversal, equal-length, and action-level controls before attributing a behavioral gain to semantic compatibility. The simulator supplies answer correctness; it does not certify the latent meaning of a vector. Recent source-readout and answer-encoding studies [R38, R39] make these controls necessary: answer presence and apparent semantic categories do not by themselves identify what an intervention controls.

### 5.2 Intervention construction

For each selected decoder block l, collect the residual block output at the final token of each teacher-forced structured response. With n matched training pairs, define:

    d_l = (1/n) sum_i (h_i,l,compatible - h_i,l,incompatible)
    v_l = d_l / ||d_l||_2
    s_l = mean of ||h_i,l,label||_2 over both endpoints
    h'_l = h_l + alpha s_l v_l

A zero or nonfinite difference is rejected. V1 and V2 use separately fitted vectors. The supplied version chooses the vector; there is no automatic semantic gate and no online vector update. The primary coefficient grid is {0, 0.025, 0.05, 0.1, 0.2}; block candidates are zero-based outputs 6, 13, and 20 of the 28-block target model.

At inference, modify only the final prompt position during prefill and the current token during cached decoding. Other prompt tokens retain their original activations. This schedule differs from CounterSteer's tool-span prefill intervention. Training endpoint readout and inference intervention sites are not identical; whether the direction transfers is an empirical assumption. Activation pooling and token-site variants are follow-up ablations.

The operation is additive residual steering. Scaling changes the magnitude of that direction. Projection h - (h dot v)v removes a component and is not the implemented intervention. Sparse-feature suppression requires a feature representation, such as an autoencoder, and would be another method. Logit bias and final-output filtering occur at different sites. Weight editing changes parameters; this intervention leaves weights fixed. These mechanisms must not be reported interchangeably.

### 5.3 Baselines and attribution

| Condition | Ontology context | Intervention | Interpretation |
| --- | --- | --- | --- |
| A | Absent | None | Descriptive prior-world behavior |
| B | Plain full rules | None | Ordinary ontology prompting |
| C | Structured full rules | None | Strong prompt baseline |
| C+V | Identical to C | Current version direction | Primary effect of steering |
| C+old | V2, identical to C | V1 direction | Stale-vector cost |
| C+random | Identical to C | Random unit direction, matched norm | Perturbation specificity |
| C+zero | Identical to C | Zero coefficient | Dev grid and hook/no-op check |

Only C+V versus C isolates the incremental intervention under the same prompt. A favorable C+V versus A comparison could be entirely explained by context. Optional retrieval D, grammar-constrained decoding, and simulator-filtered systems are strong practical extensions, but are not implemented empirical baselines in this release. Their absence bounds the eventual system-level competitiveness claim.

The implemented version analysis compares current V2 and stale V1 directions under V2 context. A full two-context-by-two-vector matrix, including V2-on-V1, is a planned follow-up rather than an implemented condition. The primary V2 current/stale comparison uses the same layer, coefficient, and current-version magnitude scale, preventing differences in vector norm from becoming a false adaptation effect. Also report C in V2. Random controls use fixed seeds and the same norm; three seeds are a diagnostic with limited coverage.

### 5.4 Selection, outcomes, and statistical analysis

Select on development family-macro operational success subject to at most 5 percentage-point point-estimate losses in ordinary feasible-task success and unknown recognition relative to C. Prefer the smaller coefficient in ties; retain zero when no admissible positive coefficient improves the criterion. Freeze all selection inputs and the chosen configuration before test inference.

The primary outcome is operational success: correct status and ontology adherence, with executable goal completion additionally required for feasible cases. Report its paired C+V-minus-C difference, macro-averaged over scenario families. Status accuracy is a diagnostic. Secondary measures are concept-status accuracy, schema validity, executable feasible-goal success, illegal/undefined action incidence, and false rejection. Report V2 temporal feasible-task success separately. An incorrect "infeasible" answer on a feasible task scores as failure; an empty plan cannot count as task success when actions are required. Malformed outputs remain in denominators.

Use 10,000 paired family-cluster bootstrap replicates with a recorded seed. Preserve instances, conditions, and versions within sampled families. Provide every family effect, micro averages, denominators, and intervals. The temporal feasible test stratum has only one family, so family bootstrap intervals there are degenerate and cannot establish temporal generalization uncertainty. Report descriptive within-family rates. Few structural families limit coverage and interval stability; many numeric variants cannot create independent structural replication. Secondary sampling runs with seeds 11, 29, and 47 are nested within cases and do not increase the family count. Multiplicity beyond the primary contrast is reported as exploratory unless a separate plan is frozen.

Semantic interference is operationalized as an executable use of a prohibited or undefined capability. Mentioning such a concept in an explanation is not itself a violation. Free-text claims outside the action schema require blinded human annotation; they are not fully certified by the symbolic evaluator. A later annotation study should double-code a stratified sample, report agreement and disagreements, and avoid treating an LLM judge as ground truth.

### 5.5 Local implementation and feasibility

The initial model is Qwen2.5-1.5B-Instruct at an immutable recorded revision. PyTorch decoder-block forward hooks expose the required residual tensors; Transformers supplies tokenization and generation. MPS is the preferred Apple Silicon device, with CPU fallback and recorded dtype. The inspected M4 Max host has 48 GiB unified memory. Approximately 1.5 billion FP16 parameters alone occupy 3 GB; context, runtime, and cache overhead must be measured separately.

Ordinary inference support does not imply arbitrary activation modification. Hook tests must verify the block-output tensor shape, exact changed positions, preserved surrounding outputs, hook removal, zero-coefficient equivalence, and actual cached generation on a tiny model. These checks establish implementation behavior, not steering effectiveness in the target model.

A weekend study should begin with a small technical smoke and measured throughput. Estimate full runtime from observed tokens per second before committing to the grid. The code does not train model weights or sparse autoencoders. MLX may be a useful later port but is not silently substituted for the verified PyTorch hook mechanism. No claim of target-model speed or memory performance is made before measurement.

## 6. Results: model experiments pending

No model-performance experiment is reported in this version. There are no measured adherence gains, planning improvements, adaptation scores, or throughput claims. Symbolic evaluator tests and hook tests, when present in the release validation record, verify software and reference semantics only. They do not supply evidence for H1-H5.

The eventual results should include condition-by-version status accuracy, executable success, unknown recognition, temporal success, illegal-action rates, and paired intervals. Publish all selected and rejected development candidates and the frozen test selection. A result in which no admissible positive coefficient beats C is a valid outcome and should remain visible. Tables of hypothetical numerical improvements are deliberately absent.

## 7. Discussion: prospective interpretation

If the current-version direction exceeds C on held-out families while preserving feasible reasoning and unknown recognition, the study would support a bounded behavioral effect for this model, ontology, extraction policy, and intervention schedule. A matched random control is needed to distinguish the learned direction from nonspecific perturbation. Cross-version performance would show whether separately learned vectors can be selected without over-suppressing new abilities, not whether arbitrary ontology updates automatically yield valid vectors.

If classification improves while executable planning does not, the safer explanation is improved surface compliance. If V1 steering harms V2 temporal success and V2 steering only returns it to C's level, the contribution is evidence of stale steering risk. If a larger or more conditional method is needed, the small static experiment still defines a reproducible failure boundary. Probe separability, if later added, is not equivalent to causal necessity or sufficiency.

The study cannot show that the model stops representing or "thinking about" forbidden magic. Nor does operational consistency imply factual correctness, authority, or a guarantee of containment. A symbolic post-validator can enforce the executable subset more directly. Steering is useful only if measured benefits justify its complexity or improve properties beyond that validator's scope.

## 8. Limitations and follow-up studies

The first benchmark is small, synthetic, and generated from a shared grammar. Structural family holdout is stronger than random instance splitting, but remains a limited generalization test. Independent scenario writers, more held-out families, paraphrase controls, distractor lore, and longer compositions are required before broad claims. Ontology wording may correlate with version selection, so isolate explicit version names from rule content in later controls.

The training endpoints contain labels and differing action tokens; surface leakage and generic refusal remain plausible. The undefined echo_matter operation occurs in training negatives and held-out unknown cases; separate recognition of seen and unseen undefined names before claiming unknown-concept generalization. A single linear direction can entangle multiple constraints. Final-response activation readout may be poorly aligned with the token states where plans are generated. Layer and coefficient sweeps create selection pressure; development-only freezing reduces, but does not erase, researcher degrees of freedom. Small family counts weaken uncertainty estimates.

Only one small model is the initial target. A positive result should be replicated on another 1B-3B model and a second causal ontology before testing larger systems. Compare CAA-style vectors with CAST/K-CAST, action-specific subspaces, projection, and symbolic constrained generation under matched resource budgets. Larger representations and sparse features are follow-ups, not prerequisites for the pilot. A negative result should trigger alternative readout, pair design, or nonlinear interventions without rewriting the original test as successful.

## 9. Reproducibility, authorship, and release status

The repository includes ontology versions, generator, symbolic evaluator, steering runtime, prospective analysis plan, related-work audit, and publication metadata. Preserve the source commit, model revision, dependency versions, data hashes, vector construction records, frozen selection, and raw output logs in any experimental release. The Zenodo upload package contains this protocol PDF and a source archive; it has no invented DOI or completed experimental data.

AI assistance was used to search and organize literature, draft text, and implement software. The named human author remains responsible for reviewing sources, validating claims, resolving authorship and licensing, and approving any publication. The author name follows the authenticated GitHub profile; affiliation and ORCID are intentionally unspecified pending author confirmation.

Code is distributed under MIT; manuscript and documentation under CC BY 4.0. No funding source, ethics approval, competing-interest declaration, peer review, or institutional affiliation is fabricated. This document is a research-protocol preprint and should be deposited with that status clearly stated.

## References

[R01] Mark Russinovich. 2026. *CounterSteer: Suppressing Indirect Prompt Injection with Activation Steering.* arXiv:2609.36570v1. https://arxiv.org/abs/2609.36570v1

[R02] Nina Rimsky et al. 2024. *Steering Llama 2 via Contrastive Activation Addition.* ACL. https://aclanthology.org/2024.acl-long.828/

[R03] Alexander Matt Turner et al. *Activation Addition: Steering Language Models Without Optimization.* https://arxiv.org/abs/2308.10248

[R04] Andy Zou et al. 2023. *Representation Engineering: A Top-Down Approach to AI Transparency.* https://arxiv.org/abs/2310.01405

[R05] Bruce W. Lee et al. 2025. *Programming Refusal with Conditional Activation Steering.* ICLR. https://arxiv.org/abs/2409.05907v3

[R06] Marco Valentino, Geonhee Kim, Dhairya Dalal, Zhixue Zhao, and Andre Freitas. 2026. *Mitigating Content Effects on Reasoning in Language Models through Fine-Grained Activation Steering.* AAAI; arXiv:2505.12189v3. https://arxiv.org/abs/2505.12189v3

[R07] Kinshuk Vasisht, Navreet Kaur, and Danish Pruthi. 2025. *Knowledge Graph Guided Evaluation of Abstention Techniques.* NAACL, pp. 6921-6939. https://aclanthology.org/2025.naacl-long.353/

[R18] Abulhair Saparov and He He. 2023. *Language Models Are Greedy Reasoners: A Systematic Formal Analysis of Chain-of-Thought.* ICLR. https://arxiv.org/abs/2210.01240

[R19] Oyvind Tafjord, Bhavana Dalvi, and Peter Clark. 2021. *ProofWriter: Generating Implications, Proofs, and Abductive Statements over Natural Language.* Findings of ACL. https://aclanthology.org/2021.findings-acl.317/

[R20] Youssef Benchekroun et al. *WorldSense: A Synthetic Benchmark for Grounded Reasoning in Large Language Models.* https://arxiv.org/abs/2311.15930

[R22] Kevin Meng et al. 2022. *Locating and Editing Factual Associations in GPT.* NeurIPS. https://arxiv.org/abs/2202.05262

[R30] Antonio Morandi. 2026. *Epistemological Coherence in Large Language Models: The Compound Problem of Grammatical-Ontological and Epistemological Contamination in AI Knowledge Representation.* Author-hosted preprint; section 7.2 proposes ontology-framing steering. https://www.ayurvedicpoint.it/images/pdf/EC_LLM_V2.pdf

[R32] *Circuit-level Steering for Personalized Knowledge Injection in Language Models.* ICLR 2026 anonymous submission; author identity and decision unconfirmed in the retrieved primary record. https://openreview.net/pdf/69c979c667564ad900737b8c64ed13022ec74bfd.pdf

[R33] Oliver Steele, Jiangtao Wen, and Yuxing Han. 2026. *One Mechanism for Many Mental Spaces: A Shared Router over a Value Slot in Language Models.* https://arxiv.org/abs/2607.10248

[R38] Jiaran Ye et al. 2026. *Where Steering Signals Come From: Activation Source Selection in Activation Steering.* https://arxiv.org/abs/2607.25270

[R39] Zhiwei Gao, Shaowen Peng, Shoko Wakamiya, and Eiji Aramaki. 2026. *What Does Activation Steering Control? Attribution Across Answer Encodings and Output-Sensitive Subspaces.* https://arxiv.org/abs/2608.22985

The expanded reference inventory, verification notes, and competing-method analysis are in references.md and research/related-work.md. Reference numbers are stable repository identifiers rather than consecutive manuscript numbering.
