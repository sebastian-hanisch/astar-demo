"""Die zentrale Korrektheits-Kette für A*: findet IMMER denselben Pfadwert wie Uniform-Cost-Search (beide optimal),
gegen Brute-Force-Enumeration auf kleinen Instanzen kreuzgeprüft; löst die handgebaute Heuristik-Falle, an der
Greedy Best-First Search scheitert; expandiert nie mehr Knoten als UCS; Pfadkosten stimmen mit einer unabhängigen
Neuberechnung überein; die geerbten GBFS-/UCS-Eigenschaften bleiben in der Kopie intakt."""

import pytest

import astar_algorithm as A
import astar_graph as G
import astar_scenario as S

EPS = 1e-9


def _brute_force_shortest_cost(graph, start, goal):
    best = None
    stack = [(start, [start], 0.0)]
    while stack:
        node, path, cost = stack.pop()
        if node == goal:
            if best is None or cost < best:
                best = cost
            continue
        for v, w in zip(graph.neighbors[node], graph.weights[node]):
            if v not in path:
                stack.append((v, path + [v], cost + w))
    return best


@pytest.mark.parametrize("seed", range(15))
def test_a_star_finds_the_true_shortest_path_cost(seed):
    inst = S.grid_instance(side=5, obstacle_pct=15, seed=seed)
    result = A.a_star(inst.graph, inst.start, inst.goal)
    brute = _brute_force_shortest_cost(inst.graph, inst.start, inst.goal)
    assert result.cost == pytest.approx(brute, abs=1e-6)


def test_a_star_matches_brute_force_on_the_trap_instance():
    inst = S.trap_instance()
    result = A.a_star(inst.graph, inst.start, inst.goal)
    assert result.cost == pytest.approx(_brute_force_shortest_cost(inst.graph, inst.start, inst.goal), abs=1e-6)


@pytest.mark.parametrize("seed", range(40))
def test_a_star_cost_always_equals_uniform_cost_search(seed):
    inst = S.grid_instance(side=12, obstacle_pct=(seed % 5) * 10, seed=seed)
    a = A.a_star(inst.graph, inst.start, inst.goal)
    u = A.uniform_cost_search(inst.graph, inst.start, inst.goal)
    assert a.cost == pytest.approx(u.cost, abs=1e-9)


def test_a_star_solves_the_trap_where_greedy_best_first_fails():
    """Der direkte Beweis, dass g(n) im Suchkern etwas bewirkt: dieselbe Instanz, an der GBFS den längeren
    Köder-Korridor nimmt, findet A* den kürzeren Umweg."""
    inst = S.trap_instance()
    gbfs = A.greedy_best_first(inst.graph, inst.start, inst.goal)
    astar = A.a_star(inst.graph, inst.start, inst.goal)
    ucs = A.uniform_cost_search(inst.graph, inst.start, inst.goal)
    assert gbfs.cost > ucs.cost + 0.5
    assert astar.cost == pytest.approx(ucs.cost, abs=1e-9)
    assert astar.path == ucs.path != gbfs.path


@pytest.mark.parametrize("seed", range(60))
def test_a_star_never_expands_more_nodes_than_uniform_cost_search(seed):
    inst = S.grid_instance(side=14, obstacle_pct=(seed % 5) * 10, seed=seed)
    a = A.a_star(inst.graph, inst.start, inst.goal)
    u = A.uniform_cost_search(inst.graph, inst.start, inst.goal)
    assert a.expansions <= u.expansions


@pytest.mark.parametrize("seed", range(20))
def test_returned_costs_match_an_independent_recomputation(seed):
    inst = S.grid_instance(side=12, obstacle_pct=25, seed=seed)
    for search in (A.greedy_best_first, A.a_star, A.uniform_cost_search):
        result = search(inst.graph, inst.start, inst.goal)
        assert G.path_cost(inst.graph, result.path) == pytest.approx(result.cost, abs=1e-6)


