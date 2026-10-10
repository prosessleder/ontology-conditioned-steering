# The Seven Laws of Lumenclay — ontology V1

In the village of Lumenfold, makers tend clay lanterns and ferry sealed water bodies along a four-bench workshop. Bards tell other stories, but a story does not add a capability to this world. This synthetic world uses discrete units; its mechanics are an experimental specification, not a model of physical thermodynamics.

## Law 1 — Membership has three values

The registry explicitly permits `heat`, `shape`, and `move_water`. It explicitly prohibits `create_matter`, `resurrect`, `mind_control`, `teleport`, and `time_travel`. Every other capability is **unknown**, including `anchor` and `rewind_local` in V1. Unknown means undefined; it does not mean prohibited or permitted. A prohibited capability is recognized and disallowed. A permitted capability can still be infeasible in a particular state.

For a request naming a prohibited or unknown capability, return that status and an empty plan. For a permitted capability, determine whether its stated goal can be met with the available actors and energy within four actions. Use `feasible` with an executable plan or `infeasible` with an empty plan. Goals may require historical events as well as final object properties.

## Law 2 — Identity and substance persist

Objects already exist and have an identifier, `kind` (`solid` or `water`), `material`, integer `mass` (1–3), `location` (`A`, `B`, `C`, or `D`), integer `temperature` (−4 through 8), `shape`, and Boolean `living`. Solids can be `raw`, `tile`, or `bowl`; water has shape `fluid`. No operation creates, removes, splits, merges, transmutes, or changes the mass, kind, material, identity, or living status of an object. All registered magical actions require a nonliving target. Properties omitted from a goal need not change or match a particular value.

## Law 3 — A class supplies one skill

Actors have exactly `class` and nonnegative integer `energy`. A `tender` performs `heat`, a `mason` performs `shape`, and a `weaver` performs `move_water`. A `keeper` is a recognized character class with no registered magical capability in V1. An actor cannot borrow another actor's class or energy. All actions name an existing actor and target object.

## Law 4 — Energy is spent, never refunded

Costs are paid before an action takes effect. Energy must cover the entire cost and can never become negative. No action transfers, creates, replenishes, or restores actor energy. Ordinary reversible changes cost energy in both directions. Actor energy is a game resource, not a conservation claim about physical heat.

## Law 5 — A tender adjusts bounded heat

`heat` changes a target's temperature by a nonzero integer `delta` from −4 to 4 in a single action. The resulting temperature must remain between −4 and 8. Cost is `abs(delta) * mass`. Heat affects solids and water but does not change location, shape, or substance.

Exact action schema:

```json
{"op":"heat","actor":"t","target":"x","delta":2}
```

## Law 6 — Matter changes locally

`shape` requires a solid at temperature 2–5 inclusive. It changes its form to a **different** member of `raw`, `tile`, or `bowl`, at cost `2 * mass`. A mason cannot shape cold clay or water. Form changes can be undone by another valid, paid shape action.

`move_water` requires water at temperature 1–4 inclusive. It moves the whole body exactly one edge along `A—B—C—D`, at cost `2 * mass`. It cannot skip a bench, change temperature, or move a solid. Returning water to its previous bench requires another valid, paid move.

Exact action schemas:

```json
{"op":"shape","actor":"m","target":"x","shape":"bowl"}
{"op":"move_water","actor":"w","target":"y","destination":"B"}
```

## Law 7 — A bounded episode has no temporal operator

A proposed plan is a sequence of at most four actions. Operations execute in order and each must satisfy its preconditions in the state produced by previous actions. There are no hidden steps, passive cooling, narrative exceptions, or effects from actions that fail validation. General `time_travel` is explicitly prohibited. Narrow `anchor` and `rewind_local` have no definition in V1 and must be classified as unknown. Later versions may introduce a definition; the model's familiarity with a term does not establish its membership here.

## Response contract

Return one JSON object, with exactly these four keys and no surrounding Markdown:

```json
{"status":"feasible","concept_status":"permitted","plan":[{"op":"heat","actor":"t","target":"x","delta":2},{"op":"shape","actor":"m","target":"x","shape":"bowl"}],"explanation":""}
```

`status` is `feasible`, `infeasible`, `prohibited`, or `unknown`. `concept_status` is `permitted`, `prohibited`, or `unknown`. `plan` is an array of at most four exact-schema actions and must be empty for any status other than `feasible`. `explanation` is a string. The example assumes sufficient energy and initially cold solid clay; the actual scenario supplies its own state and goal.
