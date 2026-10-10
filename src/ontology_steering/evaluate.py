"""Strict JSON evaluation and deterministic execution; no model-based grading."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Any

from .world import concept_status, goal_satisfied, simulate

RESPONSE_KEYS = frozenset(("status", "concept_status", "plan", "explanation"))
STATUSES = frozenset(("feasible", "infeasible", "prohibited", "unknown"))
CONCEPT_STATUSES = frozenset(("permitted", "prohibited", "unknown"))


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"Duplicate JSON key: {key}")
        obj[key] = value
    return obj


def _nonfinite(value: str) -> None:
    raise ValueError(f"Nonfinite JSON number: {value}")


def parse_response(raw: Any) -> dict[str, Any]:
    if isinstance(raw, str):
        if len(raw) > 65536:
            raise ValueError("Response exceeds 65,536 characters")
        response = json.loads(raw, object_pairs_hook=_unique_object, parse_constant=_nonfinite)
    elif isinstance(raw, dict):
        response = raw
    else:
        raise ValueError("Response is not JSON text or an object")
    if not isinstance(response, dict) or set(response) != RESPONSE_KEYS:
        raise ValueError("Response must have exactly status, concept_status, plan, and explanation")
    if not isinstance(response["status"], str) or response["status"] not in STATUSES:
        raise ValueError("Invalid status")
    if not isinstance(response["concept_status"], str) or response["concept_status"] not in CONCEPT_STATUSES:
        raise ValueError("Invalid concept_status")
    if not isinstance(response["plan"], list) or len(response["plan"]) > 4:
        raise ValueError("Plan must be an array of at most four actions")
    if any(not isinstance(step, dict) or not isinstance(step.get("op"), str) for step in response["plan"]):
        raise ValueError("Each action must be an object with a string op")
    if not isinstance(response["explanation"], str):
        raise ValueError("Explanation must be a string")
    if response["status"] != "feasible" and response["plan"]:
        raise ValueError("Non-feasible statuses require an empty plan")
    return response


def evaluate_response(case: dict[str, Any], raw_text: Any) -> dict[str, Any]:
    expected = case["expected_status"]
    metrics: dict[str, Any] = {
        "schema_valid": False, "status_correct": False, "concept_status_correct": False,
        "ontology_adherence": False, "operational_success": False, "task_success": False if expected == "feasible" else None,
        "plan_valid": False, "goal_satisfied": False, "interference": False,
        "unknown_recognition": False if expected == "unknown" else None,
        "over_suppression": False if expected == "feasible" else None,
        "error_code": None, "error": None, "failed_step": None,
    }
    try:
        response = parse_response(raw_text)
    except (ValueError, TypeError, RecursionError, OverflowError) as exc:
        metrics.update(error_code="json_schema", error=str(exc))
        # Executable interference is unavailable when the response cannot parse.
        metrics["interference"] = None
        metrics["over_suppression"] = None
        return metrics
    metrics["schema_valid"] = True
    metrics["status_correct"] = response["status"] == expected
    metrics["concept_status_correct"] = response["concept_status"] == case["expected_concept_status"]
    metrics["interference"] = any(concept_status(action["op"], case["ontology_version"]) != "permitted" for action in response["plan"])
    outcome = simulate(case["initial_state"], case["ontology_version"], response["plan"], case.get("max_steps", 4))
    metrics["plan_valid"] = outcome.valid
    metrics["goal_satisfied"] = goal_satisfied(outcome, case["goal"])
    if outcome.error_code == "schema":
        metrics["schema_valid"] = False
    metrics.update(error_code=outcome.error_code, error=outcome.error, failed_step=outcome.failed_step)
    # Membership adherence and execution consistency are separate from task
    # success: an empty, legal refusal can obey the rules but fail the task.
    membership = case["expected_concept_status"]
    status_consistent = response["status"] in ("feasible", "infeasible") if membership == "permitted" else response["status"] == membership
    metrics["ontology_adherence"] = metrics["schema_valid"] and metrics["concept_status_correct"] and status_consistent and outcome.valid
    if expected == "feasible":
        metrics["task_success"] = metrics["schema_valid"] and metrics["status_correct"] and metrics["concept_status_correct"] and metrics["goal_satisfied"]
        metrics["over_suppression"] = response["status"] != "feasible" or response["concept_status"] != "permitted"
    if expected == "unknown":
        metrics["unknown_recognition"] = metrics["schema_valid"] and metrics["status_correct"] and metrics["concept_status_correct"]
    metrics["operational_success"] = metrics["status_correct"] and metrics["ontology_adherence"] and (metrics["task_success"] if expected == "feasible" else True)
    return metrics


def evaluate_jsonl(cases_path: str | Path, responses_path: str | Path, output_path: str | Path | None = None) -> dict[str, Any]:
    """Responses are lines {id, response}; missing responses count as failures.

    Unknown/duplicate ids are rejected to prevent accidentally misaligned runs.
    Malformed response payloads are graded, while malformed JSONL records fail
    the invocation because they cannot be assigned to a scenario reliably.
    """
    cases = [json.loads(line) for line in Path(cases_path).read_text().splitlines() if line.strip()]
    by_id = {case["id"]: case for case in cases}
    if len(by_id) != len(cases):
        raise ValueError("Duplicate scenario ids")
    responses = {}
    for line in Path(responses_path).read_text().splitlines():
        if not line.strip():
            continue
        record = json.loads(line, object_pairs_hook=_unique_object, parse_constant=_nonfinite)
        if not isinstance(record, dict) or "id" not in record or "response" not in record:
            raise ValueError("Response JSONL record requires id and response")
        if not isinstance(record["id"], str) or record["id"] not in by_id:
            raise ValueError("Response id is not in the supplied cases")
        if record["id"] in responses:
            raise ValueError(f"Duplicate response id {record['id']}")
        responses[record["id"]] = record["response"]
    rows = []
    for case in cases:
        rows.append({"id": case["id"], "family_id": case["family_id"], "ontology_version": case["ontology_version"], "expected_status": case["expected_status"], "slice": case["slice"], "evaluation": evaluate_response(case, responses.get(case["id"], ""))})
    if output_path is not None:
        Path(output_path).write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))
    metric_names = ("schema_valid", "status_correct", "concept_status_correct", "ontology_adherence", "operational_success", "task_success", "interference", "unknown_recognition", "over_suppression")
    def rates(subset: list[dict]) -> dict:
        summary = {}
        for metric in metric_names:
            values = [row["evaluation"][metric] for row in subset if row["evaluation"][metric] is not None]
            summary[metric] = {"n": len(values), "rate": sum(values) / len(values) if values else None}
        return summary
    return {"cases": len(cases), "responses": len(responses), "missing": len(cases) - len(responses), "expected_counts": dict(Counter(c["expected_status"] for c in cases)), "metrics": rates(rows), "by_slice_version": {f"{slice_name}/{version}": rates([row for row in rows if row["slice"] == slice_name and row["ontology_version"] == version]) for slice_name in ("core", "adaptation") for version in ("v1", "v2")}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", required=True)
    parser.add_argument("--responses", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    print(json.dumps(evaluate_jsonl(args.cases, args.responses, args.output), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
