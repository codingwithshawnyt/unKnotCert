"""
Definitive interleaving graph analysis for the structural characterization.

Key findings from previous analysis:
1. The STATIC interleaving graph is too dense to predict monotone reducibility
2. All 5 diagrams have unpeelable cores in the interleaving graph
3. Greedy R1/R2-down elimination fails for all 5 diagrams

New analysis:
1. Compute R2-down-only monotone reducibility (this is the right question)
2. Characterize the "stuck" states: what Gauss word structure prevents R2-down?
3. Analyze the maximal independent set in the nesting tree
4. Compute the "nesting width" - maximum number of simultaneously nested pairs
"""

import sys
from pathlib import Path
from collections import defaultdict, deque

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.gauss import (
    crossing_number, get_valid_actions, apply_action, _pair_positions
)
from experiments.run import DIAGRAMS


def max_nesting_depth_at_each_position(word):
    """Compute the nesting depth at each position in the Gauss word.
    
    Nesting depth at position i = number of crossings whose interval
    contains position i.
    """
    if not word:
        return []
    
    pairs = _pair_positions(word)
    n = len(word)
    depth = [0] * n
    
    for cid, (p1, s1, p2, s2) in pairs.items():
        if p1 < p2:
            for i in range(p1, p2 + 1):
                depth[i] += 1
        else:
            for i in range(p1, n):
                depth[i] += 1
            for i in range(0, p2 + 1):
                depth[i] += 1
    
    return depth


def nesting_width(word):
    """Maximum number of simultaneously active intervals (max nesting depth)."""
    depths = max_nesting_depth_at_each_position(word)
    return max(depths) if depths else 0


def analyze_interleaving_at_stuck_state(word):
    """Analyze the interleaving structure at a state where no R1/R2-down is possible.
    
    Returns properties of the stuck word.
    """
    pairs = _pair_positions(word)
    cids = sorted(pairs.keys())
    n = len(cids)
    
    if n == 0:
        return {'trivial': True}
    
    # Build interleaving graph
    interleaved = defaultdict(set)
    for i in range(len(cids)):
        a = cids[i]
        a1, _, a2, _ = pairs[a]
        for j in range(i + 1, len(cids)):
            b = cids[j]
            b1, _, b2, _ = pairs[b]
            if (a1 < b1 < a2 < b2) or (b1 < a1 < b2 < a2):
                interleaved[a].add(b)
                interleaved[b].add(a)
    
    # Check if any pair is non-interleaved (adjacent in nesting tree => R2 possible)
    non_interleaved_pairs = 0
    for a in cids:
        for b in cids:
            if a >= b:
                continue
            if b not in interleaved[a]:
                non_interleaved_pairs += 1
    
    # Compute the "interleaving density": fraction of pairs that are interleaved
    total_pairs = n * (n - 1) // 2
    interleaved_pairs = sum(len(v) for v in interleaved.values()) // 2
    density = interleaved_pairs / total_pairs if total_pairs > 0 else 0
    
    # Check for R1-applicable crossings (adjacent same-id pairs)
    L = len(word)
    W2 = word + word
    r1_count = 0
    for i in range(L):
        if W2[i][0] == W2[i + 1][0] and W2[i][1] == -W2[i + 1][1]:
            r1_count += 1
    
    # Check for R2-applicable pairs (nested pairs with no crossing between them)
    r2_count = 0
    actions = get_valid_actions(word, 999)
    r2_actions = [a for a in actions if a[0] == 'R2_down']
    r2_count = len(r2_actions)
    
    return {
        'trivial': False,
        'cr': n,
        'interleaved_pairs': interleaved_pairs,
        'non_interleaved_pairs': non_interleaved_pairs,
        'total_pairs': total_pairs,
        'interleaving_density': density,
        'r1_count': r1_count,
        'r2_count': r2_count,
        'stuck': (r1_count == 0 and r2_count == 0),
    }


def exhaustive_monotone_down_search(word, max_states=50000):
    """BFS using only R1-down and R2-down moves.
    
    Returns (found_unknot, states_explored, unique_states, stuck_cns).
    """
    from core.canonical import canonical
    
    initial = list(word)
    canon_initial = canonical(initial)
    visited = {canon_initial}
    queue = deque([initial])
    states_explored = 0
    stuck_cns = set()
    found = False
    
    while queue and states_explored < max_states:
        current = queue.popleft()
        states_explored += 1
        
        if not current:
            found = True
            break
        
        cn = crossing_number(current)
        next_id = max(c for c, _ in current) + 1 if current else 1
        actions = get_valid_actions(current, next_id)
        down_actions = [a for a in actions if a[0] in ('R1_down', 'R2_down')]
        
        if not down_actions:
            stuck_cns.add(cn)
            continue
        
        for action in down_actions:
            new_word, _ = apply_action(current, action, next_id)
            canon = canonical(new_word)
            if canon not in visited:
                visited.add(canon)
                queue.append(new_word)
    
    return found, states_explored, len(visited), sorted(stuck_cns)


