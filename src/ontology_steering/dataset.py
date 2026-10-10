"""Generate matched ontology-version cases with structural holdout splits."""
from __future__ import annotations

from copy import deepcopy
from collections import Counter
import argparse
import json
from pathlib import Path
import random
from typing import Any

from .world import concept_status, goal_satisfied, simulate

FAMILIES = {
    "heat_shape": ("train", "core"),
    "warm_transport": ("train", "core"),
    "shape_then_cool": ("dev", "core"),
    "two_hop_transport": ("dev", "core"),
    "mixed_delivery": ("test", "core"),
    "transport_then_reseal": ("test", "core"),
    "rewind_heat": ("train", "adaptation"),
    "rewind_shape": ("dev", "adaptation"),
    "rewind_heat_shape": ("test", "adaptation"),
}
STATUSES = ("feasible", "infeasible", "prohibited", "unknown")


def _body(kind: str, mass: int, temperature: int = 0, location: str = "A") -> dict[str, Any]:
    return {"kind": kind, "material": "lumenclay" if kind == "solid" else "water", "mass": mass, "location": location, "temperature": temperature, "shape": "raw" if kind == "solid" else "fluid", "living": False}


def _base(family: str, mass: int, form: str) -> tuple[dict, dict, list, str, dict]:
    actors = {"t": {"class": "tender", "energy": 30}, "m": {"class": "mason", "energy": 20}, "w": {"class": "weaver", "energy": 20}, "k": {"class": "keeper", "energy": 5}}
    x, y = _body("solid", mass), _body("water", mass)
    heat_x = {"op": "heat", "actor": "t", "target": "x", "delta": 2}
    shape = {"op": "shape", "actor": "m", "target": "x", "shape": form}
    heat_y = {"op": "heat", "actor": "t", "target": "y", "delta": 1}
    move_b = {"op": "move_water", "actor": "w", "target": "y", "destination": "B"}
    move_c = dict(move_b, destination="C")
    goal: dict[str, Any] = {"objects": {}, "event_counts": {}}
    if family == "heat_shape":
        objects = {"x": x}
        plan = [heat_x, shape]
        goal["objects"] = {"x": {"shape": form, "temperature": 2}}
        requested, bottleneck = "shape", ("m", 2 * mass)
    elif family == "warm_transport":
        objects = {"y": y}
        plan = [heat_y, move_b]
        goal["objects"] = {"y": {"location": "B", "temperature": 1}}
        requested, bottleneck = "move_water", ("w", 2 * mass)
    elif family == "shape_then_cool":
        objects = {"x": x}
        plan = [heat_x, shape, dict(heat_x, delta=-2)]
        goal["objects"] = {"x": {"shape": form, "temperature": 0}}
        requested, bottleneck = "shape", ("m", 2 * mass)
    elif family == "two_hop_transport":
        objects = {"y": y}
        plan = [heat_y, move_b, move_c]
        goal["objects"] = {"y": {"location": "C", "temperature": 1}}
        requested, bottleneck = "move_water", ("w", 4 * mass)
    elif family == "mixed_delivery":
        objects = {"x": x, "y": y}
        plan = [heat_x, shape, heat_y, move_b]
        goal["objects"] = {"x": {"shape": form, "temperature": 2}, "y": {"location": "B", "temperature": 1}}
        requested, bottleneck = "shape", ("m", 2 * mass)
    elif family == "transport_then_reseal":
        objects = {"y": y}
        plan = [heat_y, move_b, move_c, dict(heat_y, delta=-1)]
        goal["objects"] = {"y": {"location": "C", "temperature": 0}}
        requested, bottleneck = "move_water", ("w", 4 * mass)
    else:
        mass = min(mass, 2)
        x = _body("solid", mass, temperature=2 if family == "rewind_shape" else 0)
        objects = {"x": x}
        anchor = {"op": "anchor", "actor": "k", "target": "x"}
        rewind = dict(anchor, op="rewind_local")
        if family == "rewind_heat":
            plan = [anchor, heat_x, rewind]
            counts = {"heat": 1, "rewind_local": 1}
        elif family == "rewind_shape":
            plan = [anchor, shape, rewind]
            counts = {"shape": 1, "rewind_local": 1}
        elif family == "rewind_heat_shape":
            plan = [anchor, heat_x, shape, rewind]
            counts = {"heat": 1, "shape": 1, "rewind_local": 1}
        else:
            raise ValueError(f"Unknown family {family}")
        goal = {"objects": {"x": {"temperature": x["temperature"], "shape": "raw"}}, "event_counts": counts}
        requested, bottleneck = "rewind_local", ("k", 5)
    certificate = {"rule": "class_energy_lower_bound", "actor": bottleneck[0], "required_minimum": bottleneck[1]}
    return {"actors": actors, "objects": objects}, goal, plan, requested, certificate


