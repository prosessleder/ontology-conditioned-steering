# Dataset design and leakage controls

The executable generator is `src/ontology_steering/dataset.py`; simulator rules are in `world.py`. Default seed 1729 and `per_family=12` generate **720 cases**, equally divided into 240 train, 240 development, and 240 test cases. These are benchmark inputs, not measured model outputs.

## Two distinct evaluation slices

The **core slice** contains 576 cases: six structural families × twelve instances per label × four labels × two ontology versions. Within every family and version, `feasible`, `infeasible`, `prohibited`, and `unknown` have equal counts. The same core case is evaluated under V1 and V2; its label is unchanged.

The **adaptation slice** contains 144 cases: three temporal structural families × twelve instances × two feasibility settings × two versions. A V1 temporal request is `unknown`; the matched V2 request is either `feasible` or `infeasible`. Thus this slice is intentionally **not label balanced across versions**: 72 V1 unknown, 36 V2 feasible, and 36 V2 infeasible. Analyze it separately. A pooled accuracy would hide the distinction between recognizing a newly defined concept and executing it successfully.

## Structural holdout

| Split | Core families | Temporal family | Required feasible plan lengths |
|---|---|---|---|
| Train | `heat_shape`, `warm_transport` | `rewind_heat` | 2, 2, 3 |
| Development | `shape_then_cool`, `two_hop_transport` | `rewind_shape` | 3, 3, 3 |
| Test | `mixed_delivery`, `transport_then_reseal` | `rewind_heat_shape` | 4, 4, 4 |

A family belongs to exactly one split. Holdout concerns **compositions of shared primitives**: test combines separate-object transformations or extends water transport with restoration of temperature; test temporal restoration combines two intervening changes. It does not hold out all primitive actions, character classes, or operation tokens. This is a deliberately modest compositional generalization test.

Instances vary mass, initial temperature, target form, transport direction, and energy margin. The generator uses fixed actor/object identifiers to avoid a naming task. Initial heat deltas and resource costs vary with causal quantities. It adds direct phrasing, a paraphrase, or descriptive distracting folklore according to the instance index, with all variants retained in the family's split. The distractor mentions other-world teleportation and century-scale rewind; it issues no instruction to override the ontology. Styles are matched between ontology versions. Paraphrase/distractor robustness is secondary because it co-varies with numeric instances; this release does not provide a fully crossed clean-versus-distractor intervention for every world state.

## Objective labels

Every feasible reference plan is executed and checked against final object properties and minimum event counts. Ordinary plans require two to four actions. Temporal goals require an actual `rewind_local` event, so ordinary cooling cannot be mistaken for successful temporal execution.

Every core infeasible case differs from a feasible instance in one class actor's energy. A checked lower-bound certificate proves insufficient energy: required shaping costs at least `2 * mass`, required transport costs at least `2 * mass * graph_distance`, and any rewind costs its sole keeper at least 2 + 3 = 5. These certificates are valid because no action changes class, transfers energy, or replenishes energy. Temporal infeasible instances cycle through four constraints: keeper energy 4; mass 3 exceeding the anchor cap; a living target; or absence of any keeper (the nominal keeper has tender class). Additional checked certificates prove no anchorable object or no keeper exists. With default n=12 there are nine V2 infeasible cases per boundary type across the three splits. A bounded exhaustive solver enumerates the finite action schema independently; unit tests check a feasible and infeasible instance of every family against it. The generator validates every certificate and every feasible reference; it does not run exhaustive search on all 720 cases. Temporal zero/third/interrupted change, wrong-keeper identity, and anchor reuse are simulator unit tests; they are not distinct model-evaluation slices in this release.

Prohibited requests cycle through explicit matter creation, teleportation, and general time travel. Unknown requests cycle through undefined shadow weaving, song binding, and matter echo. These categories share otherwise matched state/goal fields. They require empty plans and correct membership/status, even if the underlying physical goal could be achieved using a different registered capability: the task first asks for the status of the named capability.

## Contrastive training pairs

The preferred **`pairs-common.jsonl`** contains 48 training pairs, 24 per ontology version, from the same ordinary feasible train instances. Each pair compares a reference plan with one of four negative types, evenly distributed in the default common set: an operation replaced by explicit `time_travel`; an operation replaced by undefined `echo_matter`; one actor replaced by an actor of the wrong class; or the first two actions reversed so their preconditions fail. The last two types contain only registered operation tokens, challenging a pure forbidden-word detector. Answer fields and empty explanations remain identical; word count and syntax are matched, though tokenization lengths can differ for operation replacements. Version counterparts use the **same corruption**, so pair count, scenario composition, and answer text are matched across V1 and V2. Only the ontology prompt changes.

Half the primary contrasts necessarily change operation tokens; the others alter actor binding or causal order. This is not a perfectly surface-controlled test of a latent compatibility concept. It might learn operation-token associations, role bindings, positional heuristics, or output formatting. Independent executable task evaluation and the unseen temporal/4-step compositions test whether any benefit extends beyond training contrasts. Directions collected from completed gold responses are not evidence about the model's spontaneous reasoning trajectories. Negative-control vectors and nonzero-versus-zero interventions are essential.

The optional **`pairs.jsonl`** contains 60 pairs: the 48 common pairs plus twelve V2 feasible `rewind_heat` pairs. V1 has 24 and V2 36 pairs in this file. It is an **exploratory extension** that changes sample composition and exposes the V2 temporal operator in positive examples. Use it only as a separately reported ablation; comparing its V1/V2 vectors cannot isolate ontology-context adaptation. The primary version-transfer analysis uses the common file and evaluates temporal generalization without temporal training examples.

No test family, answer, or activation may be used to construct a vector or select a layer/coefficient. Development data select the intervention once; preserve the selection record before test inference. Matched V1/V2 cases and repeated seeds remain clustered observations rather than independent evidence.

## Schema and commands

Each case includes `id`, `pair_id`, `family_id`, `split`, `slice`, `ontology_version`, `style`, `question`, `initial_state`, `goal`, `requested_concept`, `max_steps`, `boundary_type`, `expected_status`, `expected_concept_status`, `reference_plan`, and an optional checked `infeasibility_certificate`. Only question/state/goal/requested concept are rendered as task inputs; expected fields and reference plans must never enter model prompts.

```sh
PYTHONPATH=src python3 -m ontology_steering.dataset --output data --seed 1729 --per-family 12
```

This writes `train.jsonl`, `dev.jsonl`, `test.jsonl`, both pair files, and `manifest.json`. The manifest states counts and the family assignment. Hash input files, ontology text, model configuration, vectors, and selection records in run provenance. The dataset generator and symbolic evaluator use only the Python standard library.
