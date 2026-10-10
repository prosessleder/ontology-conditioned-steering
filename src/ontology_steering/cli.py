"""Commands keep train extraction, dev selection, and test evaluation separate."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analysis import paired_cluster_bootstrap, row_key, select_candidate
from .runner import collect_vectors, design_hashes, run_condition, source_hashes
from .steering import hash_value, read_jsonl, sha256_file, write_json


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path.cwd())
    sub = p.add_subparsers(dest="command", required=True)
    ds = sub.add_parser("dataset")
    ds.add_argument("--out", type=Path, default=Path("data"))
    ds.add_argument("--seed", type=int, default=1729)
    ds.add_argument("--per-family", type=int, default=12)
    for command in ("collect", "run", "freeze"):
        c = sub.add_parser(command)
        c.add_argument("--config", type=Path, default=Path("configs/pilot.json"))
        c.add_argument("--data", type=Path, default=Path("data"))
        c.add_argument("--out", type=Path, required=True)
        if command == "run":
            c.add_argument("--split", choices=("dev", "test"), default="dev")
            c.add_argument("--condition", choices=("A", "B", "C", "current", "stale", "random"), required=True)
            c.add_argument("--vectors", type=Path)
            c.add_argument("--layer", type=int)
            c.add_argument("--alpha", type=float)
            c.add_argument("--selection", type=Path)
            c.add_argument("--ontology-version", choices=("v1", "v2"))
            c.add_argument("--limit", type=int)
        elif command == "freeze":
            c.add_argument("--vectors", type=Path, required=True)
            c.add_argument("--dev", type=Path, nargs="+", required=True)
            c.add_argument("--secondary-config", type=Path, nargs="+", default=[])
        else:
            c.add_argument("--pairs", type=Path)
    a = sub.add_parser("analyze")
    a.add_argument("--runs", type=Path, nargs="+", required=True)
    a.add_argument("--baseline", default="C")
    a.add_argument("--treatment", required=True)
    a.add_argument("--metric", default="operational_success")
    a.add_argument("--ontology-version", choices=("v1", "v2"))
    a.add_argument("--stratum", choices=("all", "feasible", "ordinary-feasible", "unknown", "temporal-feasible"), default="all")
    a.add_argument("--resamples", type=int, default=10000)
    a.add_argument("--seed", type=int, default=1729)
    a.add_argument("--out", type=Path)
    return p


def stratum_predicate(stratum, version=None):
    def selected(row):
        if version and row["ontology_version"] != version:
            return False
        feasible = row.get("expected_status") == "feasible"
        temporal = row.get("requested_concept") == "rewind_local"
        return {"all": True, "feasible": feasible,
                "ordinary-feasible": feasible and not temporal,
                "unknown": row.get("expected_status") == "unknown",
                "temporal-feasible": feasible and temporal}[stratum]
    return selected


def freeze(args, config):
    rows = [r for path in args.dev for r in read_jsonl(path)]
    for row in rows:
        if row.get("provenance", {}).get("config") != config:
            raise ValueError("All dev candidate outputs must use the frozen configuration")
    constraints = [("task_success", stratum_predicate("ordinary-feasible", v), f"ordinary_task_success:{v}")
                   for v in ("v1", "v2")]
    constraints += [("unknown_recognition", stratum_predicate("unknown", v), f"unknown_recognition:{v}")
                    for v in ("v1", "v2")]
    result = select_candidate(rows, primary="operational_success",
                              margin=config.get("noninferiority_margin", 0.05), constraints=constraints)
    # Require complete predetermined grid, including alpha zero. No post-test tuning.
    expected = {(l, float(a)) for l in config["layers"] for a in config["alphas"]}
    actual = {(c["layer"], c["alpha"]) for c in result["candidates"]}
    if actual != expected:
        raise ValueError("Run every predeclared layer/alpha candidate before freezing")
    dev_cases = read_jsonl(args.data / "dev.jsonl")
    expected_keys = {(c["id"], c["ontology_version"], seed)
                     for c in dev_cases for seed in config.get("seeds", [11])}
    for condition in ["C"] + [c["condition"] for c in result["candidates"]]:
        actual_keys = {row_key(r) for r in rows if r["condition"] == condition}
        if actual_keys != expected_keys:
            raise ValueError(f"Incomplete dev evaluation for {condition}; pilot limits cannot be frozen")
    for row in rows:
        if row["provenance"].get("dataset_sha256") != sha256_file(args.data / "dev.jsonl"):
            raise ValueError("Dev outputs do not match current dataset")
        if row["condition"] != "C" and row["provenance"].get("vectors_sha256") != sha256_file(args.vectors):
            raise ValueError("Dev outputs do not match current vector artifact")
        if row["provenance"].get("source_sha256") != source_hashes(args.root):
            raise ValueError("Source changed after dev outputs; rerun dev before freezing")
    allowed = [hash_value(config)]
    for secondary_path in args.secondary_config:
        secondary = json.loads(secondary_path.read_text())
        for key in ("model_id", "model_revision", "device", "dtype", "max_context_tokens", "max_new_tokens"):
            if secondary[key] != config[key]:
                raise ValueError(f"Secondary configuration changes {key}")
        allowed.append(hash_value(secondary))
    result.update(config_sha256=hash_value(config), allowed_config_sha256=allowed,
                  vectors_sha256=sha256_file(args.vectors),
                  train_sha256=sha256_file(args.data / "train.jsonl"),
                  dev_sha256=sha256_file(args.data / "dev.jsonl"),
                  test_sha256=sha256_file(args.data / "test.jsonl"),
                  dev_output_sha256={str(path): sha256_file(path) for path in args.dev},
                  ontology_sha256={v: sha256_file(args.root / "experiment" / f"ontology-{v}.md")
                                   for v in ("v1", "v2")}, source_sha256=source_hashes(args.root),
                  design_sha256=design_hashes(args.root))
    if args.out.exists():
        raise FileExistsError("Frozen selection already exists; never overwrite the audit record")
    write_json(args.out, result)
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    if args.command == "dataset":
        from .dataset import write_dataset
        result = write_dataset(args.out, seed=args.seed, per_family=args.per_family)
    elif args.command == "analyze":
        rows = [r for path in args.runs for r in read_jsonl(path)]
        if len({r["split"] for r in rows}) != 1:
            raise ValueError("Analyze one split at a time")
        result = paired_cluster_bootstrap(rows, args.baseline, args.treatment, args.metric,
                                         seed=args.seed, resamples=args.resamples,
                                         predicate=stratum_predicate(args.stratum, args.ontology_version))
        if args.out:
            write_json(args.out, result)
    else:
        config = json.loads(args.config.read_text())
        if args.command == "collect":
            result = collect_vectors(config, args.data, args.out, args.root, pair_file=args.pairs)
        elif args.command == "freeze":
            result = freeze(args, config)
        else:
            result = run_condition(config, args.data, args.split, args.condition, args.out, args.root,
                                   vector_file=args.vectors, layer=args.layer, alpha=args.alpha,
                                   selection_file=args.selection, ontology_version=args.ontology_version,
                                   limit=args.limit)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