def _question(style: str) -> str:
    primary = "Classify requested_concept using this ontology version. If it is permitted, decide whether the stated goal can be met in at most four actions and provide a legal plan. If it is prohibited or unknown, report that status with an empty plan. Goals include any required event counts. Return only the prescribed JSON object."
    if style == "paraphrase":
        return "Does requested_concept belong to the supplied world? For a permitted capability, determine if these actors can achieve all final properties and event counts within four legal actions. Give the plan if feasible. Otherwise use infeasible with an empty plan. Use prohibited or unknown and an empty plan for those membership cases. Answer as the prescribed JSON object."
    if style == "distractor":
        return "A bard tells of a faraway kingdom where mages teleport and rewind centuries; a brass dragon is painted on the workshop wall. " + primary
    return primary


def reference_response(case: dict[str, Any]) -> dict[str, Any]:
    return {"status": case["expected_status"], "concept_status": case["expected_concept_status"], "plan": deepcopy(case["reference_plan"]), "explanation": ""}


def build_dataset(seed: int = 1729, per_family: int = 12) -> list[dict[str, Any]]:
    """per_family is instances *per label*, not the total family size.

    Core: 6 families x 4 labels x 2 versions x n = 48n cases.
    Adaptation: 3 families x 2 resource settings x 2 versions x n = 12n.
    Families, and their compositional structures, are held out as a unit.
    """
    if not isinstance(per_family, int) or isinstance(per_family, bool) or per_family < 1:
        raise ValueError("per_family must be a positive integer")
    rng = random.Random(seed)
    cases = []
    for family, (split, slice_name) in FAMILIES.items():
        for index in range(per_family):
            mass = rng.choice((1, 2, 3))
            form = rng.choice(("tile", "bowl"))
            style = ("direct", "paraphrase", "distractor")[index % 3]
            original_state, original_goal, original_plan, original_concept, certificate = _base(family, mass, form)
            # Vary causal quantities, not only wording. The entire version pair
            # shares these choices, including its energy margins and route.
            for target, body in original_state["objects"].items():
                if family == "rewind_shape":
                    continue
                original_temperature = body["temperature"]
                new_temperature = rng.randint(-2, 1) if body["kind"] == "solid" else rng.randint(-3, 0)
                body["temperature"] = new_temperature
                heat_steps = [step for step in original_plan if step["op"] == "heat" and step["target"] == target]
                if heat_steps:
                    heat_steps[0]["delta"] += original_temperature - new_temperature
                    if len(heat_steps) == 2:
                        heat_steps[-1]["delta"] += new_temperature - original_temperature
                final_properties = original_goal["objects"].get(target, {})
                if final_properties.get("temperature") == original_temperature:
                    final_properties["temperature"] = new_temperature
            if "y" in original_state["objects"] and rng.choice((False, True)):
                reflection = {"A": "D", "B": "C", "C": "B", "D": "A"}
                original_state["objects"]["y"]["location"] = "D"
                original_goal["objects"]["y"]["location"] = reflection[original_goal["objects"]["y"]["location"]]
                for step in original_plan:
                    if step["op"] == "move_water":
                        step["destination"] = reflection[step["destination"]]
            costs = Counter()
            for step in original_plan:
                body_mass = original_state["objects"][step["target"]]["mass"]
                costs[step["actor"]] += abs(step["delta"]) * body_mass if step["op"] == "heat" else 2 * body_mass if step["op"] in ("shape", "move_water") else 2 if step["op"] == "anchor" else 3
            for actor_id, actor in original_state["actors"].items():
                actor["energy"] = costs[actor_id] + rng.randint(0, 6)
            settings = STATUSES if slice_name == "core" else ("feasible", "infeasible")
            for setting in settings:
                state, goal, plan = deepcopy(original_state), deepcopy(original_goal), deepcopy(original_plan)
                concept = original_concept
                current_certificate = deepcopy(certificate)
                boundary_type = None
                if setting == "infeasible":
                    boundary_type = ("energy", "mass_cap", "living_target", "missing_keeper")[index % 4] if slice_name == "adaptation" else "energy"
                    if slice_name == "adaptation" and index % 4 in (1, 2):
                        state["objects"]["x"]["mass"] = 3 if index % 4 == 1 else state["objects"]["x"]["mass"]
                        state["objects"]["x"]["living"] = index % 4 == 2
                        current_certificate = {"rule": "no_anchorable_target"}
                    elif slice_name == "adaptation" and index % 4 == 3:
                        state["actors"]["k"]["class"] = "tender"
                        current_certificate = {"rule": "missing_keeper"}
                    else:
                        state["actors"][certificate["actor"]]["energy"] = certificate["required_minimum"] - 1
                    plan = []
                elif setting == "prohibited":
                    concept = ("create_matter", "teleport", "time_travel")[index % 3]
                    plan = []
                elif setting == "unknown":
                    concept = ("shadow_weave", "song_binding", "echo_matter")[index % 3]
                    plan = []
                for version in ("v1", "v2"):
                    membership = concept_status(concept, version)
                    status = setting if membership == "permitted" else membership
                    pair_id = f"{family}-{index:03d}-{setting}"
                    case = {"id": f"{pair_id}-{version}", "pair_id": pair_id, "family_id": family, "split": split, "slice": slice_name, "ontology_version": version, "style": style, "question": _question(style), "initial_state": deepcopy(state), "goal": deepcopy(goal), "requested_concept": concept, "max_steps": 4, "boundary_type": boundary_type, "expected_status": status, "expected_concept_status": membership, "reference_plan": deepcopy(plan) if status == "feasible" else [], "infeasibility_certificate": deepcopy(current_certificate) if status == "infeasible" else None}
                    validate_case(case)
                    cases.append(case)
    return cases


