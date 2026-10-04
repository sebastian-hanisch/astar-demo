# A* – optimal und informiert – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-astar-demo.streamlit.app/)**

Zweites Stück der **Heuristische-Baumsuche-Linie** der "Konzepte"-Reihe für die Website "Sebastian Hanisch – Operations Research und Machine Learning" - die direkte Antwort auf die Schwäche der Wurzel [greedy-best-first-demo](../greedy-best-first-demo): **Greedy Best-First Search (GBFS)** wählt den nächsten Knoten nur nach der Heuristik h(n) und ignoriert den bisherigen Pfadwert g(n) - schnell, aber nicht optimal. **A\*** (Hart, Nilsson & Raphael 1968) wählt nach **f(n) = g(n) + h(n)** und ist mit einer zulässigen Heuristik beweisbar optimal.

**Einordnung in die Linie:** derselbe Graph, dieselbe Instanz, derselbe Suchkern wie in der Wurzel (`_search`, dort schon korrektheitsgeprüft) - A\* ist dort nur eine **dritte Prioritätsformel**. Verglichen werden drei Suchen: GBFS (schnell, nicht optimal), A\* (die Behauptung: beides) und Uniform-Cost-Search (UCS, optimal, ohne Richtungsinformation - die Referenz).

```
Greedy Best-First Search (Wurzel)                                                          [gebaut]
 ├─ A* → Iterative Deepening A* (IDA*)                                     [A* = DIESES STÜCK, IDA* gebaut]
 ├─ Beam Search → {Diverse Beam Search, Monobeam}                                          [gebaut]
 └─ Monte Carlo Tree Search (MCTS)                                                         [gebaut]
Beam Search + A* → Beam Stack Search (Konvergenzpunkt)                                     [gebaut]
```

Ergebnis in Kürze: **A\* ist ausnahmslos optimal** (Lücke 0.0 % in jedem gemessenen Fall) und expandiert nie mehr Knoten als UCS - aber die Vorab-Hypothese "A\* behält den Großteil von GBFS' Effizienzvorsprung" ist **widerlegt**: im Standardfall behält er nur **32 %** (1.38x weniger Expansionen als UCS, GBFS erreicht 4.99x). Und er wächst nicht mit der Instanzgröße: bei GBFS steigt der Vorsprung von 2.8x auf 8.5x, bei A\* bleibt er bei ~1.4x. Der gemessene Grund: die geradlinige Heuristik ist auf diesen Vierer-Rastern **locker** (h(Start) liegt bei nur 0.81 bis 0.61 des wahren Weges), A\* muss deshalb ein breites Gebiet erkunden.

| Frage | Ergebnis (Rastergröße 12, Hindernisdichte 15 %, sofern nicht anders angegeben; Mittel über 5 feste Instanzen, Seeds 100000–100004; vollständig deterministisch) |
|---|---|
| **Ist A\* optimal?** | ✅ Lücke **0.0 %** bei jeder Hindernisdichte und jeder Rastergröße |
| **Behält A\* GBFS' Effizienzvorsprung?** | ⚠️ nur **32 %** im Standardfall (37/41/43/44/34 % über 0–40 % Hindernisse) - Verhältnis ggü. UCS **1.38x** gegen GBFS **4.99x** (Expansionen 90 gegen 24 gegen 121) |
| **Hindernisdichte-Sweep (0/10/20/30/40 %)** | ⚠️ A\*-Verhältnis **1.47/1.52/1.54/1.49/1.20x** - flach bis 30 %, bricht erst bei 40 % ein (GBFS: 6.26/5.58/4.55/3.21/1.92x, monoton fallend) |
| **Rastergrößen-Sweep (6/10/14/18/22)** | ⚠️ A\*-Verhältnis **1.38/1.45/1.56/1.46/1.39x** - wächst NICHT (GBFS: 2.8/4.1/6.0/7.7/8.5x) |
| **Warum? Heuristik-Enge** | h(Start) / wahrer Weg = **0.81** (0 % Hindernisse), **0.76** (15 %), **0.61** (40 %) - je lockerer, desto breiter sucht A\* |
| **Expandiert A\* je mehr Knoten als UCS?** | ✅ NIE (60 Zufallsinstanzen im Test plus alle Sweep-Instanzen) |
| **Handgebaute Heuristik-Falle** | ✅ GBFS 7.47 % zu lang (6 Expansionen), A\* und UCS beide optimal (7 bzw. 8) |

