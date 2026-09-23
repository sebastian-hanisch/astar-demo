"""Jede Zahl in den Hilfetexten, Presets, Tabellen und Grenzen der App ist hier über die fünf festen Sweep-
Instanzen belegt, mit denselben Auswertungsfunktionen wie die App selbst (`ev.run_config`/`ev.sweep`/
`ev.astar_worse_than_ucs_share`) - NIE über ein Ad-hoc-Skript mit abweichender Zufalls-Bindung. Positive UND
negative Aussagen: A* ist ausnahmslos optimal (positiv) - aber die Vorab-Hypothese "A* behält den Großteil von
GBFS' Effizienzvorsprung" ist FALSCH, er behält nur rund ein Drittel (negativ, der zentrale ehrliche Befund)."""

from functools import lru_cache

import pytest

import astar_constants as C
import astar_evaluation as ev


@lru_cache(maxsize=None)
def _cfg(items):
    return ev.run_config(ev.Settings(), **dict(items))


def cfg(**kw):
    return _cfg(tuple(sorted(kw.items())))


def near(value, expected, tol):
    assert abs(value - expected) <= tol, f"{value:.3f} statt {expected}"


# --- Standardfall ------------------------------------------------------------------------------------------------------------------------------


def test_default_numbers():
    row = cfg()
    near(row["gbfs_gap"], 16.517, 1.0)
    near(row["gbfs_ratio"], 4.993, 0.4)
    near(row["astar_ratio"], 1.376, 0.15)
    near(row["kept_share"], 32.25, 4.0)
    near(row["expansions_gbfs"], 24.4, 2.0)
    near(row["expansions_astar"], 90.0, 6.0)
    near(row["expansions_ucs"], 121.4, 6.0)


def test_the_gbfs_numbers_match_the_root_demo_exactly():
    """Die Kopie ist treu: dieselben Werte wie in greedy-best-first-demo (dort ebenfalls per Test belegt)."""
    row = cfg()
    assert row["gbfs_gap"] == pytest.approx(16.51669894246011, abs=1e-6)
    assert row["gbfs_ratio"] == pytest.approx(4.993236714975845, abs=1e-6)


# --- Optimalität ohne Ausnahme -----------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("obstacle_pct", list(C.OBSTACLE_SWEEP))
def test_a_star_is_optimal_at_every_obstacle_density(obstacle_pct):
    assert cfg(obstacle_pct=obstacle_pct)["astar_gap"] == pytest.approx(0.0, abs=1e-9)


@pytest.mark.parametrize("side", list(C.SCALING_SIDES))
def test_a_star_is_optimal_at_every_grid_size(side):
    assert cfg(side=side)["astar_gap"] == pytest.approx(0.0, abs=1e-9)


# --- Zentrale Frage: behält A* den Großteil von GBFS' Vorsprung? - NEIN ------------------------------------------------------------------------


def test_a_star_keeps_only_a_minority_of_the_gbfs_advantage():
    for kw in (dict(), dict(obstacle_pct=0), dict(obstacle_pct=40), dict(side=22)):
        assert cfg(**kw)["kept_share"] < 50.0, kw


def test_a_star_is_far_less_efficient_than_gbfs_everywhere():
    for kw in (dict(), dict(obstacle_pct=0), dict(obstacle_pct=40), dict(side=6), dict(side=22)):
        row = cfg(**kw)
        assert row["gbfs_ratio"] > row["astar_ratio"] + 0.5, kw


@pytest.mark.parametrize("obstacle_pct,expected,tol", [(0, 1.473, 0.15), (10, 1.52, 0.15), (20, 1.54, 0.15), (30, 1.49, 0.15), (40, 1.204, 0.15)])
def test_obstacle_sweep_a_star_ratio_numbers(obstacle_pct, expected, tol):
    near(cfg(obstacle_pct=obstacle_pct)["astar_ratio"], expected, tol)


def test_a_star_advantage_collapses_only_at_forty_percent_obstacles():
    """Anders als bei GBFS (monoton fallend): A*s Verhältnis bleibt bis 30 % flach und bricht erst bei 40 % ein."""
    flat = [cfg(obstacle_pct=o)["astar_ratio"] for o in (0, 10, 20, 30)]
    assert max(flat) - min(flat) < 0.15
    assert cfg(obstacle_pct=40)["astar_ratio"] < min(flat) - 0.15


# --- Größen-Sweep: A*s Vorsprung wächst NICHT mit der Größe ---------------------------------------------------------------------------------------


@pytest.mark.parametrize("side,expected,tol", [(6, 1.38, 0.2), (14, 1.56, 0.2), (22, 1.39, 0.2)])
def test_scaling_a_star_ratio_numbers(side, expected, tol):
    near(cfg(side=side)["astar_ratio"], expected, tol)


def test_a_star_advantage_does_not_grow_with_grid_size_while_gbfs_does():
    small, large = cfg(side=6), cfg(side=22)
    assert large["gbfs_ratio"] > small["gbfs_ratio"] + 3.0
    assert abs(large["astar_ratio"] - small["astar_ratio"]) < 0.3


# --- Heuristik-Enge: der gemessene Grund ------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("obstacle_pct,expected", [(0, 0.81), (15, 0.757), (40, 0.61)])
def test_heuristic_tightness_numbers(obstacle_pct, expected):
    near(cfg(obstacle_pct=obstacle_pct)["tightness"], expected, 0.04)


def test_the_heuristic_gets_looser_with_more_obstacles():
    assert cfg(obstacle_pct=0)["tightness"] > cfg(obstacle_pct=15)["tightness"] > cfg(obstacle_pct=40)["tightness"]


# --- Effizienz-Frage: A* nie schlechter als UCS -----------------------------------------------------------------------------------------------


def test_a_star_never_expands_more_nodes_than_ucs_on_the_sweep_instances():
    for obstacle_pct in C.OBSTACLE_SWEEP:
        worse, total = ev.astar_worse_than_ucs_share(ev.Settings(obstacle_pct=obstacle_pct), seeds=C.SWEEP_SEEDS)
        assert worse == 0, f"obstacle_pct={obstacle_pct}: {worse}/{total}"


# --- Handgebaute Heuristik-Falle ---------------------------------------------------------------------------------------------------------------


def test_trap_instance_numbers():
    a = ev.analyse(ev.Settings(network="trap"))
    near(a.gbfs_gap, 7.468, 0.1)
    assert abs(a.astar_gap) < 1e-9
    assert (a.gbfs.expansions, a.astar.expansions, a.ucs.expansions) == (6, 7, 8)


# --- Sonstiges --------------------------------------------------------------------------------------------------------------------------------


def test_preset_count_matches_the_readme():
    assert len(C.PRESETS) == 5