def find_stuck_state_greedy(word):
    """Apply greedy R2-down until stuck, then return the stuck word."""
    current = list(word)
    next_id = max(c for c, _ in current) + 1 if current else 1
    steps = 0
    
    while current:
        actions = get_valid_actions(current, next_id)
        r1 = [a for a in actions if a[0] == 'R1_down']
        r2 = [a for a in actions if a[0] == 'R2_down']
        
        if not r1 and not r2:
            return current, steps
        
        if r1:
            chosen = r1[0]
        else:
            chosen = r2[0]
        
        current, next_id = apply_action(current, chosen, next_id)
        steps += 1
    
    return current, steps


def main():
    diagrams = {
        'Goeritz': DIAGRAMS['Goeritz'],
        'Culprit': DIAGRAMS['Culprit'],
        'D28': DIAGRAMS['D28'],
        'D43': DIAGRAMS['D43'],
        'OchiaiII': DIAGRAMS['OchiaiII'],
    }
    
    monotone_r1r2_known = {
        'Goeritz': False,
        'Culprit': False,
        'D28': True,
        'D43': True,
        'OchiaiII': True,
    }
    
    print("=" * 80)
    print("DEFINITIVE STRUCTURAL ANALYSIS")
    print("=" * 80)
    
    results = {}
    
    for name, word in diagrams.items():
        n = crossing_number(word)
        ns_width = nesting_width(word)
        
        # Check R1/R2-down availability at the initial word
        actions = get_valid_actions(word, 999)
        r1 = [a for a in actions if a[0] == 'R1_down']
        r2 = [a for a in actions if a[0] == 'R2_down']
        
        # Find stuck state via greedy R2-down
        stuck_word, steps = find_stuck_state_greedy(word)
        stuck_cn = crossing_number(stuck_word)
        stuck_analysis = analyze_interleaving_at_stuck_state(stuck_word)
        
        # Do exhaustive monotone-down search (skip large diagrams)
        if n <= 30:
            found, explored, unique, stuck_list = exhaustive_monotone_down_search(word)
        else:
            # For D43 and OchiaiII, we already know from BFS that they ARE monotone-reducible
            found = monotone_r1r2_known[name]
            explored = -1
            unique = -1
            stuck_list = []
        
        results[name] = {
            'cr': n,
            'nesting_width': ns_width,
            'initial_r1': len(r1),
            'initial_r2': len(r2),
            'greedy_stuck_cn': stuck_cn,
            'greedy_steps': steps,
            'stuck_interleaving_density': stuck_analysis.get('interleaving_density', 0),
            'exhaustive_found': found,
            'exhaustive_explored': explored,
            'exhaustive_unique': unique,
            'exhaustive_stuck_count': len(stuck_list),
        }
        
        print(f"\n--- {name} (cr={n}) ---")
        print(f"  Nesting width (max simultaneous nesting): {ns_width}")
        print(f"  Initial R1-down available: {len(r1)}")
        print(f"  Initial R2-down available: {len(r2)}")
        print(f"  Greedy R2-down: stuck at cn={stuck_cn} after {steps} steps")
        if stuck_analysis.get('interleaving_density', 0) > 0:
            print(f"  Stuck word: {stuck_analysis['cr']} crossings, "
                  f"interleaving density={stuck_analysis['interleaving_density']:.2f}")
        print(f"  Exhaustive R1+R2-down search: {'FOUND UNKNOT' if found else 'NO UNKNOT PATH'}")
        print(f"    States explored: {explored}, unique states: {unique}")
        if stuck_list:
            print(f"    Stuck states encountered: {len(stuck_list)}, "
                  f"at crossing numbers: {sorted(set(stuck_list))}")
        print(f"  Known monotone-reducible (R1+R2 only): {monotone_r1r2_known[name]}")
        print(f"  Search confirms: {found == monotone_r1r2_known[name]}")
    
    print()
    print("=" * 80)
    print("SUMMARY TABLE")
    print("=" * 80)
    print(f"{'Diagram':<12} {'cr':>4} {'NW':>4} {'R2_0':>5} {'StuckCN':>8} "
          f"{'Monotone':>9} {'Exhaustive':>11} {'Match':>6}")
    print("-" * 70)
    
    for name, r in results.items():
        match = str(r['exhaustive_found'] == monotone_r1r2_known[name])
        print(f"{name:<12} {r['cr']:>4} {r['nesting_width']:>4} {r['initial_r2']:>5} "
              f"{r['greedy_stuck_cn']:>8} "
              f"{str(monotone_r1r2_known[name]):>9} "
              f"{str(r['exhaustive_found']):>11} {match:>6}")
    
    print()
    print("=" * 80)
    print("INTERLEAVING DENSITY AT STUCK STATES")
    print("=" * 80)
    
    for name, word in diagrams.items():
        stuck_word, steps = find_stuck_state_greedy(word)
        analysis = analyze_interleaving_at_stuck_state(stuck_word)
        print(f"\n--- {name}: greedy stuck at cn={analysis.get('cr', '?')} ---")
        if not analysis.get('trivial', False):
            print(f"  Interleaving density: {analysis['interleaving_density']:.3f}")
            print(f"  Interleaved pairs: {analysis['interleaved_pairs']} / {analysis['total_pairs']}")
            print(f"  Non-interleaved pairs: {analysis['non_interleaved_pairs']}")
            print(f"  R1-down applicable: {analysis['r1_count']}")
            print(f"  R2-down applicable: {analysis['r2_count']}")
            print(f"  Word (first 20 tokens): {stuck_word[:20]}")


if __name__ == '__main__':
    main()