## Was die Demo zeigt

1. **A\* in Aktion** (Schritt-Slider): **Instanz** → **Suche in Aktion** (eine der drei Suchen wählbar, Regler über die Expansionsreihenfolge - GBFS läuft schmal aufs Ziel zu, A\* erkundet eine Ellipse um die Luftlinie, UCS einen Kreis um den Start) → **Ergebnis** (alle drei Pfade überlagert).
2. **Was die Suchen gefunden haben:** Lücke, Effizienz von A\* und GBFS, behaltener Vorsprung, Heuristik-Enge.
3. **📐 Sweeps** über Hindernisdichte und Rastergröße, wählbare Kennzahl (Effizienzverhältnis beider Suchen / behaltener Anteil / Heuristik-Enge), 5 feste Instanzen ab Seed 100000.
4. **🔬 Experiment:** "Expandiert A\* je MEHR Knoten als UCS?" - für eine zulässige Heuristik nicht zu erwarten, hier trotzdem direkt geprüft.
5. **🚧 Grenzen:** Tabelle "Annahme – was passiert – wer setzt an".

Regler: Instanz (Raster / handgebaute Heuristik-Falle), Rastergröße (5–25), Hindernisdichte (0–40 %), Seed der Instanz (+ 🎲). A\* bringt **keine eigenen Regler** mit (wie jedes "Optimalitätsgarantie"-Stück bewusst schlicht), **kein Bewertungsbudget** und **keinen Ketten-Seed** (vollständig deterministisch).

## Messwerte der Presets

| Preset | GBFS-Lücke | A\*-Effizienz | GBFS-Effizienz | behaltener Anteil (Instanz-Seed 35) |
|---|---|---|---|---|
| Standardfall (Voreinstellung) | 22.53 % | 1.54x | 5.48x | 43 % |
| Handgebaute Heuristik-Falle | 7.47 % | 1.14x | 1.33x | 50 % |
| Offenes Feld (engste Heuristik) | 11.65 % | 1.62x | 6.26x | 46 % |
| Viele Hindernisse (lockere Heuristik) | 12.89 % | 1.21x | 2.93x | 26 % |
| Großes Raster (Vorsprung wächst nicht) | 13.09 % | 1.32x | 9.72x | 27 % |

Die einzelne Instanz (Seed 35) weicht von den Sweep-Mitteln ab (z. B. Standardfall 1.54x gegen 1.38x im Mittel) - die Mittelwerte oben sind die belastbaren Zahlen; jedes Preset prüft sich zusätzlich über die 5 festen Sweep-Instanzen gegen eine gemessene Spannweite (siehe `tests/test_presets.py`).

## Modell und Verfahren

- **Instanz und Graph** (`astar_scenario.py`, `astar_graph.py`): wortgleiche Kopien aus [greedy-best-first-demo](../greedy-best-first-demo) - gestörtes Raster mit Hindernissen, Kantengewicht = echter euklidischer Abstand (macht die Heuristik automatisch zulässig), plus die handgebaute 8-Knoten-Falle.
- **Suchkern** (`astar_algorithm.py`): der `_search(graph, start, goal, priority_fn, relax)`-Kern und `greedy_best_first`/`uniform_cost_search` wortgleich aus der Wurzel, NEU `a_star` (`priority = g(n) + h(n)`, `relax=True` - klassische Dijkstra-Relaxation, nötig für die Optimalität).
- **Auswertung** (`astar_evaluation.py`): Drei-Wege-Kennzahlen, behaltener Anteil = (Exp. UCS − Exp. A\*) / (Exp. UCS − Exp. GBFS), Heuristik-Enge, Sweeps.

## Was nicht funktioniert hat / Grenzen

