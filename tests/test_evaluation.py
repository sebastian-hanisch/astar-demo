import math

import astar_constants as C
import astar_evaluation as EV


def test_analyse_grid_and_trap_return_valid_results_for_all_three_searches():
    for network in ("grid", "trap"):
        a = EV.analyse(EV.Settings(network=network, side=10, obstacle_pct=20, seed=1))
        for result in (a.gbfs, a.astar, a.ucs):
            assert result.path and result.path[0] == a.inst.start and result.path[-1] == a.inst.goal


def test_a_star_gap_is_zero_and_gbfs_gap_is_never_negative():
    for seed in range(15):
        a = EV.analyse(EV.Settings(side=10, obstacle_pct=20, seed=seed))
        assert abs(a.astar_gap) < 1e-9
        assert a.gbfs_gap >= -1e-9


def test_ratios_are_finite_and_a_star_is_never_less_efficient_than_ucs():
    for seed in range(15):
        a = EV.analyse(EV.Settings(side=10, obstacle_pct=20, seed=seed))
        assert a.gbfs_ratio > 0 and a.astar_ratio >= 1.0


def test_kept_share_is_between_zero_and_one_hundred_when_defined():
    for seed in range(15):
        a = EV.analyse(EV.Settings(side=12, obstacle_pct=15, seed=seed))
        if not math.isnan(a.kept_share):
            assert 0.0 <= a.kept_share <= 100.0 + 1e-9


def test_kept_share_is_nan_when_gbfs_has_no_advantage():
    a = EV.analyse(EV.Settings(network="trap"))
    # Falle: GBFS 6, A* 7, UCS 8 Expansionen -> definiert (Vorsprung 2), A* behält die Hälfte
    assert a.kept_share == 50.0


def test_tightness_is_between_zero_and_one():
    for seed in range(10):
        a = EV.analyse(EV.Settings(side=10, obstacle_pct=20, seed=seed))
        assert 0.0 < a.tightness <= 1.0 + 1e-9


def test_run_config_averages_over_the_requested_seeds():
    out = EV.run_config(EV.Settings(), seeds=(1, 2, 3))
    assert out["n_runs"] == 3 and out["astar_gap"] == 0.0
    for key in ("gbfs_gap", "astar_gap", "gbfs_ratio", "astar_ratio", "kept_share", "tightness"):
        assert key in out and f"{key}_sd" in out
    for key in ("expansions_gbfs", "expansions_astar", "expansions_ucs"):
        assert out[key] > 0


def test_sweep_returns_one_row_per_value():
    assert [r["value"] for r in EV.sweep("obstacle_pct", EV.Settings())] == list(C.OBSTACLE_SWEEP)
    assert [r["value"] for r in EV.sweep("side", EV.Settings())] == list(C.SCALING_SIDES)


def test_worse_share_is_a_valid_fraction():
    worse, total = EV.astar_worse_than_ucs_share(EV.Settings(), seeds=C.SWEEP_SEEDS)
    assert 0 <= worse <= total == len(C.SWEEP_SEEDS)


def test_analyse_is_deterministic():
    a1 = EV.analyse(EV.Settings(side=12, obstacle_pct=25, seed=7))
    a2 = EV.analyse(EV.Settings(side=12, obstacle_pct=25, seed=7))
    assert a1.astar_ratio == a2.astar_ratio and a1.gbfs_gap == a2.gbfs_gap
