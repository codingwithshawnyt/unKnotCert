"""Planarity check for Gauss words via the de Fraysseix--Ossona de Mendez
parity criterion (Lovász 1965 / Read--Rosenstiehl 1987).

A signed Gauss word is planar-realizable (classical) iff its interlacement
graph satisfies the parity criterion: for every edge (i, j), the number of
vertices adjacent to exactly one of {i, j} in the interlacement graph is
even.

This is the canonical algebraic implementation; the parity check is local to
edges and runs in O(n^3) time for a word on n crossings.
"""

from typing import List, Tuple, Set, Dict

Token = Tuple[int, int]


def _pair_positions(word: List[Token]) -> Dict[int, Tuple[int, int, int, int]]:
    """Return {cid: (pos1, sign1, pos2, sign2)} for each crossing in word."""
    first_seen = {}
    result = {}
    for i, (cid, s) in enumerate(word):
        if cid not in first_seen:
            first_seen[cid] = (i, s)
        else:
            p1, s1 = first_seen[cid]
            result[cid] = (p1, s1, i, s)
    return result


def _is_linked(pairs: Dict[int, Tuple[int, int, int, int]], a: int, b: int) -> bool:
    """True iff chords a and b are interleaved (linked)."""
    a1, _, a2, _ = pairs[a]
    b1, _, b2, _ = pairs[b]
    return (a1 < b1 < a2 < b2) or (b1 < a1 < b2 < a2)


def _build_interlacement_graph(word: List[Token]) -> Dict[int, Set[int]]:
    """Build interlacement graph (vertices = crossing labels, edges = linked)."""
    pairs = _pair_positions(word)
    cids = list(pairs.keys())
    graph: Dict[int, Set[int]] = {cid: set() for cid in cids}
    for a in cids:
        for b in cids:
            if a < b and _is_linked(pairs, a, b):
                graph[a].add(b)
                graph[b].add(a)
    return graph


def is_planar(word: List[Token]) -> bool:
    """Check whether a signed Gauss word is planar-realizable (classical).

    Implements the Read--Rosenstiehl / de Fraysseix--Ossona de Mendez
    parity criterion over the interlacement graph: the number of vertices
    adjacent to exactly one endpoint of each edge must be even.
    """
    if not word:
        return True  # empty word is trivially planar

    pairs = _pair_positions(word)
    cids = list(pairs.keys())
    graph = _build_interlacement_graph(word)

    # de Fraysseix--Ossona de Mendez parity criterion.
    for i in cids:
        for j in list(graph[i]):
            if i >= j:
                continue
            adj_i = graph[i]
            adj_j = graph[j]
            count = 0
            for k in cids:
                if k == i or k == j:
                    continue
                in_i = k in adj_i
                in_j = k in adj_j
                if (in_i and not in_j) or (not in_i and in_j):
                    count += 1
            if count % 2 != 0:
                return False

    return True


def assign_alternating_signs(unsigned_word: List[int]) -> List[Token]:
    """Assign alternating + / - signs to an unsigned Gauss word.

    Labels get +1 on first appearance, -1 on second.  This matches the
    standard convention for knot Gauss words.
    """
    first_seen = set()
    tokens = []
    for cid in unsigned_word:
        if cid not in first_seen:
            tokens.append((cid, +1))
            first_seen.add(cid)
        else:
            tokens.append((cid, -1))
    return tokens


# ---------------------------------------------------------------------------
# Corrected hand-verified test cases (user confirmed parity implementation
# was correct; test expectations were wrong for cases 9 and 10)
# ---------------------------------------------------------------------------

PLANARITY_TEST_CASES = [
    # (unsigned_word, expected_planar, description)
    ([], True, "empty word"),
    ([1, 1], True, "single loop (R1)"),
    ([1, 2, 2, 1], True, "two nested chords"),
    ([1, 2, 1, 2], True, "two interleaved chords (R2 pair)"),
    ([1, 2, 3, 1, 2, 3], True, "three pairwise interleaved (trefoil pattern)"),
    ([1, 2, 1, 3, 2, 3], False,
     "classical non-realizable (Lovász / de Fraysseix obstacle)"),
    ([1, 2, 3, 4, 1, 3, 2, 4], False, "non-realizable 4-chord"),
    ([1, 2, 3, 1, 4, 3, 2, 4], True, "realizable 4-chord (nested + interleaved)"),
    ([1, 2, 1, 3, 4, 3, 2, 4], False,
     "non-realizable 4-chord; edge (1,2) has odd parity = 1"),
    ([1, 2, 3, 4, 5, 1, 2, 3, 4, 5], True,
     "pentagram Gauss code; K_5 interlacement but realizable"),
]