- **Vorab-Hypothese "A\* behält den Großteil von GBFS' Effizienzvorsprung" - WIDERLEGT.** Im Mittel nur 32 % (Spanne 32-44 % über die Sweeps). Die Optimalitätsgarantie kostet den größeren Teil des Vorsprungs.
- **A\*s Vorsprung wächst nicht mit der Instanzgröße** (1.38x bei Größe 6, 1.39x bei 22), GBFS' schon (2.8x bis 8.5x) - der Vorsprung wächst mit der Größe nur, wenn man auf die Optimalitätsgarantie verzichtet.
- **Der gemessene Grund ist die Heuristik-Qualität, nicht der Algorithmus**: h(Start) liegt bei 0.81 (offenes Feld) bis 0.61 (40 % Hindernisse) des wahren Wegs. Untergrenze (im Test, eine Instanz): mit dem EXAKTEN Restweg als h expandiert A\* nur die Knoten des optimalen Pfads - dazwischen liegt der ganze Spielraum besserer Heuristiken, die hier nicht gebaut werden.
- **Anders als bei GBFS sinkt A\*s Vorsprung nicht monoton mit den Hindernissen**: flach bis 30 %, Einbruch bei 40 % (dort ist die Heuristik am lockersten).
- **Speicher ist unbegrenzt**: A\* hält die gesamte Grenzmenge - auf riesigen Graphen das eigentliche Problem (das Thema des nächsten Kindes dieses Zweigs, IDA\*).
- **Synthetische Instanzen:** ein Raster mit Jitter, Vierer-Nachbarschaft (keine Diagonalen), keine Zeitfenster, keine gerichteten Kanten.

## Verifikation

- **A\* findet IMMER denselben Pfadwert wie UCS**: über 40 Zufallsinstanzen mit 0–40 % Hindernissen UND gegen vollständige Enumeration aller einfachen Pfade (Brute-Force) auf kleinen Instanzen kreuzgeprüft.
- **A\* löst die handgebaute Falle**, an der GBFS scheitert - der direkte Beweis, dass g(n) im Suchkern etwas bewirkt.
- **A\* expandiert nie mehr Knoten als UCS** (60 Zufallsinstanzen).
- **Zwei Sonderfälle direkt nachgewiesen**: mit h ≡ 0 reproduziert A\* die Expansionsreihenfolge von UCS exakt; mit dem exakten Restweg als h expandiert er nur die Knoten des optimalen Pfads.
- **Die Heuristik ist auf den Instanzen dieser Linie tatsächlich zulässig** - gegen UCS-Distanzen von jedem Knoten zum Ziel geprüft (A\*s Optimalität hängt genau daran).
- **Die Kopie ist treu**: die GBFS-Zahlen stimmen bytegenau mit der Wurzel überein (als Test hinterlegt).
- **Alle Zahlen der App-Texte sind als Tests hinterlegt**, über dieselben Auswertungsfunktionen wie die App selbst (`ev.run_config`/`ev.sweep`), NIE über ein Ad-hoc-Skript - auch die Heuristik-Enge, die als Erklärung dient, ist eine echte Auswertungsfunktion und wird per Test belegt; AppTest-Rauchtests (Voreinstellung, jedes Preset, jeder Schritt, beide Instanz-Typen, jede der drei beobachtbaren Suchen, Instanzwechsel im Schritt 2, ausgeblendete Regler bei der Falle, Extremwerte, Permalink-Grenzen, Sweeps/Experiment auf Abruf, Footer).

Literatur: Hart, P. E., Nilsson, N. J., & Raphael, B. (1968). *A Formal Basis for the Heuristic Determination of Minimum Cost Paths.* IEEE Transactions on Systems Science and Cybernetics, 4(2), 100-107.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `app.py` | Streamlit-App: Instanz-Umschalter, Schritte (mit wählbarer Suche), Ergebnis, 📐 Sweeps, 🔬 Experiment, 🚧 Grenzen, Mathe |
| `astar_algorithm.py` | Gemeinsamer Suchkern (Kopie aus der Wurzel) + `a_star` als dritter Wrapper |
| `astar_graph.py`, `astar_scenario.py` | Graph, Raster- und Fallen-Instanz (Kopie aus der Wurzel) |
| `astar_constants.py` | Konstanten, Presets, gemessene Werte |
| `astar_evaluation.py` | Drei-Wege-Kennzahlen, behaltener Anteil, Heuristik-Enge, Sweeps |
| `astar_presets.py`, `astar_visualization.py` | Permalink/Presets, Plotly-Figuren (Expansionsschritte, Drei-Pfade-Überlagerung, Sweeps) |
| `tests/` | Zentrale Korrektheitskette (Brute-Force, Falle, Sonderfälle), Szenario/Auswertung, Aussagen der App, Presets, AppTest |

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zur Reihe: [Heuristische Baumsuche: Greedy bis MCTS](https://sebastianhanisch.net/konzepte-heuristische-baumsuche.html).
