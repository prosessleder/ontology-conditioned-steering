import pytest

from ontology_steering.analysis import paired_cluster_bootstrap, select_candidate


def row(id, family, condition, value, seed=11, version="v1", split="test", alpha=None, layer=None):
    return {"id": id, "family_id": family, "condition": condition, "seed": seed,
            "ontology_version": version, "split": split,
            "evaluation": {"joint_success": value, "task_success": value},
            "alpha": alpha, "layer": layer}


def test_equal_family_weight_and_pairing():
    rows = [row("x", "one", "C", 0), row("x", "one", "T", 1)]
    for i in range(10):
        rows += [row(str(i), "two", "C", 1), row(str(i), "two", "T", 0)]
    result = paired_cluster_bootstrap(rows, "C", "T", "joint_success", resamples=100, seed=9)
    assert result["effect"] == 0  # Cases would weight the larger family ten times.
    assert result["n_family_clusters"] == 2
    assert result == paired_cluster_bootstrap(rows, "C", "T", "joint_success", resamples=100, seed=9)
    with pytest.raises(ValueError, match="Incomplete"):
        paired_cluster_bootstrap(rows[:-1], "C", "T", "joint_success", resamples=10)
    with pytest.raises(ValueError, match="Duplicate"):
        paired_cluster_bootstrap(rows + rows[:1], "C", "T", "joint_success", resamples=10)


def test_version_twins_and_seeds_do_not_inflate_independence():
    rows = []
    for version in ("v1", "v2"):
        for seed in (11, 29, 47):
            rows += [row("x", "one", "C", 0, seed, version),
                     row("x", "one", "T", 1, seed, version)]
    result = paired_cluster_bootstrap(rows, "C", "T", "joint_success", resamples=100)
    assert result["effect"] == 1
    assert result["n_family_clusters"] == 1
    assert result["ci95"] is None
    assert result["interval_informative"] is False
    assert result["per_family"][0]["baseline_rate"] == 0
    assert result["per_family"][0]["treatment_rate"] == 1


def test_dev_selection_and_noninferiority_screen():
    rows = [row("x", "f", "C", 0, split="dev"),
            row("x", "f", "current:l0:a0", 0, split="dev", alpha=0, layer=0),
            row("x", "f", "current:l0:a0.1", 1, split="dev", alpha=.1, layer=0)]
    result = select_candidate(rows, primary="joint_success", constraints=[("task_success", lambda r: True)])
    assert result["selected"]["alpha"] == .1
    rows[-1]["evaluation"]["task_success"] = -1
    result = select_candidate(rows, primary="joint_success", constraints=[("task_success", lambda r: True)])
    assert result["selected"]["alpha"] == 0
    rows[-1]["split"] = "test"
    with pytest.raises(ValueError, match="dev"):
        select_candidate(rows, primary="joint_success")


def test_identical_prompt_is_checked():
    rows = [row("x", "f", "C", 0), row("x", "f", "T", 1)]
    for i, r in enumerate(rows):
        r.update(prompt_baseline="C", prompt_sha256=str(i))
    with pytest.raises(ValueError, match="prompt differs"):
        paired_cluster_bootstrap(rows, "C", "T", "joint_success", resamples=10)
