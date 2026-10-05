"""Unabhängiges Orakel für die drei Suchen: scipy-Dijkstra (andere Implementierung als der Suchkern) liefert die wahren
Distanzen; daraus folgen Optimalität, die Konsistenz der Heuristik und die Schranken für die Zahl der Expansionen von
A* (alle Knoten mit f < C* müssen, kein Knoten mit f > C* darf expandiert werden). GBFS wird zusätzlich mit einer
eigenen, listenbasierten Neuimplementierung verglichen. Klein und schnell."""

import math

import numpy as np
import pytest

import astar_algorithm as A
import astar_scenario as S

sparse = pytest.importorskip("scipy.sparse")
csgraph = pytest.importorskip("scipy.sparse.csgraph")


def _distances_from(graph, source):
    rows, cols, vals = [], [], []
    for u in range(graph.n):
        for v, w in zip(graph.neighbors[u], graph.weights[u]):
            rows.append(u)
            cols.append(v)
            vals.append(w)
    matrix = sparse.csr_matrix((vals, (rows, cols)), shape=(graph.n, graph.n))
    return csgraph.dijkstra(matrix, indices=source)


def _reference_gbfs_order(graph, start, goal):
    h = np.hypot(*(graph.xy - graph.xy[goal]).T)
    opened, seen, closed, counter = [(h[start], 0, start)], {start}, [], 1
    while opened:
        k = min(range(len(opened)), key=lambda i: (opened[i][0], opened[i][1]))
        _, _, u = opened.pop(k)
        closed.append(u)
        if u == goal:
            break
        for v in graph.neighbors[u]:
            if v not in seen:
                seen.add(v)
                opened.append((h[v], counter, v))
                counter += 1
    return closed


@pytest.mark.parametrize("seed", range(40))
def test_search_results_against_scipy_dijkstra(seed):
    side, pct = 4 + seed % 7, (seed % 5) * 10
    inst = S.grid_instance(side, pct, 5000 + seed)
    g, s, t = inst.graph, inst.start, inst.goal
    ds, dt = _distances_from(g, s), _distances_from(g, t)
    h = A.heuristic(g.xy, t)
    assert np.all(h <= dt + 1e-9)                                                  # zulässig
    assert all(h[u] <= w + h[v] + 1e-9 for u in range(g.n) for v, w in zip(g.neighbors[u], g.weights[u]))  # konsistent
    c_star = ds[t]
    astar, ucs, gbfs = A.a_star(g, s, t), A.uniform_cost_search(g, s, t), A.greedy_best_first(g, s, t)
    assert astar.cost == pytest.approx(c_star, abs=1e-9) and ucs.cost == pytest.approx(c_star, abs=1e-9)
    assert gbfs.cost >= c_star - 1e-9
    f = ds + h
    assert set(np.where(f < c_star - 1e-9)[0]) <= set(astar.order)                # nichts mit f < C* ausgelassen
    assert all(f[x] <= c_star + 1e-9 for x in astar.order)                         # nichts mit f > C* expandiert
    assert set(np.where(ds < c_star - 1e-9)[0]) <= set(ucs.order)
    assert all(ds[x] <= c_star + 1e-9 for x in ucs.order)
    assert gbfs.order == _reference_gbfs_order(g, s, t)


def test_trap_instance_oracle():
    inst = S.trap_instance()
    ds = _distances_from(inst.graph, inst.start)
    gbfs = A.greedy_best_first(inst.graph, inst.start, inst.goal)
    assert A.a_star(inst.graph, inst.start, inst.goal).cost == pytest.approx(ds[inst.goal], abs=1e-9)
    assert 100 * (gbfs.cost / ds[inst.goal] - 1) == pytest.approx(7.47, abs=0.01)
    assert not math.isinf(gbfs.cost)