@pytest.mark.parametrize("seed", range(20))
def test_a_star_returns_a_valid_connected_path(seed):
    inst = S.grid_instance(side=10, obstacle_pct=30, seed=seed)
    result = A.a_star(inst.graph, inst.start, inst.goal)
    assert result.path[0] == inst.start and result.path[-1] == inst.goal
    assert len(set(result.path)) == len(result.path)
    for u, v in zip(result.path[:-1], result.path[1:]):
        assert v in inst.graph.neighbors[u]


def test_no_path_is_correctly_reported_for_disconnected_graphs():
    graph = G.from_edges(4, [(0, 0), (1, 0), (2, 0), (3, 0)], [(0, 1, 1.0), (2, 3, 1.0)])
    for search in (A.greedy_best_first, A.a_star, A.uniform_cost_search):
        result = search(graph, 0, 3)
        assert result.path == [] and result.cost == float("inf")


@pytest.mark.parametrize("seed", range(10))
def test_heuristic_is_admissible_on_generated_instances(seed):
    """A*s Optimalität hängt an genau dieser Eigenschaft: h(n) darf den tatsächlichen Restweg nie überschätzen."""
    inst = S.grid_instance(side=8, obstacle_pct=20, seed=seed)
    h = A.heuristic(inst.graph.xy, inst.goal)
    for node in range(inst.graph.n):
        true_dist = A.uniform_cost_search(inst.graph, node, inst.goal).cost
        if true_dist == float("inf"):
            continue
        assert h[node] <= true_dist + EPS


def test_a_star_is_deterministic():
    inst = S.grid_instance(side=12, obstacle_pct=25, seed=3)
    r1 = A.a_star(inst.graph, inst.start, inst.goal)
    r2 = A.a_star(inst.graph, inst.start, inst.goal)
    assert r1.path == r2.path and r1.cost == r2.cost and r1.expansions == r2.expansions and r1.order == r2.order


def test_inherited_greedy_best_first_never_beats_the_optimum():
    for seed in range(30):
        inst = S.grid_instance(side=10, obstacle_pct=25, seed=seed)
        gbfs = A.greedy_best_first(inst.graph, inst.start, inst.goal)
        ucs = A.uniform_cost_search(inst.graph, inst.start, inst.goal)
        assert gbfs.cost >= ucs.cost - EPS


def test_a_star_with_a_zero_heuristic_would_equal_uniform_cost_search():
    """Sonderfall: mit h == 0 ist f(n) = g(n) - A* reduziert sich exakt auf UCS (gleiche Reihenfolge, gleiche
    Expansionen). Über den gemeinsamen Suchkern direkt geprüft."""
    inst = S.grid_instance(side=10, obstacle_pct=20, seed=5)
    zero_h = A._search(inst.graph, inst.start, inst.goal, lambda node, g: g + 0.0, relax=True)
    ucs = A.uniform_cost_search(inst.graph, inst.start, inst.goal)
    assert zero_h.order == ucs.order and zero_h.cost == ucs.cost


def test_a_star_with_a_perfect_heuristic_expands_only_the_optimal_path():
    """Sonderfall in die andere Richtung: mit dem EXAKTEN Restweg als h expandiert A* (bei eindeutigem Optimum)
    ausschließlich Knoten auf dem optimalen Pfad - die theoretische Untergrenze dessen, was eine Heuristik
    überhaupt leisten kann. Zeigt, wie viel Luft die geradlinige Heuristik dieser Demo noch lässt."""
    inst = S.grid_instance(side=10, obstacle_pct=20, seed=5)
    true = [A.uniform_cost_search(inst.graph, n, inst.goal).cost for n in range(inst.graph.n)]
    perfect = A._search(inst.graph, inst.start, inst.goal, lambda node, g: g + true[node], relax=True)
    ucs = A.uniform_cost_search(inst.graph, inst.start, inst.goal)
    assert perfect.cost == pytest.approx(ucs.cost, abs=1e-9)
    assert perfect.expansions == len(ucs.path)
