"""A* - optimal UND informiert, aber nur teilweise so schnell wie Greedy Best-First - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Zweites Stück der Heuristische-Baumsuche-Linie der "Konzepte"-Reihe, direkte Antwort auf die Schwäche der Wurzel
(greedy-best-first-demo): Greedy Best-First Search ignoriert den bisherigen Pfadwert g(n) und findet deshalb nicht
garantiert den kürzesten Pfad. A* wählt stattdessen nach f(n) = g(n) + h(n) und ist mit einer zulässigen Heuristik
beweisbar optimal. Bekommt man damit BEIDES - Optimalität und den Effizienzvorsprung der Greedy-Suche? Muss
gemessen werden, nicht angenommen.

Lauffähig mit: streamlit run app.py
"""

from dataclasses import replace

import streamlit as st

import astar_constants as C
from astar_evaluation import SWEEP_LABELS, Settings, analyse, astar_worse_than_ucs_share, sweep
from astar_presets import (
    apply_preset,
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sync_query_params,
)
from astar_visualization import (
    ASTAR_COLOR,
    EXPANDED_COLOR,
    GBFS_COLOR,
    UCS_COLOR,
    build_expansion_step,
    build_instance,
    build_paths,
    build_sweep,
)

st.set_page_config(page_title="A* – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _sweep(param, base):
    return sweep(param, base)


@st.cache_data(show_spinner=False)
def _worse_share(base, seeds):
    return astar_worse_than_ucs_share(base, seeds)


SEARCH_LABELS = {"gbfs": "Greedy Best-First", "astar": "A*", "ucs": "Uniform-Cost-Search"}
SEARCH_COLORS = {"gbfs": GBFS_COLOR, "astar": ASTAR_COLOR, "ucs": UCS_COLOR}

st.title("⭐ A* – optimal und informiert")
st.markdown(
    """
**Zweites Stück der Heuristische-Baumsuche-Linie** - die direkte Antwort auf die Schwäche der Wurzel
(`greedy-best-first-demo`): Greedy Best-First Search (GBFS) wählt den nächsten Knoten nur nach der Heuristik
**h(n)** und ignoriert den bisherigen Pfadwert **g(n)** - schnell, aber nicht optimal.

**A\\*** wählt nach **f(n) = g(n) + h(n)**: mit einer zulässigen Heuristik (h überschätzt den Restweg nie) ist der
gefundene Pfad beweisbar der kürzeste. Bekommt man damit wirklich **beides** - die Optimalität von
Uniform-Cost-Search UND den Effizienzvorsprung der Greedy-Suche? Oder kostet die Garantie den Vorsprung fast
vollständig?
"""
)
st.caption(
    "Setzt direkt auf der Wurzel auf ([greedy-best-first-demo](https://github.com/sebastian-hanisch/greedy-best-first-demo)): "
    "derselbe Graph, dieselbe Instanz, derselbe Suchkern - A* ist dort nur eine dritte Prioritätsformel. Weitere "
    "Geschwister: Beam Search → {Diverse Beam Search, Monobeam}, Iterative Deepening A* (IDA*), Monte Carlo "
    "Tree Search (MCTS), Beam Search + A* → Beam Stack Search."
)

with st.expander("So funktioniert A*", expanded=True):
    st.markdown(
        """
1. Dieselbe Prioritätswarteschlange wie bei GBFS und Uniform-Cost-Search - nur die **Priorität** ist anders.
2. **GBFS:** Priorität = h(n) (nur "wie nah am Ziel sieht das aus?"). **UCS:** Priorität = g(n) (nur "wie viel
   habe ich bisher gezahlt?"). **A\\*:** Priorität = g(n) + h(n) - beides zusammen.
3. Findet A* einen billigeren Weg zu einem noch nicht expandierten Knoten, bekommt der Knoten den besseren
   Elternknoten (wie bei UCS, nötig für die Optimalität) - GBFS behält dagegen immer den ersten.
4. Da h(n) der geradlinige Abstand ist und Kantengewichte echte Abstände sind, ist h automatisch zulässig - A\\*
   erbt daraus die Optimalitätsgarantie, ohne dass sie hier neu bewiesen werden müsste (im Test geprüft).
        """
    )

if C.PRESETS:
    st.caption("🎯 Schnellstart – ein Beispielszenario laden:")
    preset_names = list(C.PRESETS.keys())
    for row in (preset_names[:3], preset_names[3:]):
        if not row:
            continue
        cols = st.columns(len(row))
        for col, name in zip(cols, row):
            with col:
                st.button(name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP.get(name, ""), key=f"preset_{name}")

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    st.header("⚙️ Einstellungen")
    network = st.radio("Instanz", options=["grid", "trap"], format_func=lambda n: "Raster" if n == "grid" else "Handgebaute Heuristik-Falle",
                        key="network_select", horizontal=True, help="Die Falle ist ein fester, von Hand gebauter Graph - Rastergröße/Hindernisdichte/Seed wirken dort nicht.")
    if network == "grid":
        side = st.slider("Rastergröße (Seitenlänge)", *bounds("side_slider"), key="side_slider")
        obstacle_pct = st.slider("Hindernisdichte [%]", *bounds("obstacle_slider"), key="obstacle_slider", step=C.OBSTACLE_STEP,
                                  help="Mehr Hindernisse machen die geradlinige Heuristik lockerer - A*s Vorsprung ggü. UCS bricht bei 40 % ein.")
        seed = st.number_input("Zufalls-Seed der Instanz", *bounds("seed_input"), key="seed_input", step=1)
        st.button("🎲 Neue Instanz generieren", width="stretch", on_click=randomize_seed)
    else:
        side, obstacle_pct, seed = C.DEFAULT_SIDE, C.DEFAULT_OBSTACLE, C.DEFAULT_SEED

sync_query_params({"network_select": network, "side_slider": int(side), "obstacle_slider": int(obstacle_pct), "seed_input": int(seed)})

settings = Settings(network, int(side), int(obstacle_pct), int(seed))
a = _analysis(settings)
results = {"gbfs": a.gbfs, "astar": a.astar, "ucs": a.ucs}

# --- A* in Aktion ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 A* in Aktion")
STEP_LABELS = {1: "1 · Instanz", 2: "2 · Suche in Aktion", 3: "3 · Ergebnis"}
step = st.select_slider("Schritt", options=list(STEP_LABELS), key="astar_step", format_func=lambda s: STEP_LABELS[s])

if step == 1:
    st.markdown(f"**{a.inst.graph.n} Zellen** ({len(a.inst.blocked_xy)} Hindernisse), Start (grün) und Ziel (rot)")
    st.plotly_chart(build_instance(a.inst), width="stretch", key="s1_map")
elif step == 2:
    which = st.radio("Welche Suche beobachten?", options=list(SEARCH_LABELS), format_func=lambda k: SEARCH_LABELS[k], key="watch_select", horizontal=True)
    order = results[which].order
    expand_step = st.slider("Expandierte Knoten (Reihenfolge der gewählten Suche)", 0, len(order), len(order))
    st.plotly_chart(build_expansion_step(a.inst, order, expand_step, color=SEARCH_COLORS[which]), width="stretch", key="s2_map")
    st.caption(
        f"{SEARCH_LABELS[which]} expandiert {len(order)} Knoten bis zum Ziel - GBFS {a.gbfs.expansions}, A* {a.astar.expansions}, "
        f"UCS {a.ucs.expansions}. GBFS läuft schmal auf das Ziel zu, A* erkundet eine Ellipse um die Luftlinie, UCS einen Kreis um den Start."
    )
else:
    st.markdown(
        f"**GBFS**: {a.gbfs.cost:.2f} km (Lücke {a.gbfs_gap:.2f} %) – **A\\***: {a.astar.cost:.2f} km (Lücke {a.astar_gap:.2f} %) – "
        f"**UCS**: {a.ucs.cost:.2f} km (optimal)"
    )
    st.plotly_chart(build_paths(a.inst, a.gbfs.path, a.astar.path, a.ucs.path), width="stretch", key="s3_map")

st.markdown("---")

# --- Ergebnis ----------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Was die Suchen gefunden haben")
st.caption(
    "**Effizienzverhältnis:** UCS-Expansionen / Expansionen der jeweiligen Suche (>1 = effizienter als UCS). "
    "**Behaltener Anteil:** wie viel von GBFS' Effizienzvorsprung A* behält (0 % = A* bringt ggü. UCS nichts, 100 % = so schnell wie GBFS)."
)
m1, m2, m3, m4 = st.columns(4)
m1.metric("A*: Lücke", f"{a.astar_gap:.2f} %", delta=f"GBFS {a.gbfs_gap:.2f} %", delta_color="off")
m2.metric("A*: Effizienz", f"{a.astar_ratio:.2f}x", delta=f"{a.astar.expansions} vs. {a.ucs.expansions} Expansionen", delta_color="off")
m3.metric("GBFS: Effizienz", f"{a.gbfs_ratio:.2f}x", delta=f"{a.gbfs.expansions} vs. {a.ucs.expansions} Expansionen", delta_color="off")
kept = a.kept_share
m4.metric("Behaltener Vorsprung", "-" if kept != kept else f"{kept:.0f} %", delta=f"Heuristik-Enge {a.tightness:.2f}", delta_color="off")
st.caption("**Lücke:** Optimalitätslücke ggü. UCS. **Effizienz:** Effizienzverhältnis. **Heuristik-Enge:** h(Start) / tatsächlicher kürzester Weg (1.0 = perfekt). Je lockerer, desto breiter muss A* suchen.")

st.markdown("---")

# --- Sweeps ------------------------------------------------------------------------------------------------------------------------------------

if network == "grid":
    st.subheader("📐 Wie stark hängt der Vorsprung von Hindernisdichte und Rastergröße ab?")
    sweep_param = st.selectbox("Welcher Regler soll durchgefahren werden?", list(SWEEP_LABELS), format_func=lambda k: SWEEP_LABELS[k], key="sweep_select")
    metric = st.radio("Kennzahl", options=["ratio", "kept", "tight"],
                       format_func=lambda k: {"ratio": "Effizienzverhältnis (x)", "kept": "Behaltener GBFS-Vorsprung (%)", "tight": "Heuristik-Enge"}[k],
                       key="sweep_metric", horizontal=True)
    base_sweep = replace(settings, seed=0)
    if st.button("Sweep über 5 feste Instanzen berechnen", key="sweep_start"):
        st.session_state["sweep_done"] = st.session_state.get("sweep_done", set()) | {(sweep_param, base_sweep)}
    if (sweep_param, base_sweep) in st.session_state.get("sweep_done", set()):
        rows_sweep = _sweep(sweep_param, base_sweep)
        if metric == "ratio":
            series, label = [("gbfs_ratio", "Greedy Best-First", GBFS_COLOR), ("astar_ratio", "A*", ASTAR_COLOR)], "Effizienzverhältnis ggü. UCS (x)"
        elif metric == "kept":
            series, label = [("kept_share", "Von A* behaltener Anteil", ASTAR_COLOR)], "Behaltener GBFS-Vorsprung (%)"
        else:
            series, label = [("tightness", "h(Start) / wahrer Weg", EXPANDED_COLOR)], "Heuristik-Enge"
        st.plotly_chart(build_sweep(rows_sweep, SWEEP_LABELS[sweep_param], series, label), width="stretch", key="sweep_chart")
        st.caption("Mittel über 5 feste Instanzen (Seeds 100000–100004, getrennt vom Seed oben). Optimalitätslücke von A*: in jedem Punkt 0 %.")

    st.markdown("---")

    st.subheader("🔬 Expandiert A* je MEHR Knoten als UCS?")
    st.caption("Für eine zulässige Heuristik nicht zu erwarten - hier trotzdem direkt geprüft, über die 5 festen Sweep-Instanzen bei der aktuellen Hindernisdichte.")
    if st.button("Prüfen", key="worse_start"):
        st.session_state["worse_on"] = True
    if st.session_state.get("worse_on"):
        worse, total = _worse_share(base_sweep, C.SWEEP_SEEDS)
        if worse == 0:
            st.success(f"In allen {total} geprüften Instanzen hat A* NIE mehr Knoten expandiert als UCS.")
        else:
            st.warning(f"In {worse} von {total} Instanzen hat A* mehr Knoten expandiert als UCS.")

    st.markdown("---")

# --- Grenzen -----------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **A\\* behält den Großteil von GBFS' Effizienzvorsprung** | Gemessen NICHT: im Mittel nur 32 % (1.38x ggü. UCS, GBFS 4.99x). Der Vorsprung wächst zudem nicht mit der Rastergröße (1.38x bei 6, 1.39x bei 22, GBFS 2.8x bis 8.5x). | (kein Nachfolger nötig - eine echte, gemessene Eigenschaft, keine Lücke) |
| **Die geradlinige Heuristik ist eng genug** | Auf diesen Vierer-Rastern liegt h(Start) nur bei 0.81 (offen) bis 0.61 (40 % Hindernisse) des wahren Wegs - A* muss ein breites Gebiet erkunden. Mit dem exakten Restweg als h expandierte A\\* im Test (eine Instanz) nur die Knoten des optimalen Pfads. | bessere Heuristiken (hier nicht gebaut) |
| **Speicher ist unbegrenzt** | A* hält die gesamte Grenzmenge im Speicher - auf riesigen Graphen das eigentliche Problem. | **Iterative Deepening A\\*** (IDA\\*) |
| **Eine Heuristik ist verfügbar** | Ohne brauchbare Heuristik (h ≡ 0) reduziert sich A\\* exakt auf UCS - im Test nachgewiesen. | **Monte Carlo Tree Search** (bewertet ohne Heuristik) |
| **Synthetische Instanzen:** ein Raster mit Jitter, Vierer-Nachbarschaft, keine Zeitfenster, keine gerichteten Kanten. | | |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Heuristik.** $h(n) = \lVert xy_n - xy_{\text{Ziel}} \rVert_2$ - zulässig, da Kantengewichte echte euklidische
Abstände sind (Dreiecksungleichung).

**Prioritäten.** GBFS: $f(n) = h(n)$. UCS: $f(n) = g(n)$. **A\*:** $f(n) = g(n) + h(n)$.

**Optimalität.** Ist $h$ zulässig ($h(n) \le h^*(n)$, dem wahren Restweg), so findet A* einen kürzesten Pfad.
Sonderfälle, im Test nachgewiesen: $h \equiv 0$ ergibt exakt UCS; $h = h^*$ ergibt (auf der Testinstanz) eine Suche, die nur die
Knoten des optimalen Pfads expandiert.

**Behaltener Vorsprung.** $\dfrac{E_{\text{UCS}} - E_{\text{A*}}}{E_{\text{UCS}} - E_{\text{GBFS}}}$ mit $E$ = Knoten-Expansionen.

**Heuristik-Enge.** $h(\text{Start}) / L_{\text{opt}}$.

**Literatur.** Hart, P. E., Nilsson, N. J., & Raphael, B. (1968). *A Formal Basis for the Heuristic Determination
of Minimum Cost Paths.* IEEE Transactions on Systems Science and Cybernetics, 4(2), 100-107.

Implementiert in `astar_algorithm.py` (gemeinsamer Suchkern `_search`, dritter Wrapper `a_star`),
`astar_graph.py`/`astar_scenario.py` (Graph, Raster- und Fallen-Instanzen, Kopie aus der Wurzel),
`astar_evaluation.py` (Drei-Wege-Kennzahlen, Sweeps).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zur Reihe: [Heuristische Baumsuche: Greedy bis MCTS](https://sebastianhanisch.net/konzepte-heuristische-baumsuche.html)."
)
