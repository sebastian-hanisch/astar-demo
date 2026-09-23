"""AppTest-Rauchtests: Voreinstellung, jedes Preset, jeder Schritt, beide Instanz-Typen, Randwerte, Würfel-Knopf,
Permalink-Grenzen, Sweeps/Experimente auf Abruf, Footer."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import astar_constants as C

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def _run(astar_step=1, **state):
    at = AppTest.from_file(APP, default_timeout=60)
    for k, v in state.items():
        at.session_state[k] = v
    at.run()
    if astar_step != 1:
        at.select_slider(key="astar_step").set_value(astar_step).run()
    return at


def _ok(at):
    assert not at.exception, [e.value for e in at.exception]


def test_default_run_has_no_exception():
    at = _run()
    _ok(at)
    assert at.metric


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_every_preset_button_runs(name):
    at = _run()
    next(b for b in at.button if b.key == f"preset_{name}").click().run()
    _ok(at)
    p = C.PRESETS[name]
    assert at.session_state["network_select"] == p["network"]
    assert at.metric


@pytest.mark.parametrize("step", [1, 2, 3])
def test_every_step_runs_for_both_networks(step):
    for network in ("grid", "trap"):
        at = _run(network_select=network, astar_step=step)
        _ok(at)
        assert at.get("plotly_chart") and at.session_state["astar_step"] == step


@pytest.mark.parametrize("kw", [
    dict(side_slider=C.SIDE_MIN), dict(side_slider=C.SIDE_MAX),
    dict(obstacle_slider=C.OBSTACLE_MIN), dict(obstacle_slider=C.OBSTACLE_MAX),
])
def test_extreme_settings_run(kw):
    _ok(_run(**kw))


def test_dice_button_changes_the_seed():
    at = _run()
    old = at.session_state["seed_input"]
    next(b for b in at.button if b.label == "🎲 Neue Instanz generieren").click().run()
    _ok(at)
    assert at.session_state["seed_input"] != old


def test_permalink_values_are_clamped_and_snapped():
    at = AppTest.from_file(APP, default_timeout=60)
    at.query_params["side"] = "9999"
    at.query_params["obstacle"] = "9999"
    at.query_params["network"] = "trap"
    at.run()
    _ok(at)
    assert at.session_state["side_slider"] == C.SIDE_MAX
    assert at.session_state["obstacle_slider"] == C.OBSTACLE_MAX
    assert at.session_state["network_select"] == "trap"


def test_sidebar_hides_grid_only_controls_for_the_trap_network():
    at = _run(network_select="trap")
    _ok(at)
    assert not any(s.key == "side_slider" for s in at.slider)


def test_sweeps_run_on_demand():
    at = _run(side_slider=8)
    at.selectbox(key="sweep_select").set_value("obstacle_pct").run()
    next(b for b in at.button if b.key == "sweep_start").click().run()
    _ok(at)
    assert at.get("plotly_chart")


def test_worse_expansion_experiment_runs_on_demand():
    at = _run(side_slider=8)
    next(b for b in at.button if b.key == "worse_start").click().run()
    _ok(at)
    assert at.session_state["worse_on"]


def test_footer_and_grenzen_are_present():
    at = _run()
    assert any("Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net)" in c.value for c in at.caption)
    assert any("Wo die Annahmen enden" in s.value for s in at.subheader)
    assert any("behält den Großteil von GBFS" in m.value for m in at.markdown)


@pytest.mark.parametrize("which", ["gbfs", "astar", "ucs"])
def test_step_two_lets_you_watch_each_of_the_three_searches(which):
    at = _run(astar_step=2, watch_select=which)
    _ok(at)
    assert at.get("plotly_chart")


def test_changing_the_instance_while_watching_step_two_does_not_crash():
    """Die Schranken des Expansions-Reglers hängen an der gewählten Suche und Instanz - ein Wechsel darf keinen
    Wert außerhalb der neuen Grenzen zurücklassen."""
    at = _run(astar_step=2, side_slider=22)
    _ok(at)
    at.session_state["side_slider"] = C.SIDE_MIN
    at.run()
    _ok(at)
    at.session_state["network_select"] = "trap"
    at.run()
    _ok(at)


def test_the_four_metrics_are_shown():
    at = _run()
    labels = {m.label for m in at.metric}
    assert {"A*: Lücke", "A*: Effizienz", "GBFS: Effizienz", "Behaltener Vorsprung"} <= labels
