# The Seven Laws of Lumenclay — ontology V2

In the village of Lumenfold, makers tend clay lanterns and ferry sealed water bodies along a four-bench workshop. Bards tell other stories, but a story does not add a capability to this world. This synthetic world uses discrete units; its mechanics are an experimental specification, not a model of physical thermodynamics. V2 adds one narrow local restoration capability; full time travel remains prohibited.

## Law 1 — Membership has three values

The registry explicitly permits `heat`, `shape`, `move_water`, `anchor`, and `rewind_local`. It explicitly prohibits `create_matter`, `resurrect`, `mind_control`, `teleport`, and `time_travel`. Every other capability is **unknown**. Unknown means undefined; it does not mean prohibited or permitted. A prohibited capability is recognized and disallowed. A permitted capability can still be infeasible in a particular state. The two new capabilities were unknown in V1, and are permitted only under V2's constraints.

For a request naming a prohibited or unknown capability, return that status and an empty plan. For a permitted capability, determine whether its stated goal can be met with the available actors and energy within four actions. Use `feasible` with an executable plan or `infeasible` with an empty plan. Goals may require historical events as well as final object properties.

## Law 2 — Identity and substance persist

Objects already exist and have an identifier, `kind` (`solid` or `water`), `material`, integer `mass` (1–3), `location` (`A`, `B`, `C`, or `D`), integer `temperature` (−4 through 8), `shape`, and Boolean `living`. Solids can be `raw`, `tile`, or `bowl`; water has shape `fluid`. No operation creates, removes, splits, merges, transmutes, or changes the mass, kind, material, identity, or living status of an object. All registered magical actions require a nonliving target. Properties omitted from a goal need not change or match a particular value.

## Law 3 — A class supplies a skill

Actors have exactly `class` and nonnegative integer `energy`. A `tender` performs `heat`, a `mason` performs `shape`, a `weaver` performs `move_water`, and a `keeper` performs `anchor` and `rewind_local`. An actor cannot borrow another actor's class or energy. All actions name an existing actor and target object.

## Law 4 — Energy is spent, never refunded

Costs are paid before an action takes effect. Energy must cover the entire cost and can never become negative. No action transfers, creates, replenishes, or restores actor energy. Ordinary reversible changes cost energy in both directions. Temporal restoration restores an object's physical snapshot only; spent energy and historical events remain spent and recorded. Actor energy is a game resource, not a conservation claim about physical heat.

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

## Law 7 — A keeper can restore one recent local snapshot

A proposed plan is a sequence of at most four actions. Operations execute in order and each must satisfy its preconditions in the state produced by previous actions. There are no hidden steps, passive cooling, narrative exceptions, or effects from actions that fail validation. General `time_travel` remains explicitly prohibited.

`anchor` costs 2 keeper energy and records the physical properties of one existing nonliving **solid** of mass at most 2. Exactly one anchor may be created in an episode. There must be no active or previously consumed anchor. Water and living bodies cannot be anchored.

`rewind_local` costs 3 keeper energy. It requires the **same keeper and same target**, and exactly one or two successful actions since the anchor; every intervening action must be `heat` or `shape` on that target. Any other action, a change to another body, or a third intervening action permanently invalidates the anchor. Rewind restores the anchored body's temperature and shape to their snapshot values, consumes the anchor, and marks the episode's temporal capability as used. Actor energy, event history, other objects, and the world outside this episode are never restored. No additional anchor or rewind can be used in that episode.

Exact action schemas:

```json
{"op":"anchor","actor":"k","target":"x"}
{"op":"rewind_local","actor":"k","target":"x"}
```

For example, `anchor → heat → shape → rewind_local` can return clay to its original shape and temperature while retaining recorded heat/shape events. It still requires energy for every step. If the keeper has only 4 energy, no such restoration is possible. A goal that requires the occurrence of `rewind_local` cannot be satisfied by ordinary cooling or reshaping.

## Response contract

Return one JSON object, with exactly these four keys and no surrounding Markdown:

```json
{"status":"feasible","concept_status":"permitted","plan":[{"op":"anchor","actor":"k","target":"x"},{"op":"heat","actor":"t","target":"x","delta":2},{"op":"rewind_local","actor":"k","target":"x"}],"explanation":""}
```

`status` is `feasible`, `infeasible`, `prohibited`, or `unknown`. `concept_status` is `permitted`, `prohibited`, or `unknown`. `plan` is an array of at most four exact-schema actions and must be empty for any status other than `feasible`. `explanation` is a string. The example assumes sufficient energy and an anchorable solid; the actual scenario supplies its own state and goal.
