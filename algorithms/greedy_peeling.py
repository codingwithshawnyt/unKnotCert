"""Greedy bigon peeling algorithm for virtual unknotting.

Attempts to reduce a Gauss word to the empty word using only
bigon R1-down and bigon R2-down moves. A bigon R2-down move
requires that the two outer arcs of the nested pair are empty
of all other chord endpoints (the genuine bigon condition on
chord diagrams).

The greedy algorithm simply applies any available move at each
step. The Greedy Completeness Theorem guarantees that if any
sequence of bigon R1/R2 moves reduces the word to empty, then
every maximal greedy sequence does.
"""

import time
from typing import List, Tuple, Optional, Dict

from core.gauss import (
    Token, MoveDescriptor, crossing_number,
    get_bigon_R2_pairs, get_R1_down_positions, apply_action
)


def greedy_bigon_peel(word: List[Token], verbose: bool = False
) -> Tuple[bool, Optional[List[Tuple[str, int, int]]], Dict]:
    """Attempt to reduce word to empty using only bigon R1-down and bigon R2-down.

    Returns:
        (success, move_sequence, stats) where:
        - success: True if word reduced to empty
        - move_sequence: list of (move_type, param1, param2) or None if failed
        - stats: dict with algorithm statistics
    """
    t0 = time.time()
    current = list(word)
    moves: List[Tuple[str, int, int]] = []
    initial_cn = crossing_number(current)
    cn_trace = [initial_cn]
    steps = 0
    r1_count = 0
    r2_count = 0
    stuck_state = None
    next_id = (max(c for c, _ in current) + 1) if current else 1

    while current:
        r1_positions = get_R1_down_positions(current)
        r2_pairs = get_bigon_R2_pairs(current)

        if r1_positions:
            pos = r1_positions[0]
            move = ('R1_down', pos)
            current, next_id = apply_action(current, move, next_id)
            r1_count += 1
            moves.append(('R1_down', pos, -1))
            if verbose:
                print(f"  R1_down at pos {pos}, cr={crossing_number(current)}")

        elif r2_pairs:
            outer, inner = r2_pairs[0]
            move = ('R2_down', outer, inner)
            current, next_id = apply_action(current, move, next_id)
            r2_count += 1
            moves.append(('R2_down', outer, inner))
            if verbose:
                print(f"  R2_down ({outer},{inner}), cr={crossing_number(current)}")

        else:
            stuck_state = list(current)
            if verbose:
                cn = crossing_number(current)
                print(f"  STUCK at cr={cn}, no bigon R1 or R2 available")
            break

        cn_trace.append(crossing_number(current))
        steps += 1

        if steps > initial_cn * 2:
            if verbose:
                print(f"  SAFETY: exceeded {initial_cn * 2} steps, aborting")
            stuck_state = list(current)
            break

    success = len(current) == 0
    elapsed = time.time() - t0

    stats = {
        'success': success,
        'initial_cn': initial_cn,
        'steps': steps,
        'r1_down_count': r1_count,
        'r2_down_count': r2_count,
        'cn_trace': cn_trace,
        'wall_time': elapsed,
    }

    if not success and stuck_state is not None:
        stats['stuck_cn'] = crossing_number(stuck_state)
        stats['stuck_word'] = stuck_state

    return success, moves if success else None, stats


def greedy_bigon_peel_all_orderings(word: List[Token], max_tries: int = 1000
) -> Tuple[bool, Optional[List[Tuple[str, int, int]]], Dict]:
    """Try all orderings of bigon moves (up to max_tries) to find a successful peel.

    Uses a backtracking approach: at each step, try all available moves
    rather than just the first one. Returns the first successful sequence found.

    This is useful for diagrams where the first greedy choice gets stuck
    but some other ordering succeeds.
    """
    initial_cn = crossing_number(word)
    next_id_start = (max(c for c, _ in word) + 1) if word else 1

    def _search(current, moves, next_id, depth, visited):
        if not current:
            return True, list(moves)

        if depth > initial_cn:
            return False, None

        canon = tuple(sorted([(c, s) for c, s in current]))
        if canon in visited:
            return False, None
        visited.add(canon)

        r1_positions = get_R1_down_positions(current)
        r2_pairs = get_bigon_R2_pairs(current)

        if not r1_positions and not r2_pairs:
            return False, None

        for pos in r1_positions:
            move = ('R1_down', pos)
            new_word, new_next = apply_action(current, move, next_id)
            ok, result = _search(new_word, moves + [('R1_down', pos, -1)],
                                 new_next, depth + 1, visited)
            if ok:
                return True, result

        for outer, inner in r2_pairs:
            move = ('R2_down', outer, inner)
            new_word, new_next = apply_action(current, move, next_id)
            ok, result = _search(new_word, moves + [('R2_down', outer, inner)],
                                 new_next, depth + 1, visited)
            if ok:
                return True, result

        return False, None

    t0 = time.time()
    visited = set()
    ok, result = _search(list(word), [], next_id_start, 0, visited)
    elapsed = time.time() - t0

    stats = {
        'success': ok,
        'initial_cn': initial_cn,
        'states_explored': len(visited),
        'wall_time': elapsed,
    }

    return ok, result, stats


def verify_peel(word: List[Token], moves: List[Tuple[str, int, int]]) -> bool:
    """Verify that applying a move sequence to word produces the empty word."""
    current = list(word)
    next_id = (max(c for c, _ in current) + 1) if current else 1

    for move_tuple in moves:
        mt = move_tuple[0]
        if mt == 'R1_down':
            pos = move_tuple[1]
            move = ('R1_down', pos)
        elif mt == 'R2_down':
            outer, inner = move_tuple[1], move_tuple[2]
            move = ('R2_down', outer, inner)
        else:
            return False
        current, next_id = apply_action(current, move, next_id)

    return len(current) == 0
