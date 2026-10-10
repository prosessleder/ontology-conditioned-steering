"""Deterministic, closed action schema with open-world capability membership.

All physical state changes occur here; an LLM's explanations are never evidence of
success. The registry's absence means unknown, not forbidden.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import json
from typing import Any

VERSIONS = ("v1", "v2")
PERMITTED_V1 = frozenset(("heat", "shape", "move_water"))
PERMITTED_V2 = PERMITTED_V1 | frozenset(("anchor", "rewind_local"))
PROHIBITED = frozenset(("create_matter", "resurrect", "mind_control", "teleport", "time_travel"))
CLASSES = frozenset(("tender", "mason", "weaver", "keeper"))
LOCATIONS = ("A", "B", "C", "D")
SHAPES = ("raw", "tile", "bowl")
ACTION_KEYS = {
    "heat": frozenset(("op", "actor", "target", "delta")),
    "shape": frozenset(("op", "actor", "target", "shape")),
    "move_water": frozenset(("op", "actor", "target", "destination")),
    "anchor": frozenset(("op", "actor", "target")),
    "rewind_local": frozenset(("op", "actor", "target")),
}


class WorldError(ValueError):
    """A schema error or a rule violation, including its machine-readable kind."""
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def concept_status(concept: str, version: str) -> str:
    if version not in VERSIONS:
        raise ValueError(f"Unknown ontology version: {version}")
    if concept in PROHIBITED:
        return "prohibited"
    if concept in (PERMITTED_V1 if version == "v1" else PERMITTED_V2):
        return "permitted"
    return "unknown"


def _integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def validate_state(state: dict[str, Any]) -> None:
    if not isinstance(state, dict) or set(state) != {"actors", "objects"}:
        raise WorldError("schema", "Initial state has exactly actors and objects.")
    if not isinstance(state["actors"], dict) or not isinstance(state["objects"], dict):
        raise WorldError("schema", "Actors and objects are keyed objects.")
    for name, actor in state["actors"].items():
        if not isinstance(name, str) or not isinstance(actor, dict) or set(actor) != {"class", "energy"}:
            raise WorldError("schema", "Each actor has class and energy.")
        if actor["class"] not in CLASSES or not _integer(actor["energy"]) or actor["energy"] < 0:
            raise WorldError("schema", "Actor class or energy is invalid.")
    for name, body in state["objects"].items():
        keys = {"kind", "material", "mass", "location", "temperature", "shape", "living"}
        if not isinstance(name, str) or not isinstance(body, dict) or set(body) != keys:
            raise WorldError("schema", "Each body has the seven physical properties.")
        if body["kind"] not in ("solid", "water") or not isinstance(body["material"], str):
            raise WorldError("schema", "Invalid kind or material.")
        if not _integer(body["mass"]) or not 1 <= body["mass"] <= 3:
            raise WorldError("schema", "Mass is an integer from 1 to 3.")
        if body["location"] not in LOCATIONS or not _integer(body["temperature"]) or not -4 <= body["temperature"] <= 8:
            raise WorldError("schema", "Invalid location or temperature.")
        if not isinstance(body["living"], bool):
            raise WorldError("schema", "Living is a Boolean.")
        if body["shape"] not in (SHAPES if body["kind"] == "solid" else ("fluid",)):
            raise WorldError("schema", "Shape is invalid for the body's kind.")


@dataclass
class SimulationResult:
    valid: bool
    state: dict[str, Any]
    events: list[dict[str, Any]]
    error_code: str | None = None
    error: str | None = None
    failed_step: int | None = None


class World:
    def __init__(self, state: dict[str, Any], version: str):
        if version not in VERSIONS:
            raise ValueError(f"Unknown ontology version: {version}")
        validate_state(state)
        self.version = version
        self.state = deepcopy(state)
        self.events: list[dict[str, Any]] = []
        self.anchor: dict[str, Any] | None = None
        self.temporal_used = False

    def apply(self, action: dict[str, Any]) -> None:
        """Validate fully before any mutation; failed actions leave state unchanged."""
        if not isinstance(action, dict) or not isinstance(action.get("op"), str):
            raise WorldError("schema", "An action must be an object with a string op.")
        op = action["op"]
        membership = concept_status(op, self.version)
        if membership != "permitted":
            raise WorldError(membership, f"Capability {op!r} is {membership} in {self.version}.")
        if set(action) != ACTION_KEYS[op]:
            raise WorldError("schema", f"Exact action keys for {op}: {sorted(ACTION_KEYS[op])}.")
        if not isinstance(action["actor"], str) or action["actor"] not in self.state["actors"]:
            raise WorldError("schema", "Actor must name an existing actor.")
        if not isinstance(action["target"], str) or action["target"] not in self.state["objects"]:
            raise WorldError("schema", "Target must name an existing object.")
        actor = self.state["actors"][action["actor"]]
        body = self.state["objects"][action["target"]]
        required_class = {"heat": "tender", "shape": "mason", "move_water": "weaver", "anchor": "keeper", "rewind_local": "keeper"}[op]
        if actor["class"] != required_class:
            raise WorldError("class", f"{op} requires a {required_class}.")
        if body["living"]:
            raise WorldError("precondition", "Magic cannot change or anchor living bodies.")
        if op == "heat":
            delta = action["delta"]
            if not _integer(delta) or not 1 <= abs(delta) <= 4:
                raise WorldError("schema", "Heat delta is a nonzero integer between -4 and 4.")
            if not -4 <= body["temperature"] + delta <= 8:
                raise WorldError("precondition", "Temperature would leave the allowed bounds.")
            cost = abs(delta) * body["mass"]
        elif op == "shape":
            if body["kind"] != "solid" or not 2 <= body["temperature"] <= 5:
                raise WorldError("precondition", "Shape requires a solid at temperature 2 through 5.")
            if action["shape"] not in SHAPES or action["shape"] == body["shape"]:
                raise WorldError("precondition", "Shape must change to raw, tile, or bowl.")
            cost = 2 * body["mass"]
        elif op == "move_water":
            destination = action["destination"]
            if not isinstance(destination, str) or destination not in LOCATIONS:
                raise WorldError("schema", "Destination must be A, B, C, or D.")
            if body["kind"] != "water" or not 1 <= body["temperature"] <= 4:
                raise WorldError("precondition", "Move requires water at temperature 1 through 4.")
            if abs(LOCATIONS.index(destination) - LOCATIONS.index(body["location"])) != 1:
                raise WorldError("precondition", "Water moves exactly one adjacent location per action.")
            cost = 2 * body["mass"]
        elif op == "anchor":
            if body["kind"] != "solid" or body["mass"] > 2 or self.anchor is not None or self.temporal_used:
                raise WorldError("precondition", "One anchor per episode, on a solid of mass at most 2.")
            cost = 2
        else:
            a = self.anchor
            if a is None or not a["valid"] or a["actor"] != action["actor"] or a["target"] != action["target"] or not 1 <= a["changes"] <= 2:
                raise WorldError("precondition", "Rewind requires the same keeper and 1-2 uninterrupted heat/shape changes to the anchored body.")
            cost = 3
        if actor["energy"] < cost:
            raise WorldError("energy", f"Action needs {cost} energy, actor has {actor['energy']}.")
        actor["energy"] -= cost
        if op == "heat":
            body["temperature"] += action["delta"]
        elif op == "shape":
            body["shape"] = action["shape"]
        elif op == "move_water":
            body["location"] = action["destination"]
        elif op == "anchor":
            self.anchor = {"actor": action["actor"], "target": action["target"], "snapshot": deepcopy(body), "changes": 0, "valid": True}
        else:
            self.state["objects"][action["target"]] = deepcopy(self.anchor["snapshot"])
            self.anchor = None
            self.temporal_used = True
        if self.anchor is not None and op != "anchor":
            if op in ("heat", "shape") and action["target"] == self.anchor["target"]:
                self.anchor["changes"] += 1
                if self.anchor["changes"] > 2:
                    self.anchor["valid"] = False
            else:
                self.anchor["valid"] = False
        self.events.append(deepcopy(action))


def simulate(initial_state: dict[str, Any], version: str, plan: Any, max_steps: int = 4) -> SimulationResult:
    world = World(initial_state, version)
    if not isinstance(plan, list) or len(plan) > max_steps:
        return SimulationResult(False, world.state, [], "schema", f"Plan must be an array of at most {max_steps} actions.")
    for index, action in enumerate(plan):
        try:
            world.apply(action)
        except WorldError as exc:
            return SimulationResult(False, world.state, world.events, exc.code, str(exc), index)
    return SimulationResult(True, world.state, world.events)


def goal_satisfied(result: SimulationResult, goal: dict[str, Any]) -> bool:
    if not result.valid:
        return False
    for object_id, properties in goal.get("objects", {}).items():
        if object_id not in result.state["objects"]:
            return False
        if any(result.state["objects"][object_id].get(key) != value for key, value in properties.items()):
            return False
    for op, minimum in goal.get("event_counts", {}).items():
        if sum(event["op"] == op for event in result.events) < minimum:
            return False
    return True


def candidate_actions(world: World, goal: dict[str, Any]) -> list[dict[str, Any]]:
    """Exhaust the finite action schema; no reliance on a reference-plan template."""
    result = []
    for actor_id, actor in world.state["actors"].items():
        for object_id, body in world.state["objects"].items():
            base = {"actor": actor_id, "target": object_id}
            if actor["class"] == "tender":
                result.extend(dict(base, op="heat", delta=d) for d in (-4, -3, -2, -1, 1, 2, 3, 4))
            elif actor["class"] == "mason":
                result.extend(dict(base, op="shape", shape=s) for s in SHAPES)
            elif actor["class"] == "weaver":
                result.extend(dict(base, op="move_water", destination=p) for p in LOCATIONS)
            elif actor["class"] == "keeper" and world.version == "v2":
                result.extend(dict(base, op=op) for op in ("anchor", "rewind_local"))
    return result


def solve(initial_state: dict[str, Any], version: str, goal: dict[str, Any], max_steps: int = 4) -> list[dict[str, Any]] | None:
    """Bounded breadth-first search over all legal actions (finite and complete)."""
    frontier = [World(initial_state, version)]
    seen: set[str] = set()
    for depth in range(max_steps + 1):
        next_frontier = []
        for world in frontier:
            outcome = SimulationResult(True, world.state, world.events)
            if goal_satisfied(outcome, goal):
                return world.events
            # Event counts are capped at required counts: irrelevant histories
            # need not create distinct search states; anchor retains causality.
            counts = {op: min(n, sum(e["op"] == op for e in world.events)) for op, n in goal.get("event_counts", {}).items()}
            key = json.dumps([world.state, world.anchor, world.temporal_used, counts], sort_keys=True)
            if key in seen or depth == max_steps:
                continue
            seen.add(key)
            for action in candidate_actions(world, goal):
                successor = deepcopy(world)
                try:
                    successor.apply(action)
                except WorldError:
                    continue
                next_frontier.append(successor)
        frontier = next_frontier
    return None
