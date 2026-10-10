from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from ontology_steering.dataset import FAMILIES, build_dataset, build_pairs, reference_response, validate_case, write_dataset
from ontology_steering.evaluate import evaluate_jsonl, evaluate_response
from ontology_steering.world import solve


class DatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = build_dataset(per_family=3)

    def test_deterministic_generation_and_counts(self):
        self.assertEqual(self.cases, build_dataset(per_family=3))
        self.assertEqual(len(self.cases), 180)
        self.assertEqual(Counter(c["split"] for c in self.cases), {"train": 60, "dev": 60, "test": 60})
        counts = Counter(c["expected_status"] for c in self.cases if c["slice"] == "core")
        self.assertEqual(counts, {"feasible": 36, "infeasible": 36, "prohibited": 36, "unknown": 36})
        self.assertNotEqual(self.cases, build_dataset(seed=1730, per_family=3))

    def test_structural_family_splits_are_disjoint(self):
        splits = {s: {c["family_id"] for c in self.cases if c["split"] == s} for s in ("train", "dev", "test")}
        for first, second in (("train", "dev"), ("dev", "test"), ("train", "test")):
            self.assertFalse(splits[first] & splits[second])
        self.assertEqual(set().union(*splits.values()), set(FAMILIES))

    def test_versions_are_matched_with_expected_label_shift(self):
        pairs = {}
        for case in self.cases:
            pairs.setdefault(case["pair_id"], {})[case["ontology_version"]] = case
        for pair in pairs.values():
            v1, v2 = pair["v1"], pair["v2"]
            for field in ("initial_state", "goal", "question", "requested_concept", "family_id", "split", "style"):
                self.assertEqual(v1[field], v2[field])
            if v1["slice"] == "core":
                self.assertEqual(v1["expected_status"], v2["expected_status"])
            else:
                self.assertEqual(v1["expected_status"], "unknown")
                self.assertIn(v2["expected_status"], ("feasible", "infeasible"))

    def test_every_reference_passes_and_certificates_are_checked(self):
        for case in self.cases:
            result = evaluate_response(case, json.dumps(reference_response(case)))
            with self.subTest(id=case["id"]):
                self.assertTrue(result["schema_valid"])
                self.assertTrue(result["status_correct"])
                self.assertTrue(result["ontology_adherence"])
                self.assertTrue(result["operational_success"])
                if case["expected_status"] == "feasible":
                    self.assertTrue(result["task_success"])
                if case["expected_status"] == "infeasible":
                    invalid = deepcopy(case)
                    invalid["infeasibility_certificate"]["rule"] = "invalid_certificate"
                    with self.assertRaises(ValueError):
                        validate_case(invalid)

    def test_adaptation_infeasibility_boundaries(self):
        cases = [case for case in build_dataset(per_family=4) if case["slice"] == "adaptation" and case["expected_status"] == "infeasible"]
        self.assertEqual({case["infeasibility_certificate"]["rule"] for case in cases}, {"class_energy_lower_bound", "no_anchorable_target", "missing_keeper"})
        for case in cases:
            self.assertIsNone(solve(case["initial_state"], "v2", case["goal"], 4))

    def test_exhaustive_search_agrees_with_one_instance_of_each_family(self):
        chosen = [c for c in self.cases if c["id"].split("-")[1] == "000" and c["expected_concept_status"] == "permitted" and c["ontology_version"] == "v2"]
        for case in chosen:
            with self.subTest(id=case["id"]):
                solution = solve(case["initial_state"], "v2", case["goal"], 4)
                self.assertEqual(solution is not None, case["expected_status"] == "feasible")

    def test_contrast_pairs_are_train_only_and_incompatible(self):
        pairs = build_pairs(self.cases)
        self.assertEqual(len(pairs), 15)
        common = build_pairs(self.cases, common_only=True)
        self.assertEqual(len(common), 12)
        self.assertEqual(Counter(p["ontology_version"] for p in common), {"v1": 6, "v2": 6})
        twins = {}
        for pair in common:
            pair_id = pair["scenario_id"].rsplit("-", 1)[0]
            twins.setdefault(pair_id, []).append(pair)
        for versions in twins.values():
            self.assertEqual(versions[0]["compatible_response"], versions[1]["compatible_response"])
            self.assertEqual(versions[0]["incompatible_response"], versions[1]["incompatible_response"])
        by_id = {case["id"]: case for case in self.cases}
        for pair in pairs:
            case = by_id[pair["scenario_id"]]
            self.assertEqual(case["split"], "train")
            self.assertTrue(evaluate_response(case, pair["compatible_response"])["task_success"])
            evaluation = evaluate_response(case, pair["incompatible_response"])
            self.assertFalse(evaluation["task_success"])
            self.assertEqual(evaluation["interference"], pair["corruption_type"] in ("prohibited_operation", "unknown_operation"))
            self.assertFalse(evaluation["plan_valid"])
        self.assertEqual({pair["corruption_type"] for pair in pairs}, {"prohibited_operation", "unknown_operation", "wrong_class", "wrong_order"})

    def test_malformed_model_json_counts_as_failure_without_crashing(self):
        feasible = next(c for c in self.cases if c["expected_status"] == "feasible")
        malformed = ("", "```json\n{}\n```", "[]", "null", "{}", '{"status":"feasible","status":"unknown"}', '{"value":NaN}', "[" * 2000, {"status": [], "concept_status": "permitted", "plan": [], "explanation": ""})
        for raw in malformed:
            with self.subTest(raw=str(raw)[:50]):
                result = evaluate_response(feasible, raw)
                self.assertFalse(result["schema_valid"])
                self.assertFalse(result["task_success"])

    def test_empty_refusal_does_not_count_as_task_success(self):
        feasible = next(c for c in self.cases if c["expected_status"] == "feasible")
        refusal = {"status": "infeasible", "concept_status": "permitted", "plan": [], "explanation": ""}
        result = evaluate_response(feasible, refusal)
        self.assertTrue(result["ontology_adherence"])
        self.assertFalse(result["task_success"])
        self.assertFalse(result["operational_success"])
        self.assertTrue(result["over_suppression"])
        incorrect_plan = reference_response(feasible)
        incorrect_plan["plan"][0]["actor"] = []
        result = evaluate_response(feasible, incorrect_plan)
        self.assertFalse(result["schema_valid"])
        self.assertFalse(result["task_success"])

    def test_jsonl_missing_responses_are_failures_and_duplicate_ids_rejected(self):
        with tempfile.TemporaryDirectory() as path:
            destination = Path(path)
            manifest = write_dataset(destination, per_family=1)
            self.assertEqual(manifest["total_cases"], 60)
            cases = [json.loads(line) for line in (destination / "test.jsonl").read_text().splitlines()]
            response_path = destination / "responses.jsonl"
            record = {"id": cases[0]["id"], "response": reference_response(cases[0])}
            response_path.write_text(json.dumps(record) + "\n")
            summary = evaluate_jsonl(destination / "test.jsonl", response_path)
            self.assertEqual(summary["missing"], len(cases) - 1)
            self.assertEqual(summary["metrics"]["schema_valid"]["rate"], 1 / len(cases))
            response_path.write_text(json.dumps(record) + "\n" + json.dumps(record) + "\n")
            with self.assertRaises(ValueError):
                evaluate_jsonl(destination / "test.jsonl", response_path)


if __name__ == "__main__":
    unittest.main()
