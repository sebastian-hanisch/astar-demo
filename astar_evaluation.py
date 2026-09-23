"""Auswertung: A* im Drei-Wege-Vergleich mit Greedy Best-First Search (GBFS, schnell aber nicht optimal) und
Uniform-Cost-Search (UCS, optimal aber ohne Richtungsinformation) - derselbe Graph, derselbe Suchkern, nur eine
andere Prioritätsformel (siehe `astar_algorithm.py`). Kennzahlen wie in der Wurzel (Optimalitätslücke,
Effizienzverhältnis ggü. UCS), jetzt für GBFS UND A* berichtet, plus **Anteil des GBFS-Vorsprungs, den A* behält**:
(Exp. UCS - Exp. A*) / (Exp. UCS - Exp. GBFS) - 0 % heißt A* bringt gar nichts ggü. UCS, 100 % heißt A* ist so
schnell wie GBFS. Vollständig deterministisch, kein Bewertungsbudget, kein Ketten-Seed."""

from dataclasses import dataclass, replace
from functools import lru_cache

import numpy as np

import astar_algorithm as A
import astar_constants as C
import astar_scenario as S


@dataclass(frozen=True)
class Settings:
    network: str = "grid"           # "grid" oder "trap" (die handgebaute Sackgassen-Instanz aus der Wurzel)
    side: int = C.DEFAULT_SIDE
    obstacle_pct: int = C.DEFAULT_OBSTACLE
    seed: int = C.DEFAULT_SEED


@lru_cache(maxsize=256)
def instance(side, obstacle_pct, seed):
    return S.grid_instance(side, obstacle_pct, seed)


def _gap(result, reference):
    if not reference.path or reference.cost <= 0:
        return 0.0
    return 100.0 * (result.cost - reference.cost) / reference.cost


@dataclass
class Analysis:
    settings: Settings
    inst: object
    gbfs: A.SearchResult
    astar: A.SearchResult
    ucs: A.SearchResult

    @property
    def gbfs_gap(self):
        return _gap(self.gbfs, self.ucs)

    @property
    def astar_gap(self):
        return _gap(self.astar, self.ucs)

    @property
    def gbfs_ratio(self):
        """UCS-Expansionen / GBFS-Expansionen (>1: GBFS effizienter als UCS)."""
        return self.ucs.expansions / self.gbfs.expansions if self.gbfs.expansions > 0 else float("nan")

    @property
    def astar_ratio(self):
        """UCS-Expansionen / A*-Expansionen (>1: A* effizienter als UCS)."""
        return self.ucs.expansions / self.astar.expansions if self.astar.expansions > 0 else float("nan")

    @property
    def tightness(self):
        """Wie eng die Heuristik am Start ist: h(Start) / tatsächlicher kürzester Weg (1.0 = perfekt, kleiner =
        lockerer). Eine lockere Heuristik zwingt A*, ein breites Gebiet zu erkunden - der gemessene Grund dafür,
        dass A* auf diesen Rastern nur einen Teil von GBFS' Effizienzvorsprung behält."""
        if not self.ucs.path or self.ucs.cost <= 0:
            return float("nan")
        h = A.heuristic(self.inst.graph.xy, self.inst.goal)
        return float(h[self.inst.start] / self.ucs.cost)

    @property
    def kept_share(self):
        """Anteil des GBFS-Effizienzvorsprungs (gegenüber UCS), den A* behält, in Prozent. NaN, falls GBFS gar
        keinen Vorsprung hat (Nenner 0)."""
        span = self.ucs.expansions - self.gbfs.expansions
        if span <= 0:
            return float("nan")
        return 100.0 * (self.ucs.expansions - self.astar.expansions) / span


def analyse(settings):
    inst = S.trap_instance() if settings.network == "trap" else instance(settings.side, settings.obstacle_pct, settings.seed)
    gbfs = A.greedy_best_first(inst.graph, inst.start, inst.goal)
    astar = A.a_star(inst.graph, inst.start, inst.goal)
    ucs = A.uniform_cost_search(inst.graph, inst.start, inst.goal)
    return Analysis(settings, inst, gbfs, astar, ucs)


# --- Sweeps --------------------------------------------------------------------------------------------------------------------------------------


def run_config(base, seeds=C.SWEEP_SEEDS, **changes):
    s0 = replace(base, **changes)
    rows = [analyse(replace(s0, seed=seed)) for seed in seeds]

    def mean_sd(values):
        values = [v for v in values if not np.isnan(v)]
        return (float(np.mean(values)), float(np.std(values))) if values else (float("nan"), float("nan"))

    out = {"n_runs": len(rows)}
    for key, values in (
        ("gbfs_gap", [r.gbfs_gap for r in rows]), ("astar_gap", [r.astar_gap for r in rows]),
        ("gbfs_ratio", [r.gbfs_ratio for r in rows]), ("astar_ratio", [r.astar_ratio for r in rows]),
        ("kept_share", [r.kept_share for r in rows]), ("tightness", [r.tightness for r in rows]),
    ):
        out[key], out[f"{key}_sd"] = mean_sd(values)
    out["expansions_gbfs"] = float(np.mean([r.gbfs.expansions for r in rows]))
    out["expansions_astar"] = float(np.mean([r.astar.expansions for r in rows]))
    out["expansions_ucs"] = float(np.mean([r.ucs.expansions for r in rows]))
    return out


SWEEP_VALUES = {"obstacle_pct": C.OBSTACLE_SWEEP, "side": C.SCALING_SIDES}
SWEEP_LABELS = {"obstacle_pct": "Hindernisdichte (%)", "side": "Rastergröße (Seitenlänge)"}


def sweep(param, base=Settings(), values=None):
    values = SWEEP_VALUES[param] if values is None else values
    return [{"value": v, **run_config(base, **{param: v})} for v in values]


def astar_worse_than_ucs_share(base=Settings(), seeds=C.SWEEP_SEEDS):
    """Anzahl Instanzen, in denen A* MEHR Knoten expandiert als UCS - für eine zulässige Heuristik nicht zu
    erwarten, hier gemessen statt vorausgesetzt. Gibt (Anzahl schlechter, Gesamtzahl) zurück."""
    rows = [analyse(replace(base, seed=seed)) for seed in seeds]
    worse = sum(1 for r in rows if r.astar.expansions > r.ucs.expansions)
    return worse, len(rows)
