"""Exact barrier computation via bounded BFS on the Reidemeister move graph.

The Core Theorem:
Let D be a knot diagram and N a positive integer.
Define G_N(D) as the graph of all Gauss words reachable from D
via Reidemeister moves whose crossing number never exceeds N.
If the trivial unknot (empty word) is NOT a vertex of G_N(D), then
any Reidemeister path from D to the unknot must exceed CN at
some point, so the minimax barrier satisfies M(D) >= N+1.

This module implements exhaustive and priority BFS to decide whether the
unknot is in G_N(D), yielding a certified lower bound on M(D).

Combined with the Squeeze Lemma upper bound from Phase 1,
this can give exact values of M(D) for specific diagrams.

Search strategies:
  - 'bfs': Standard FIFO BFS (exhaustive, visits all states).
  - 'cn_priority': Dijkstra-like priority queue keyed on CN.
    Explores low-CN states first, finds unknot faster when reachable.
    Still exhaustive if run to completion.
  - 'cn_priority_no_r3_at_ceiling': CN-priority but skips R3 moves
    at the ceiling CN. NOT exhaustive — can only prove reachability
    (upper bound), not unreachability. Useful for quickly finding
    whether a better path exists.
  - 'down_only': Only explores R1_down and R2_down moves.
    NOT exhaustive — finds unknot iff a monotone-down path exists.
    Very fast, useful as a first check.
"""

import sys
import json
import time
import heapq
from collections import deque
from typing import List, Tuple, Dict, Optional, Set

from core.gauss import (
    Token, MoveDescriptor, get_valid_actions, apply_action, crossing_number
)
from core.canonical import canonical


