import copy
import unittest

from ontology_steering.world import World, WorldError, concept_status, goal_satisfied, simulate, solve


def state(mass=1):
    return {
        "actors": {"t": {"class": "tender", "energy": 20}, "m": {"class": "mason", "energy": 10}, "w": {"class": "weaver", "energy": 10}, "k": {"class": "keeper", "energy": 5}, "k2": {"class": "keeper", "energy": 5}},
        "objects": {"x": {"kind": "solid", "material": "lumenclay", "mass": mass, "temperature": 0, "location": "A", "shape": "raw", "living": False}, "y": {"kind": "water", "material": "water", "mass": 1, "temperature": 0, "location": "A", "shape": "fluid", "living": False}},
    }


def heat(delta=2, target="x"):
    return {"op": "heat", "actor": "t", "target": target, "delta": delta}


def shape():
    return {"op": "shape", "actor": "m", "target": "x", "shape": "bowl"}


def anchor():
    return {"op": "anchor", "actor": "k", "target": "x"}


def rewind(actor="k"):
    return {"op": "rewind_local", "actor": actor, "target": "x"}


class WorldTests(unittest.TestCase):
    def test_open_world_membership_and_version_change(self):
        self.assertEqual(concept_status("time_travel", "v1"), "prohibited")
        self.assertEqual(concept_status("shadow_weave", "v2"), "unknown")
        self.assertEqual(concept_status("rewind_local", "v1"), "unknown")
        self.assertEqual(concept_status("rewind_local", "v2"), "permitted")
        with self.assertRaises(ValueError):
            concept_status("heat", "v3")

    def test_composed_shape_and_mass_scaled_energy(self):
        initial = state(2)
        result = simulate(initial, "v1", [heat(), shape(), heat(-2)])
        self.assertTrue(result.valid)
        self.assertEqual(result.state["objects"]["x"]["shape"], "bowl")
        self.assertEqual(result.state["objects"]["x"]["temperature"], 0)
        self.assertEqual(result.state["actors"]["t"]["energy"], 12)
        self.assertEqual(result.state["actors"]["m"]["energy"], 6)
        self.assertEqual(initial, state(2))
        for key in ("mass", "material", "kind", "living", "location"):
            self.assertEqual(result.state["objects"]["x"][key], initial["objects"]["x"][key])

    def test_shape_requires_temperature_and_class(self):
        self.assertEqual(simulate(state(), "v1", [shape()]).error_code, "precondition")
        wrong = dict(shape(), actor="t")
        self.assertEqual(simulate(state(), "v1", [heat(), wrong]).error_code, "class")

    def test_water_requires_warming_and_adjacency(self):
        move = {"op": "move_water", "actor": "w", "target": "y", "destination": "B"}
        self.assertFalse(simulate(state(), "v1", [move]).valid)
        self.assertFalse(simulate(state(), "v1", [heat(1, "y"), dict(move, destination="C")]).valid)
        result = simulate(state(), "v1", [heat(1, "y"), move, dict(move, destination="C"), heat(-1, "y")])
        self.assertTrue(goal_satisfied(result, {"objects": {"y": {"location": "C", "temperature": 0}}}))

    def test_failed_actions_are_atomic(self):
        world = World(state(), "v2")
        world.apply(anchor())
        before = copy.deepcopy(world.__dict__)
        with self.assertRaises(WorldError):
            world.apply(heat(99))
        self.assertEqual(world.__dict__, before)
        world.state["actors"]["t"]["energy"] = 0
        before = copy.deepcopy(world.__dict__)
        with self.assertRaises(WorldError):
            world.apply(heat())
        self.assertEqual(world.__dict__, before)

    def test_temporal_rewind_restores_body_but_not_energy_or_history(self):
        initial = state()
        result = simulate(initial, "v2", [anchor(), heat(), shape(), rewind()])
        self.assertTrue(result.valid, result.error)
        self.assertEqual(result.state["objects"], initial["objects"])
        self.assertEqual(result.state["actors"]["k"]["energy"], 0)
        self.assertEqual(result.state["actors"]["t"]["energy"], 18)
        self.assertEqual(result.state["actors"]["m"]["energy"], 8)
        self.assertEqual(len(result.events), 4)
        self.assertTrue(goal_satisfied(result, {"objects": {"x": {"shape": "raw", "temperature": 0}}, "event_counts": {"shape": 1, "rewind_local": 1}}))

    def test_temporal_boundaries(self):
        variants = [
            [anchor(), rewind()],
            [anchor(), heat(), rewind("k2")],
            [anchor(), heat(1, "y"), rewind()],
            [anchor(), heat(), heat(-1), heat(1), rewind()],
        ]
        for plan in variants:
            with self.subTest(plan=plan):
                self.assertFalse(simulate(state(), "v2", plan, max_steps=6).valid)
        self.assertEqual(simulate(state(), "v1", [anchor()]).error_code, "unknown")
        self.assertFalse(simulate(state(3), "v2", [anchor()]).valid)
        plan = [anchor(), heat(), rewind(), anchor()]
        self.assertFalse(simulate(state(), "v2", plan).valid)

    def test_living_bodies_cannot_be_changed(self):
        initial = state()
        initial["objects"]["x"]["living"] = True
        self.assertFalse(simulate(initial, "v2", [heat()]).valid)
        self.assertFalse(simulate(initial, "v2", [anchor()]).valid)

    def test_strict_action_schema(self):
        for action in (dict(heat(), delta=True), dict(heat(), delta=2.0), dict(heat(), actor=[]), dict(heat(), extra="x"), {"op": "heat"}):
            with self.subTest(action=action):
                self.assertEqual(simulate(state(), "v1", [action]).error_code, "schema")
        self.assertEqual(simulate(state(), "v1", [{"op": "create_matter"}]).error_code, "prohibited")
        self.assertEqual(simulate(state(), "v1", [{"op": "echo_matter"}]).error_code, "unknown")
        self.assertFalse(simulate(state(), "v1", [heat()] * 5).valid)
        self.assertFalse(simulate(state(), "v1", "heat").valid)

    def test_solver_checks_feasible_and_infeasible_compositions(self):
        initial = state()
        initial["objects"].pop("y")
        initial["actors"].pop("k2")
        goal = {"objects": {"x": {"shape": "bowl", "temperature": 0}}}
        plan = solve(initial, "v1", goal)
        self.assertEqual(len(plan), 3)
        self.assertTrue(goal_satisfied(simulate(initial, "v1", plan), goal))
        initial["actors"]["m"]["energy"] = 1
        self.assertIsNone(solve(initial, "v1", goal))
        self.assertIsNone(solve(state(), "v1", {"event_counts": {"rewind_local": 1}}))


if __name__ == "__main__":
    unittest.main()
