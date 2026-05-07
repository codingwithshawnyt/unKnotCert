"""Persistence invariance and bottleneck distance analysis for Phase 3.

Goal: Determine whether the 0-dimensional persistence diagram of the
Reidemeister graph (filtered by crossing number) is a knot invariant,
and whether bottleneck distance can separate knot types or quantify
unknotting hardness.

Key questions:
1. Invariance: Do different diagrams of the same knot produce the same
   (or bottleneck-equivalent) persistence diagrams?
2. Separation: Do diagrams of different knots produce distinguishable
   persistence diagrams?
3. Complexity: Does bottleneck distance to the unknot correlate with
   the minimax unknotting barrier M(D)?
"""

import numpy as np
from typing import List, Tuple, Dict
from itertools import combinations
from scipy.optimize import linear_sum_assignment


def bottleneck_distance(pd1: List[Tuple[float, float]],
                        pd2: List[Tuple[float, float]],
                        infinity_value: float = None) -> float:
    """Compute the bottleneck distance between two persistence diagrams.

    Uses the Hungarian algorithm (linear assignment) to find the optimal
    matching that minimizes the maximum cost. Points not matched to a
    partner are matched to the diagonal (birth = death).

    Args:
        pd1: First persistence diagram as list of (birth, death) pairs.
        pd2: Second persistence diagram as list of (birth, death) pairs.
        infinity_value: Value to use for infinity deaths. If None,
            uses max of all finite deaths in both diagrams + 1.

    Returns:
        The bottleneck distance (float).
    """
    if infinity_value is None:
        all_deaths = [d for _, d in pd1 + pd2 if d != float('inf')]
        infinity_value = max(all_deaths) + 1 if all_deaths else 1.0

    def normalize(pd):
        return [(b, d if d != float('inf') else infinity_value) for b, d in pd]

    d1 = normalize(pd1)
    d2 = normalize(pd2)

    n1, n2 = len(d1), len(d2)
    N = n1 + n2

    diag1 = [(b, b) for b, _ in d1]
    diag2 = [(b, b) for b, _ in d2]

    all1 = d1 + diag2
    all2 = d2 + diag1

    cost_matrix = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            p1 = all1[i]
            p2 = all2[j]
            cost_matrix[i, j] = max(abs(p1[0] - p2[0]), abs(p1[1] - p2[1]))

    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    return float(max(cost_matrix[i, j] for i, j in zip(row_ind, col_ind)))


def bottleneck_distance_approx(pd1, pd2, infinity_value=None):
    """Fast approximate bottleneck distance using greedy matching.

    For large diagrams, this is much faster than the exact Hungarian method.
    """
    if infinity_value is None:
        all_deaths = [d for _, d in pd1 + pd2 if d != float('inf')]
        infinity_value = max(all_deaths) + 1 if all_deaths else 1.0

    def normalize(pd):
        return [(b, d if d != float('inf') else infinity_value) for b, d in pd]

    d1 = normalize(pd1)
    d2 = normalize(pd2)

    def l_inf_dist(p, q):
        return max(abs(p[0] - q[0]), abs(p[1] - q[1]))

    def diag_dist(p):
        return (p[1] - p[0]) / 2.0

    costs = []
    for p in d1:
        best = min(l_inf_dist(p, q) for q in d2) if d2 else diag_dist(p)
        best = min(best, diag_dist(p))
        costs.append(best)
    for q in d2:
        best = min(l_inf_dist(q, p) for p in d1) if d1 else diag_dist(q)
        best = min(best, diag_dist(q))
        costs.append(best)

    return float(max(costs)) if costs else 0.0


def wasserstein_distance(pd1, pd2, p=1, infinity_value=None):
    """Compute the p-Wasserstein distance between two persistence diagrams.

    Uses the Hungarian algorithm for optimal matching.
    """
    if infinity_value is None:
        all_deaths = [d for _, d in pd1 + pd2 if d != float('inf')]
        infinity_value = max(all_deaths) + 1 if all_deaths else 1.0

    def normalize(pd):
        return [(b, d if d != float('inf') else infinity_value) for b, d in pd]

    d1 = normalize(pd1)
    d2 = normalize(pd2)

    n1, n2 = len(d1), len(d2)
    N = n1 + n2

    diag1 = [(b, b) for b, _ in d1]
    diag2 = [(b, b) for b, _ in d2]

    all1 = d1 + diag2
    all2 = d2 + diag1

    cost_matrix = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            p1 = all1[i]
            p2 = all2[j]
            cost_matrix[i, j] = (max(abs(p1[0] - p2[0]), abs(p1[1] - p2[1]))) ** p

    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    return float(sum(cost_matrix[i, j] for i, j in zip(row_ind, col_ind)) ** (1.0 / p))
