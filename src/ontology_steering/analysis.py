"""Paired, equally family-weighted estimation; no external statistics packages."""
from __future__ import annotations

from collections import defaultdict
import math
import random


def row_key(row):
    return row["id"], row["ontology_version"], row["seed"]


def paired_family_effects(rows, baseline, treatment, metric, predicate=None):
    """Average seed/variant paired differences within family, then weight families equally."""
    indexed = defaultdict(dict)
    for row in rows:
        if row["condition"] not in (baseline, treatment):
            continue
        if predicate is not None and not predicate(row):
            continue
        key = row_key(row)
        if row["condition"] in indexed[key]:
            raise ValueError(f"Duplicate paired row {key}: {row['condition']}")
        indexed[key][row["condition"]] = row
    if not indexed:
        raise ValueError("No eligible paired rows")
    families = defaultdict(list)
    for key, pair in indexed.items():
        if set(pair) != {baseline, treatment}:
            raise ValueError(f"Incomplete pairing at {key}; do not silently drop missing rows")
        a, b = pair[baseline], pair[treatment]
        if a["family_id"] != b["family_id"]:
            raise ValueError(f"Family mismatch at {key}")
        for field in ("model_id", "model_revision", "config", "source_sha256"):
            av = a.get("provenance", {}).get(field)
            bv = b.get("provenance", {}).get(field)
            if field == "config" and isinstance(av, dict) and isinstance(bv, dict):
                # Gaussian control draw differs, while inference settings must match C.
                av = {k: v for k, v in av.items() if k != "random_vector_seed"}
                bv = {k: v for k, v in bv.items() if k != "random_vector_seed"}
            if av != bv:
                raise ValueError(f"Matched run provenance differs for {field} at {key}")
        if a.get("prompt_baseline") == b.get("prompt_baseline") == "C":
            if a.get("prompt_sha256") != b.get("prompt_sha256"):
                raise ValueError(f"Matched C prompt differs at {key}")
        av, bv = a["evaluation"].get(metric), b["evaluation"].get(metric)
        if av is None or bv is None:
            raise ValueError(f"Missing/non-applicable metric {metric} at {key}; specify a stratum")
        if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in (av, bv)):
            raise ValueError(f"Metric {metric} must be finite numeric")
        families[a["family_id"]].append(float(bv) - float(av))
    return {family: sum(values) / len(values) for family, values in families.items()}


def percentile(values, p):
    values = sorted(values)
    pos = (len(values) - 1) * p
    lo, hi = math.floor(pos), math.ceil(pos)
    return values[lo] + (values[hi] - values[lo]) * (pos - lo)


def paired_cluster_bootstrap(rows, baseline, treatment, metric, *, seed=1729,
                             resamples=10000, predicate=None):
    """Percentile CI resampling whole family clusters, including both versions."""
    if resamples < 1:
        raise ValueError("resamples must be positive")
    effects = paired_family_effects(rows, baseline, treatment, metric, predicate)
    values = list(effects.values())
    per_family = defaultdict(lambda: {baseline: [], treatment: []})
    for row in rows:
        if row["condition"] in (baseline, treatment) and (predicate is None or predicate(row)):
            per_family[row["family_id"]][row["condition"]].append(float(row["evaluation"][metric]))
    descriptive = [{"family_id": family, "baseline_rate": sum(data[baseline]) / len(data[baseline]),
                    "treatment_rate": sum(data[treatment]) / len(data[treatment]),
                    "effect": effects[family], "n_paired_rows": len(data[baseline])}
                   for family, data in sorted(per_family.items())]
    informative = len(values) >= 2
    rng = random.Random(seed)
    boot = [sum(rng.choice(values) for _ in values) / len(values) for _ in range(resamples)] if informative else []
    return {"metric": metric, "baseline": baseline, "treatment": treatment,
            "effect": sum(values) / len(values),
            "ci95": [percentile(boot, 0.025), percentile(boot, 0.975)] if informative else None,
            "interval_informative": informative,
            "baseline_family_macro_rate": sum(d["baseline_rate"] for d in descriptive) / len(descriptive),
            "treatment_family_macro_rate": sum(d["treatment_rate"] for d in descriptive) / len(descriptive),
            "per_family": descriptive,
            "n_family_clusters": len(values), "n_rows": sum(
                r["condition"] == baseline and (predicate is None or predicate(r)) for r in rows),
            "bootstrap_seed": seed, "resamples": resamples if informative else 0,
            "requested_resamples": resamples,
            "estimand": "equal-weight mean of within-family paired outcome differences",
            "warning": ("Fewer than two independent family clusters: no informative cluster interval; report descriptive rates only"
                        if not informative else
                        "Intervals with few families are exploratory; seed repeats are not independent families")}


def select_candidate(rows, *, primary="operational_success", margin=0.05,
                     constraints=None):
    """Dev-only selection; use paired C outcomes and predetermined tolerances.

    constraints is a list of (metric, predicate). Missing required strata is an error.
    Tie-break: smallest |alpha|, then earliest layer. All values are point estimates;
    this dev screen does not establish statistical noninferiority on test.
    """
    if not rows or any(r.get("split") != "dev" for r in rows):
        raise ValueError("Selection requires exclusively dev outputs")
    conditions = sorted({r["condition"] for r in rows if r["condition"].startswith("current:")})
    if not conditions:
        raise ValueError("No current-vector dev candidates")
    candidates = []
    for condition in conditions:
        effects = paired_family_effects(rows, "C", condition, primary)
        score = sum(effects.values()) / len(effects)
        losses = {}
        for constraint in constraints or []:
            metric, predicate = constraint[:2]
            label = constraint[2] if len(constraint) > 2 else metric
            values = paired_family_effects(rows, "C", condition, metric, predicate).values()
            values = list(values)
            losses[label] = sum(values) / len(values)
        example = next(r for r in rows if r["condition"] == condition)
        candidates.append({"condition": condition, "layer": example["layer"],
                           "alpha": example["alpha"], "primary_effect": score,
                           "constraint_effects": losses,
                           "eligible": all(x >= -margin for x in losses.values())})
    eligible = [c for c in candidates if c["eligible"]]
    if not eligible:
        raise ValueError("No eligible candidate; investigate data or alpha-zero control")
    selected = sorted(eligible, key=lambda c: (-c["primary_effect"], abs(c["alpha"]), c["layer"]))[0]
    return {"selected": selected, "candidates": candidates,
            "primary_metric": primary, "noninferiority_margin": margin,
            "selection_split": "dev", "test_results_seen": False}