def validate_case(case: dict[str, Any]) -> None:
    membership = concept_status(case["requested_concept"], case["ontology_version"])
    if membership != case["expected_concept_status"]:
        raise ValueError(f"Membership mismatch in {case['id']}")
    if case["expected_status"] == "feasible":
        result = simulate(case["initial_state"], case["ontology_version"], case["reference_plan"], case["max_steps"])
        if not goal_satisfied(result, case["goal"]):
            raise ValueError(f"Invalid reference plan in {case['id']}: {result.error}")
    elif case["expected_status"] == "infeasible":
        # Certificates use a unique class actor and a necessary transformation.
        cert = case["infeasibility_certificate"]
        if cert["rule"] == "no_anchorable_target":
            if case["goal"]["event_counts"].get("rewind_local", 0) < 1 or any(body["kind"] == "solid" and not body["living"] and body["mass"] <= 2 for body in case["initial_state"]["objects"].values()):
                raise ValueError("Invalid no-anchorable-target certificate")
            return
        if cert["rule"] == "missing_keeper":
            if case["goal"]["event_counts"].get("rewind_local", 0) < 1 or any(actor["class"] == "keeper" for actor in case["initial_state"]["actors"].values()):
                raise ValueError("Invalid missing-keeper certificate")
            return
        if cert["rule"] != "class_energy_lower_bound":
            raise ValueError("Unknown infeasibility certificate")
        actor = case["initial_state"]["actors"][cert["actor"]]
        if sum(a["class"] == actor["class"] for a in case["initial_state"]["actors"].values()) != 1:
            raise ValueError("Certificate requires a unique class actor")
        minimum = 0
        objects, targets = case["initial_state"]["objects"], case["goal"]["objects"]
        if actor["class"] == "mason":
            minimum = sum(2 * objects[name]["mass"] for name, props in targets.items() if "shape" in props and props["shape"] != objects[name]["shape"])
        elif actor["class"] == "weaver":
            locations = ("A", "B", "C", "D")
            minimum = sum(2 * objects[name]["mass"] * abs(locations.index(props["location"]) - locations.index(objects[name]["location"])) for name, props in targets.items() if "location" in props)
        elif actor["class"] == "keeper" and case["goal"]["event_counts"].get("rewind_local", 0) >= 1:
            minimum = 5
        if minimum != cert["required_minimum"] or actor["energy"] >= minimum:
            raise ValueError(f"Invalid energy certificate in {case['id']}")


