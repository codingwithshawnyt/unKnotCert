"""
Persistence computation and visualization for state graphs.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict, Optional
import os


def compute_persistence(node_ids: List[str], edge_list: List[Tuple[int, int]],
                       filtration_values: List[int]) -> List[Tuple[float, float]]:
    """
    Compute 0-dimensional persistence diagram from graph filtered by crossing number.

    Uses GUDHI if available, otherwise falls back to a simple connected components tracker.
    """
    try:
        import gudhi
        return _compute_persistence_gudhi(node_ids, edge_list, filtration_values)
    except ImportError:
        try:
            import ripser
            return _compute_persistence_ripser(node_ids, edge_list, filtration_values)
        except ImportError:
            return _compute_persistence_fallback(node_ids, edge_list, filtration_values)


def _compute_persistence_gudhi(node_ids, edge_list, filtration_values):
    """Use GUDHI library for persistence computation."""
    import gudhi

    st = gudhi.SimplexTree()

    # Insert vertices with their filtration values
    for i, fval in enumerate(filtration_values):
        st.insert([i], fval)

    # Insert edges with max filtration of endpoints
    for u, v in edge_list:
        fval = max(filtration_values[u], filtration_values[v])
        st.insert([u, v], fval)

    st.compute_persistence()

    # Get 0-dimensional intervals
    intervals = st.persistence_intervals_in_dimension(0)
    result = []
    for interval in intervals:
        birth, death = interval
        if np.isinf(death):
            death = max(filtration_values) + 1
        result.append((float(birth), float(death)))

    return result


def _compute_persistence_ripser(node_ids, edge_list, filtration_values):
    """Fallback using Ripser (requires distance matrix)."""
    n = len(node_ids)
    max_f = max(filtration_values)

    # Create distance matrix based on edge connections
    dist = np.full((n, n), max_f + 2)
    np.fill_diagonal(dist, 0)
    for u, v in edge_list:
        d = max(filtration_values[u], filtration_values[v])
        dist[u, v] = d
        dist[v, u] = d

    from ripser import ripser
    result = ripser(dist, maxdim=0, thresh=max_f + 1)
    dgms = result['dgms']
    intervals = dgms[0]

    result_list = []
    for interval in intervals:
        birth, death = interval
        if np.isinf(death) or np.isnan(death):
            death = max_f + 1
        result_list.append((float(birth), float(death)))

    return result_list


def _compute_persistence_fallback(node_ids, edge_list, filtration_values):
    """Simple connected components tracker as fallback."""
    n = len(node_ids)
    parent = list(range(n))
    rank = [0] * n
    components_at_level = {}

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx == ry:
            return
        if rank[rx] < rank[ry]:
            parent[rx] = ry
        elif rank[rx] > rank[ry]:
            parent[ry] = rx
        else:
            parent[ry] = rx
            rank[rx] += 1

    # Sort edges by filtration
    edges_with_filtration = [(max(filtration_values[u], filtration_values[v]), u, v)
                             for u, v in edge_list]
    edges_with_filtration.sort()

    # Track births at each vertex addition
    births = {i: filtration_values[i] for i in range(n)}

    # Process edges
    for fval, u, v in edges_with_filtration:
        union(u, v)

    # Find roots and their min birth
    root_birth = {}
    for i in range(n):
        root = find(i)
        if root not in root_birth:
            root_birth[root] = filtration_values[i]
        else:
            root_birth[root] = min(root_birth[root], filtration_values[i])

    # Get one interval per component (simplified)
    intervals = []
    for root, birth in root_birth.items():
        intervals.append((birth, max(filtration_values) + 1))

    return intervals


def plot_diagram(diagram: List[Tuple[float, float]],
                 output_path: str,
                 title: str = "Persistence Diagram"):
    """Generate publication-quality persistence diagram plot."""
    if not diagram:
        return

    births = [d[0] for d in diagram]
    deaths = [d[1] for d in diagram]

    plt.figure(figsize=(6, 6))
    plt.scatter(births, deaths, alpha=0.7, s=50, edgecolors='k', linewidth=0.5)

    # Diagonal line
    all_vals = births + deaths
    min_val, max_val = min(all_vals), max(all_vals)
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', alpha=0.5, label='diagonal')

    plt.xlabel('Birth (crossing number)', fontsize=12)
    plt.ylabel('Death (crossing number)', fontsize=12)
    plt.title(title, fontsize=14)
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Ensure equal aspect
    plt.axis('equal')
    plt.tight_layout()

    # Save in both formats
    base = os.path.splitext(output_path)[0]
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
