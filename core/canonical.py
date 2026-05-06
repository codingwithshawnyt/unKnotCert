"""
Canonicalization for Gauss words - remap crossing IDs to detect duplicates.
"""

from typing import List, Tuple

Token = Tuple[int, int]


def canonical(word: List[Token]) -> tuple:
    """
    Remap crossing IDs to 1, 2, 3, ... in order of first appearance.
    Return a tuple of (remapped_id, sign) pairs.

    This makes two diagrams that differ only by ID permutation map to the same canonical form.
    """
    if not word:
        return tuple()

    id_map = {}
    next_id = 1
    result = []

    for crossing_id, sign in word:
        if crossing_id not in id_map:
            id_map[crossing_id] = next_id
            next_id += 1
        result.append((id_map[crossing_id], sign))

    return tuple(result)


def canonical_str(word: List[Token]) -> str:
    """Return string representation of canonical form for hashing."""
    return str(canonical(word))
