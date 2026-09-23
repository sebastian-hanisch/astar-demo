"""Presets: Vollständigkeit, gültige Werte, A*-Effizienzverhältnis bleibt in der gemessenen Spannweite über die 5
festen Sweep-Instanzen (vollständig deterministisch), A* ist in JEDEM Preset optimal."""

import pytest

import astar_constants as C
import astar_evaluation as ev
import astar_presets as P


def _settings(p, seed=None):
    return ev.Settings(network=p["network"], side=p["side"], obstacle_pct=p["obstacle_pct"], seed=p["seed"] if seed is None else seed)


def test_every_preset_has_help_and_a_band():
    assert set(C.PRESETS) == set(C.PRESET_HELP) == set(C.PRESET_EXPECTED_BANDS)
    assert len(C.PRESETS) == 5
    for name, p in C.PRESETS.items():
        assert set(p) == set(P.PRESET_KEYS) and C.PRESET_HELP[name]


def test_preset_values_are_valid():
    for p in C.PRESETS.values():
        assert p["network"] in P.NETWORKS
        assert C.SIDE_MIN <= p["side"] <= C.SIDE_MAX
        assert C.OBSTACLE_MIN <= p["obstacle_pct"] <= C.OBSTACLE_MAX


def test_default_preset_equals_the_default_settings():
    assert _settings(C.PRESETS["Standardfall (Voreinstellung)"]) == ev.Settings()


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_preset_a_star_ratio_stays_in_its_measured_band_and_a_star_is_optimal(name):
    p = C.PRESETS[name]
    lo, hi = C.PRESET_EXPECTED_BANDS[name]
    seeds = C.SWEEP_SEEDS if p["network"] == "grid" else (p["seed"],)
    for seed in seeds:
        a = ev.analyse(_settings(p, seed=seed))
        assert lo <= a.astar_ratio <= hi, (seed, a.astar_ratio)
        assert abs(a.astar_gap) < 1e-9


def test_trap_preset_shows_gbfs_failing_where_a_star_succeeds():
    a = ev.analyse(_settings(C.PRESETS["Handgebaute Heuristik-Falle"]))
    assert a.gbfs_gap > 5.0 and abs(a.astar_gap) < 1e-9


def test_many_obstacles_preset_has_a_lower_a_star_ratio_than_the_open_field_preset():
    open_field = ev.run_config(_settings(C.PRESETS["Offenes Feld (engste Heuristik)"]))
    many = ev.run_config(_settings(C.PRESETS["Viele Hindernisse (lockere Heuristik)"]))
    assert open_field["astar_ratio"] > many["astar_ratio"] + 0.15
    assert open_field["tightness"] > many["tightness"] + 0.1


def test_bounds_and_permalink_constants():
    assert P.bounds("side_slider") == (C.SIDE_MIN, C.SIDE_MAX)
    assert P.bounds("seed_input") == (0, C.SEED_MAX)
    assert len({spec.url_param for spec in P.SETTING_SPECS.values()}) == len(P.SETTING_SPECS)


def test_network_permalink_roundtrip():
    assert P._network_from_str("trap") == "trap"
    with pytest.raises(ValueError):
        P._network_from_str("nope")
