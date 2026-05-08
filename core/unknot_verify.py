"""BRS-based classical unknot verification (Phase 3.0.5).

If a Gauss word reduces to the empty word under the full Reidemeister
move set (including up-moves), it is definitively a classical unknot.

Budget table (approved by user):
  n ≤ 4   : ceiling = cr + 2, timeout 10 s
  5 ≤ n ≤ 6 : ceiling = cr + 3, timeout 30 s
  7 ≤ n ≤ 9 : ceiling = cr + 3, timeout 60 s
  10 ≤ n ≤ 12: ceiling = cr + 3, timeout 120 s
"""

import time
from typing import List, Tuple, Dict

from exact_barrier import bounded_bfs
from core.gauss import crossing_number

Token = Tuple[int, int]


BUDGET_TABLE = {
    (2, 4):  {'ceiling_offset': 2, 'timeout': 10},
    (5, 6):  {'ceiling_offset': 3, 'timeout': 30},
    (7, 9):  {'ceiling_offset': 3, 'timeout': 60},
    (10, 12): {'ceiling_offset': 3, 'timeout': 120},
}


_BUDGET_RANGES = list(BUDGET_TABLE.items())


def _lookup_budget(n: int) -> Dict:
    """Return the BRS budget for a word with crossing number *n*."""
    for (lo, hi), cfg in _BUDGET_RANGES:
        if lo <= n <= hi:
            return cfg
    # Default fallback (should not happen for n in 1..12)
    return {'ceiling_offset': 3, 'timeout': 120}


def verify_unknot(word: List[Token],
                  custom_ceiling: int = None,
                  custom_timeout: float = None,
                  verbose: bool = False) -> Dict:
    """Return whether *word* is a classical unknot via BRS.

    Parameters
    ----------
    word : list of (int, int)
        Signed Gauss word.
    custom_ceiling, custom_timeout : optional overrides
    verbose : bool

    Returns
    -------
    dict with keys:
        is_unknot, reachable_via_brs, exhaustive, ceiling, timeout,
        states_visited, path_length, wall_time.
    """
    n = crossing_number(word)
    cfg = _lookup_budget(n)
    ceiling = custom_ceiling if custom_ceiling is not None else n + cfg['ceiling_offset']
    timeout = custom_timeout if custom_timeout is not None else cfg['timeout']

    if word == []:
        return {
            'is_unknot': True,
            'reachable_via_brs': True,
            'exhaustive': True,
            'ceiling': 0,
            'timeout': 0.0,
            'states_visited': 1,
            'path_length': 0,
            'wall_time': 0.0,
        }

    result = bounded_bfs(
        word, ceiling=ceiling, strategy='bfs',
        time_limit=timeout, verbose=verbose,
        bigon_r2=True,
    )

    return {
        'is_unknot': result['reachable'],
        'reachable_via_brs': result['reachable'],
        'exhaustive': result.get('exhaustive', False),
        'ceiling': ceiling,
        'timeout': timeout,
        'states_visited': result['states_visited'],
        'path_length': result.get('path_length'),
        'wall_time': result['wall_time'],
    }


# ---------------------------------------------------------------------------
# Hand-verified unknot test cases
# ---------------------------------------------------------------------------

UNKNOT_TEST_CASES = [
    # (word, expected_is_unknot, description)
    ([], True, "empty word (trivially unknot)"),
    ([(1, +1), (1, -1)], True, "single loop (R1-down reduces)"),
    ([(1, +1), (2, +1), (2, -1), (1, -1)], True,
     "nested pair (R2-down reduces)"),
    ([(1, +1), (2, +1), (1, -1), (2, -1)], True,
     "interleaved pair (R2-down reduces)"),
    # Trefoil (non-unknot)
    ([(1, +1), (2, +1), (3, +1), (1, -1), (2, -1), (3, -1)],
     False, "right-handed trefoil (NOT unknot)"),
    ([(1, -1), (2, -1), (3, -1), (1, +1), (2, +1), (3, +1)],
     False, "left-handed trefoil (NOT unknot)"),
]
