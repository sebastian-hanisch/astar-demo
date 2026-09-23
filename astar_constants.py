"""Konstanten der A*-Demo: Raster-Geometrie (wortgleich zur Greedy-Best-First-Demo), Regler, Beschriftungen
(Messwerte + Presets folgen nach der Messreihe)."""

AREA = 100.0                     # Kantenlänge des Gebiets in km
JITTER = 0.35                    # Lageabweichung je Zelle, Anteil des Zellenabstands

SIDE_MIN, SIDE_MAX, DEFAULT_SIDE, SIDE_STEP = 5, 25, 12, 1     # Rastergröße (Zellen je Kante)
OBSTACLE_MIN, OBSTACLE_MAX, DEFAULT_OBSTACLE, OBSTACLE_STEP = 0, 40, 15, 5   # Prozent gesperrte Zellen
SEED_MAX = 999999
DEFAULT_SEED = 35

SWEEP_SEEDS = tuple(range(100000, 100005))
SCALING_SIDES = (6, 10, 14, 18, 22)
OBSTACLE_SWEEP = (0, 10, 20, 30, 40)

# --- Gemessene Werte (Mittel über 5 feste Sweep-Instanzen, Seeds 100000-100004; Rastergröße 12, Hindernisdichte
# --- 15 %, sofern nicht anders angegeben; 2026-09-23, alle Werte über ev.run_config/ev.sweep nachgerechnet,
# --- s. tests/test_claims.py). Die GBFS-Zahlen stimmen bytegenau mit greedy-best-first-demo überein (Kopie treu). ---
# ZENTRALE FRAGE - bekommt man mit A* BEIDES (Optimalität UND GBFS' Effizienz)? Optimalität: JA, ohne Ausnahme
#   (Lücke 0.0 % in allen Fällen). Effizienz: NUR TEILWEISE - im Standardfall expandiert A* 90 Knoten (GBFS 24, UCS
#   121): Effizienzverhältnis ggü. UCS 1.38x (GBFS 4.99x). A* behält im Mittel nur 32 % des GBFS-Vorsprungs - die
#   Vorab-Hypothese "A* behält den Großteil davon" ist WIDERLEGT: die Optimalitätsgarantie kostet den größeren Teil
#   des Vorsprungs.
# HINDERNISDICHTE-SWEEP (0/10/20/30/40 %): A*-Effizienzverhältnis 1.47/1.52/1.54/1.49/1.20x, behaltener Anteil
#   37/41/43/44/34 % - bei GBFS sank das Verhältnis monoton (6.26 bis 1.92x), bei A* bleibt es bis 30 % flach und
#   bricht erst bei 40 % ein.
# GRÖSSEN-SWEEP (Rastergröße 6/10/14/18/22): A*-Effizienzverhältnis 1.38/1.45/1.56/1.46/1.39x - WÄCHST NICHT mit der
#   Größe (GBFS: 2.8 bis 8.5x), behaltener Anteil sinkt bei großen Rastern (41 bis 32 %).
# WARUM (gemessen, nicht nur vermutet): die geradlinige Heuristik ist auf diesen Vierer-Rastern LOCKER - h(Start)
#   liegt im Mittel bei nur 0.81 (offenes Feld) bis 0.61 (40 % Hindernisse) des tatsächlichen kürzesten Wegs. Eine
#   lockere Heuristik zwingt A*, ein breites Gebiet zu erkunden. Untergrenze im Test: mit dem EXAKTEN Restweg als h
#   würde A* nur die Knoten des optimalen Pfads expandieren (tests/test_algorithm.py) - A* ist hier durch die
#   Heuristik-Qualität begrenzt, nicht durch den Algorithmus.
# EFFIZIENZ-FRAGE (A* nie schlechter als UCS?): in allen getesteten Instanzen expandiert A* höchstens so viele Knoten
#   wie UCS (60 Zufallsinstanzen im Test plus alle Sweep-Instanzen) - für eine zulässige Heuristik erwartet, hier
#   aber gemessen.
# HANDGEBAUTE HEURISTIK-FALLE: GBFS 7.47 % zu lang (6 Expansionen), A* und UCS beide optimal (7 bzw. 8 Expansionen) -
#   das konkrete Gegenbeispiel aus der Wurzel, an dem g(n) sichtbar den Unterschied macht.

PRESETS = {
    "Standardfall (Voreinstellung)": {"network": "grid", "side": 12, "obstacle_pct": 15, "seed": 35},
    "Handgebaute Heuristik-Falle": {"network": "trap", "side": 12, "obstacle_pct": 15, "seed": 35},
    "Offenes Feld (engste Heuristik)": {"network": "grid", "side": 12, "obstacle_pct": 0, "seed": 35},
    "Viele Hindernisse (lockere Heuristik)": {"network": "grid", "side": 12, "obstacle_pct": 40, "seed": 35},
    "Großes Raster (Vorsprung wächst nicht)": {"network": "grid", "side": 22, "obstacle_pct": 15, "seed": 35},
}
PRESET_HELP = {
    "Standardfall (Voreinstellung)": "Rastergröße 12, Hindernisdichte 15 %: A\\* findet in allen Fällen den optimalen Pfad (Lücke 0 %), expandiert aber im Mittel nur 1.38x weniger Knoten als UCS - GBFS erreicht 4.99x, dafür mit 16.5 % Lücke. A\\* behält im Mittel nur 32 % von GBFS' Vorsprung.",
    "Handgebaute Heuristik-Falle": "Der 8-Knoten-Graph aus der Wurzel: GBFS läuft in den köderhaften Korridor (7.47 % zu lang), A\\* und UCS finden beide den kürzeren Umweg - hier macht g(n) im Suchkern sichtbar den Unterschied.",
    "Offenes Feld (engste Heuristik)": "Keine Hindernisse: die Heuristik ist hier am engsten (h(Start) im Mittel bei 0.81 des wahren Wegs) und A\\* am effizientesten (1.47x ggü. UCS) - aber selbst hier bleibt er weit hinter GBFS (6.26x).",
    "Viele Hindernisse (lockere Heuristik)": "Hindernisdichte 40 %: die geradlinige Heuristik wird locker (h(Start) im Mittel nur 0.61 des wahren Wegs), A\\*s Vorsprung ggü. UCS bricht auf 1.20x ein.",
    "Großes Raster (Vorsprung wächst nicht)": "Rastergröße 22: GBFS' Effizienzvorsprung wächst auf 8.5x, A\\*s bleibt bei 1.39x - der Vorsprung wächst mit der Größe nur, wenn man auf die Optimalitätsgarantie verzichtet.",
}
# Beobachtete Spannweite des A*-Effizienzverhältnisses (UCS-Expansionen / A*-Expansionen) über die 5 festen
# Sweep-Instanzen (mit Sicherheitsabstand) - vollständig deterministisch, die Spannweite kommt allein aus der
# Instanz-Geometrie. Die Falle ist ein fester Graph (8 / 7 = 1.14).
PRESET_EXPECTED_BANDS = {
    "Standardfall (Voreinstellung)": (1.0, 2.0),
    "Handgebaute Heuristik-Falle": (1.1, 1.2),
    "Offenes Feld (engste Heuristik)": (1.2, 2.0),
    "Viele Hindernisse (lockere Heuristik)": (1.0, 1.5),
    "Großes Raster (Vorsprung wächst nicht)": (1.15, 1.8),
}