def bounded_bfs(initial_word: List[Token], ceiling: int,
                verbose: bool = True, log_interval: int = 10000,
                time_limit: Optional[float] = None,
                strategy: str = 'bfs'
) -> Dict:
    """Run bounded BFS on G_N(D) where N = ceiling.

    Args:
        initial_word: Starting Gauss word.
        ceiling: Maximum crossing number allowed.
        verbose: Print progress.
        log_interval: Print status every N states.
        time_limit: Max seconds (None = unlimited). If hit, returns partial.
        strategy: 'bfs', 'cn_priority', 'cn_priority_no_r3_at_ceiling',
                  or 'down_only'.

    Returns dict with:
    'reachable': bool -- whether the unknot is reachable within ceiling
    'exhaustive': bool -- whether the entire G_N(D) was explored
    'states_visited': int -- total states visited
    'edges_explored': int -- total transitions examined
    'max_cn_seen': int -- maximum crossing number encountered
    'wall_time': float -- seconds elapsed
    'cn_distribution': Dict[int, int] -- count of states at each CN
    'path_length': Optional[int] -- BFS depth to unknot if found
    'timed_out': bool -- whether time_limit was hit
    'strategy': str -- search strategy used
    """
    t0 = time.time()
    initial_canon = canonical(initial_word)
    initial_cn = crossing_number(initial_word)

    if initial_cn > ceiling:
        return {
            'reachable': False, 'exhaustive': True,
            'states_visited': 0, 'edges_explored': 0,
            'max_cn_seen': 0, 'wall_time': 0.0,
            'cn_distribution': {}, 'path_length': None,
            'timed_out': False, 'strategy': strategy,
            'note': 'Initial CN exceeds ceiling',
        }

    if initial_cn == 0:
        return {
            'reachable': True, 'exhaustive': True,
            'states_visited': 1, 'edges_explored': 0,
            'max_cn_seen': 0, 'wall_time': 0.0,
            'cn_distribution': {0: 1}, 'path_length': 0,
            'timed_out': False, 'strategy': strategy,
        }

    is_exhaustive = strategy in ('bfs', 'cn_priority')
    skip_r3_at_ceiling = strategy == 'cn_priority_no_r3_at_ceiling'
    down_only = strategy == 'down_only'

    visited: Set[tuple] = {initial_canon}
    edges_explored = 0
    max_cn_seen = initial_cn
    cn_dist: Dict[int, int] = {initial_cn: 1}
    next_id_tracker: Dict[tuple, int] = {initial_canon: _max_id(initial_word) + 1}
    timed_out = False

    if strategy in ('cn_priority', 'cn_priority_no_r3_at_ceiling', 'down_only'):
        counter = 0
        heap: List[Tuple[int, int, int, tuple]] = []
        heapq.heappush(heap, (initial_cn, counter, 0, tuple(initial_word)))
        counter += 1

        while heap:
            if time_limit and time.time() - t0 > time_limit:
                timed_out = True
                break

            cn_prio, _, depth, word_tuple = heapq.heappop(heap)
            word = list(word_tuple)
            word_canon = canonical(word)
            next_id = next_id_tracker.get(word_canon, _max_id(word) + 1)

            actions = get_valid_actions(word, next_id)

            for move in actions:
                mt = move[0]
                if down_only and mt not in ('R1_down', 'R2_down'):
                    continue
                if skip_r3_at_ceiling and mt.startswith('R3') and cn_prio == ceiling:
                    continue

                edges_explored += 1
                new_word, new_next_id = apply_action(word, move, next_id)
                new_cn = crossing_number(new_word)

                if new_cn > ceiling:
                    continue

                new_canon = canonical(new_word)

                if new_canon in visited:
                    continue

                visited.add(new_canon)
                next_id_tracker[new_canon] = new_next_id
                max_cn_seen = max(max_cn_seen, new_cn)
                cn_dist[new_cn] = cn_dist.get(new_cn, 0) + 1

                if new_cn == 0:
                    elapsed = time.time() - t0
                    if verbose:
                        print("UNKNOT FOUND at depth {} after {} states, {:.1f}s".format(
                            depth + 1, len(visited), elapsed))
                    return {
                        'reachable': True, 'exhaustive': True,
                        'states_visited': len(visited),
                        'edges_explored': edges_explored,
                        'max_cn_seen': max_cn_seen,
                        'wall_time': elapsed,
                        'cn_distribution': cn_dist,
                        'path_length': depth + 1,
                        'timed_out': False, 'strategy': strategy,
                    }

                heapq.heappush(heap, (new_cn, counter, depth + 1, tuple(new_word)))
                counter += 1

            if verbose and len(visited) % log_interval == 0:
                elapsed = time.time() - t0
                print("  states={}, edges={}, cn_prio={}, depth={}, heap={}, {:.1f}s".format(
                    len(visited), edges_explored, cn_prio, depth,
                    len(heap), elapsed))

    else:
        queue: deque = deque()
        queue.append((tuple(initial_word), 0))

        while queue:
            if time_limit and time.time() - t0 > time_limit:
                timed_out = True
                break

            word_tuple, depth = queue.popleft()
            word = list(word_tuple)
            word_canon = canonical(word)
            next_id = next_id_tracker.get(word_canon, _max_id(word) + 1)

            actions = get_valid_actions(word, next_id)

            for move in actions:
                edges_explored += 1
                new_word, new_next_id = apply_action(word, move, next_id)
                new_cn = crossing_number(new_word)

                if new_cn > ceiling:
                    continue

                new_canon = canonical(new_word)

                if new_canon in visited:
                    continue

                visited.add(new_canon)
                next_id_tracker[new_canon] = new_next_id
                max_cn_seen = max(max_cn_seen, new_cn)
                cn_dist[new_cn] = cn_dist.get(new_cn, 0) + 1

                if new_cn == 0:
                    elapsed = time.time() - t0
                    if verbose:
                        print("UNKNOT FOUND at depth {} after {} states, {:.1f}s".format(
                            depth + 1, len(visited), elapsed))
                    return {
                        'reachable': True, 'exhaustive': True,
                        'states_visited': len(visited),
                        'edges_explored': edges_explored,
                        'max_cn_seen': max_cn_seen,
                        'wall_time': elapsed,
                        'cn_distribution': cn_dist,
                        'path_length': depth + 1,
                        'timed_out': False, 'strategy': strategy,
                    }

                queue.append((tuple(new_word), depth + 1))

            if verbose and len(visited) % log_interval == 0:
                elapsed = time.time() - t0
                print("  states={}, edges={}, max_cn={}, depth={}, queue={}, {:.1f}s".format(
                    len(visited), edges_explored, max_cn_seen, depth,
                    len(queue), elapsed))

    elapsed = time.time() - t0
    reachable = False
    note = None

    if timed_out:
        note = 'Time limit ({:.0f}s) reached; search incomplete'.format(time_limit)
        if verbose:
            print("TIMEOUT after {:.1f}s: {} states, {} edges explored".format(
                elapsed, len(visited), edges_explored))
    elif not is_exhaustive:
        note = 'Non-exhaustive strategy ({}): unreachability not proven'.format(strategy)
        if verbose:
            print("INCOMPLETE ({}): {} states explored, unknot not found".format(
                strategy, len(visited)))
    else:
        if verbose:
            print("EXHAUSTIVE: unknot NOT reachable at ceiling={}".format(ceiling))
            print("  states={}, edges={}, max_cn={}, {:.1f}s".format(
                len(visited), edges_explored, max_cn_seen, elapsed))
            print("  => M(D) >= {}".format(ceiling + 1))

    result = {
        'reachable': reachable,
        'exhaustive': is_exhaustive and not timed_out,
        'states_visited': len(visited),
        'edges_explored': edges_explored,
        'max_cn_seen': max_cn_seen,
        'wall_time': elapsed,
        'cn_distribution': cn_dist,
        'path_length': None,
        'timed_out': timed_out,
        'strategy': strategy,
    }
    if note:
        result['note'] = note

    return result