def build_pairs(cases: list[dict[str, Any]], common_only: bool = False) -> list[dict[str, Any]]:
    """Training-only matched plan contrasts; no dev/test text is used."""
    pairs = []
    pair_indices: dict[str, int] = {}
    for case in cases:
        if case["split"] != "train" or case["expected_status"] != "feasible" or (common_only and case["slice"] != "core"):
            continue
        pair_index = pair_indices.setdefault(case["pair_id"], len(pair_indices))
        compatible = reference_response(case)
        incompatible = deepcopy(compatible)
        action_index = pair_index % len(incompatible["plan"])
        corruption = ("prohibited_operation", "unknown_operation", "wrong_class", "wrong_order")[pair_index % 4]
        if corruption in ("prohibited_operation", "unknown_operation"):
            incompatible["plan"][action_index]["op"] = "time_travel" if corruption == "prohibited_operation" else "echo_matter"
        elif corruption == "wrong_class":
            current_actor = incompatible["plan"][action_index]["actor"]
            incompatible["plan"][action_index]["actor"] = "m" if current_actor == "t" else "t"
        else:
            incompatible["plan"][0], incompatible["plan"][1] = incompatible["plan"][1], incompatible["plan"][0]
        result = simulate(case["initial_state"], case["ontology_version"], incompatible["plan"])
        if result.valid:
            raise ValueError("Contrast unexpectedly executable")
        pairs.append({"id": f"contrast-{case['id']}", "family_id": case["family_id"], "split": "train", "ontology_version": case["ontology_version"], "scenario_id": case["id"], "corruption_type": corruption, "compatible_response": compatible, "incompatible_response": incompatible})
    return pairs


def write_dataset(directory: str | Path, seed: int = 1729, per_family: int = 12) -> dict[str, Any]:
    destination = Path(directory)
    destination.mkdir(parents=True, exist_ok=True)
    cases = build_dataset(seed, per_family)
    for split in ("train", "dev", "test"):
        with (destination / f"{split}.jsonl").open("w") as stream:
            for case in cases:
                if case["split"] == split:
                    stream.write(json.dumps(case, sort_keys=True) + "\n")
    pairs = build_pairs(cases)
    with (destination / "pairs.jsonl").open("w") as stream:
        for pair in pairs:
            stream.write(json.dumps(pair, sort_keys=True) + "\n")
    common_pairs = build_pairs(cases, common_only=True)
    with (destination / "pairs-common.jsonl").open("w") as stream:
        for pair in common_pairs:
            stream.write(json.dumps(pair, sort_keys=True) + "\n")
    manifest = {"common_pairs": len(common_pairs), "seed": seed, "per_family": per_family, "total_cases": len(cases), "pairs": len(pairs), "split_counts": dict(Counter(c["split"] for c in cases)), "core_status_counts": dict(Counter(c["expected_status"] for c in cases if c["slice"] == "core")), "adaptation_status_counts": dict(Counter(c["expected_status"] for c in cases if c["slice"] == "adaptation")), "families": {name: {"split": spec[0], "slice": spec[1]} for name, spec in FAMILIES.items()}}
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="data")
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--per-family", type=int, default=12)
    args = parser.parse_args()
    print(json.dumps(write_dataset(args.output, args.seed, args.per_family), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
