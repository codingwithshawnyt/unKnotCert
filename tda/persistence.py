"""
Persistence computation and visualization for state graphs.

The Squeeze Lemma bound for unknot certification is the maximum
filtration value (crossing number) in the connected component of
the state graph that contains both the original diagram and the
unknot. This is a graph-theoretic property, not a persistence
diagram property, since the essential 0-dim class always has
death = infinity.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict, Optional
from collections import deque, defaultdict
import os


def compute_persistence(node_ids: List[str], edge_list: List[Tuple[int, int]],
                        filtration_values: List[int]) -> List[Tuple[float, float]]:
    """
    Compute 0-dimensional persistence diagram from graph filtered by crossing number.

    Uses GUDHI if available, otherwise falls back to union-find.
    """
    try:
        import gudhi
        return _compute_persistence_gudhi(node_ids, edge_list, filtration_values)
    except ImportError:
        return _compute_persistence_unionfind(node_ids, edge_list, filtration_values)


def _compute_persistence_gudhi(node_ids, edge_list, filtration_values):
    """Use GUDHI library for persistence computation."""
    import gudhi

    st = gudhi.SimplexTree()

    for i, fval in enumerate(filtration_values):
        st.insert([i], fval)

    for u, v in edge_list:
        fval = max(filtration_values[u], filtration_values[v])
        st.insert([u, v], fval)

    st.compute_persistence()

    intervals = st.persistence_intervals_in_dimension(0)
    result = []
    for interval in intervals:
        birth, death = interval
        if np.isinf(death):
            death = max(filtration_values) + 1
        result.append((float(birth), float(death)))

    return result


def _compute_persistence_unionfind(node_ids, edge_list, filtration_values):
    """
    Compute 0-dim persistence via union-find on filtration.

    At each filtration level, vertices are born before edges.
    When an edge merges two components, the one born later dies.
    """
    n = len(node_ids)
    if n == 0:
        return []

    edges_with_f = [(max(filtration_values[u], filtration_values[v]), u, v)
                    for u, v in edge_list]

    events = []
    for i in range(n):
        events.append((filtration_values[i], 0, i))
    for fval, u, v in edges_with_f:
        events.append((fval, 1, (u, v)))

    events.sort(key=lambda x: (x[0], x[1]))

    parent = list(range(n))
    rank = [0] * n
    birth_time = list(filtration_values)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx == ry:
            return None
        if birth_time[rx] > birth_time[ry]:
            rx, ry = ry, rx
        dead = ry
        parent[ry] = rx
        if rank[rx] == rank[ry]:
            rank[rx] += 1
        return dead

    intervals = []

    for time, etype, data in events:
        if etype == 0:
            pass
        else:
            u, v = data
            dead = union(u, v)
            if dead is not None:
                intervals.append((float(birth_time[dead]), float(time)))

    # Essential class
    min_birth_node = min(range(n), key=lambda i: birth_time[i])
    intervals.append((float(birth_time[min_birth_node]), float('inf')))

    max_f = max(filtration_values) if filtration_values else 0
    intervals = [(b, d if d != float('inf') else float(max_f + 1))
                 for b, d in intervals]

    return intervals


def squeeze_bound(node_ids, edge_list, filtration_values,
                  unknot_filtration: int = 0,
                  initial_filtration: Optional[int] = None) -> float:
    """Compute the Squeeze Lemma bound: the maximum crossing number
    in the connected component containing the unknot.

    This is NOT derivable from the persistence diagram alone
    (the essential class has death=inf). It requires graph traversal.

    If initial_filtration is given, we require the component to contain
    at least one vertex at that filtration level (the original diagram).
    This avoids picking an isolated cn=0 vertex that isn't connected
    to the diagram's component.
    """
    n = len(filtration_values)
    if n == 0:
        return 0.0

    adj = defaultdict(set)
    for u, v in edge_list:
        adj[u].add(v)
        adj[v].add(u)

    # Find all vertices at the unknot filtration level
    unknot_vertices = [i for i, f in enumerate(filtration_values)
                       if f == unknot_filtration]

    if not unknot_vertices:
        return float(max(filtration_values))

    # BFS from each unknot vertex; return max filtration in the
    # first component that also contains the initial diagram
    best_bound = None
    for start in unknot_vertices:
        visited = {start}
        q = deque([start])
        max_f = filtration_values[start]
        has_initial = (initial_filtration is None or
                       filtration_values[start] == initial_filtration)

        while q:
            node = q.popleft()
            for nb in adj[node]:
                if nb not in visited:
                    visited.add(nb)
                    max_f = max(max_f, filtration_values[nb])
                    if (initial_filtration is not None and
                            filtration_values[nb] == initial_filtration):
                        has_initial = True
                    q.append(nb)

        if has_initial:
            if best_bound is None or max_f < best_bound:
                best_bound = max_f

    # If no component contains both unknot and initial diagram,
    # they are disconnected: return max over all unknot components
    if best_bound is None:
        best_bound = max(filtration_values)

    return float(best_bound)


def plot_diagram(diagram: List[Tuple[float, float]],
                 output_path: str,
                 title: str = "Persistence Diagram"):
    """Generate publication-quality persistence diagram plot and JSON data dump."""
    if not diagram:
        return

    births = [d[0] for d in diagram]
    deaths = [d[1] for d in diagram]

    all_vals = births + deaths
    min_val, max_val = min(all_vals), max(all_vals)

    base = os.path.splitext(output_path)[0]
    json_path = base + '_diagram.json'
    json_data = {
        "title": title,
        "x_label": "Birth (crossing number)",
        "y_label": "Death (crossing number)",
        "points": [[b, d] for b, d in diagram],
        "diagonal": True,
        "axis_range": [min_val, max_val]
    }
    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2)

    plt.figure(figsize=(6, 6))
    plt.scatter(births, deaths, alpha=0.7, s=50, edgecolors='k', linewidth=0.5)
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', alpha=0.5, label='diagonal')

    plt.xlabel('Birth (crossing number)', fontsize=12)
    plt.ylabel('Death (crossing number)', fontsize=12)
    plt.title(title, fontsize=14)
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.axis('equal')
    plt.tight_layout()

    plt.savefig(base + '.png', dpi=300, bbox_inches='tight')
    plt.savefig(base + '.pdf', bbox_inches='tight')
    plt.close()


def summary(diagram: List[Tuple[float, float]]) -> Dict:
    """Return summary statistics of persistence diagram."""
    if not diagram:
        return {'max_persistence': 0, 'num_features': 0}

    persistences = [d - b for b, d in diagram]
    max_pers = max(persistences)
    idx = persistences.index(max_pers)

    return {
        'max_persistence': max_pers,
        'num_features': len(diagram),
        'most_persistent': diagram[idx],
        'mean_persistence': np.mean(persistences) if persistences else 0,
        'min_birth': min(b for b, _ in diagram),
        'max_death': max(d for _, d in diagram)
    }