def binary_search_barrier(initial_word: List[Token],
                          lo: int, hi: int,
                          verbose: bool = True,
                          strategy: str = 'cn_priority',
                          time_limit: Optional[float] = None
) -> Dict:
    """Find the exact minimax barrier via binary search on the ceiling.

    Searches for the smallest N such that the unknot IS reachable in G_N(D).
    The exact barrier M(D) equals that smallest N.

    Args:
        initial_word: The starting Gauss word.
        lo: Lower bound on M(D) (unknot definitely unreachable below this).
        hi: Upper bound on M(D) (unknot definitely reachable at or below this).
        verbose: Print progress.
        strategy: BFS strategy to use.
        time_limit: Per-run time limit in seconds.

    Returns dict with 'exact_barrier' (int) and per-N results.
    """
    results = {}

    while lo < hi:
        mid = (lo + hi) // 2
        if verbose:
            print("\n=== Binary search: testing N={} (lo={}, hi={}) ===".format(
                mid, lo, hi))

        r = bounded_bfs(initial_word, ceiling=mid, verbose=verbose,
                        strategy=strategy, time_limit=time_limit)
        results[mid] = r

        if r['timed_out']:
            if verbose:
                print("  TIMEOUT at N={} — cannot determine".format(mid))
            break

        if r['reachable']:
            hi = mid
            if verbose:
                print("  Unknot reachable at N={} => M(D) <= {}".format(mid, mid))
        else:
            if not r['exhaustive']:
                if verbose:
                    print("  Non-exhaustive at N={} — cannot prove unreachability".format(mid))
                break
            lo = mid + 1
            if verbose:
                print("  Unknot NOT reachable at N={} => M(D) >= {}".format(
                    mid, mid + 1))

    exact = lo
    proven = (lo == hi) or (not any(r.get('timed_out') or not r.get('exhaustive', True)
                                     for r in results.values()))
    if verbose:
        if proven:
            print("\n*** EXACT BARRIER: M(D) = {} ***".format(exact))
        else:
            print("\n*** PARTIAL: M(D) >= {} (binary search incomplete) ***".format(exact))

    return {
        'exact_barrier': exact,
        'proven': proven,
        'per_ceiling': {str(k): v for k, v in results.items()},
    }


def _max_id(word: List[Token]) -> int:
    if not word:
        return 0
    return max(c for c, _ in word)


if __name__ == '__main__':
    from experiments.run import DIAGRAMS, HARDNESS

    diagram = sys.argv[1] if len(sys.argv) > 1 else 'Goeritz'
    ceiling = int(sys.argv[2]) if len(sys.argv) > 2 else None
    strategy = sys.argv[3] if len(sys.argv) > 3 else 'bfs'
    time_limit_val = float(sys.argv[4]) if len(sys.argv) > 4 else None

    word = DIAGRAMS[diagram]
    initial_cn = crossing_number(word)
    h = HARDNESS.get(diagram, {})
    m_s2 = h.get('m', 0)

    if ceiling is None:
        ceiling = initial_cn - 1

    print("=" * 70)
    print("Bounded BFS: {} (cr={}, m_S2={})".format(diagram, initial_cn, m_s2))
    print("Ceiling N={}: testing if unknot reachable without exceeding CN={}".format(
        ceiling, ceiling))
    print("Strategy: {}".format(strategy))
    if time_limit_val:
        print("Time limit: {:.0f}s".format(time_limit_val))
    print("If unreachable => M(D) >= {}".format(ceiling + 1))
    print("=" * 70)

    result = bounded_bfs(word, ceiling=ceiling, strategy=strategy,
                         time_limit=time_limit_val)
    result['diagram'] = diagram
    result['initial_cn'] = initial_cn
    result['ceiling'] = ceiling
    result['m_s2'] = m_s2

    print("\n" + "=" * 70)
    print("RESULT: {} at ceiling={}".format(diagram, ceiling))
    print(" Reachable: {}".format(result['reachable']))
    print(" Exhaustive: {}".format(result['exhaustive']))
    print(" States visited: {}".format(result['states_visited']))
    print(" Edges explored: {}".format(result['edges_explored']))
    print(" Max CN seen: {}".format(result['max_cn_seen']))
    print(" Time: {:.1f}s".format(result['wall_time']))
    if result['reachable']:
        print(" Path length: {}".format(result['path_length']))
        print(" => M(D) <= {}".format(ceiling))
    elif result['exhaustive']:
        print(" => M(D) >= {}".format(ceiling + 1))
    else:
        print(" => Incomplete search, no rigorous bound")
    print("=" * 70)

    import os
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, 'outputs', 'barrier_results.json')
    os.makedirs(os.path.join(out_dir, 'outputs'), exist_ok=True)

    existing = {}
    if os.path.exists(out_path):
        with open(out_path) as f:
            existing = json.load(f)

    key = "{}_N{}_{}".format(diagram, ceiling, strategy)
    existing[key] = result

    with open(out_path, 'w') as f:
        json.dump(existing, f, indent=2)
    print("Saved to {}".format(out_path))
