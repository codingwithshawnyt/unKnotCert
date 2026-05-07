"""Verify the structural characterization:
   At every intermediate state of a successful R1+R2-down path,
   each interleaving-connected component contains a directly-nested pair
   (i.e., an R2-down move is always available within each component).
   
   Conversely, at the stuck states of Goeritz/Culprit,
   some component has NO directly-nested pair (complete interleaving).
"""

import sys
sys.path.insert(0, '.')
from core.gauss import _pair_positions, crossing_number, get_valid_actions, apply_action
from experiments.run import DIAGRAMS
from collections import defaultdict


def has_nested_pair(word):
    """Check if the word has any pair where one crossing directly nests another
    (i.e., an R2-down move is applicable)."""
    actions = get_valid_actions(word, 999)
    r2 = [a for a in actions if a[0] == 'R2_down']
    return len(r2) > 0, len(r2)


def interleaving_components(word):
    """Return interleaving-connected components."""
    pairs = _pair_positions(word)
    cids = sorted(pairs.keys())
    if not cids:
        return []
    
    parent = {c: c for c in cids}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[rx] = ry
    
    for i in range(len(cids)):
        a = cids[i]
        a1, _, a2, _ = pairs[a]
        for j in range(i + 1, len(cids)):
            b = cids[j]
            b1, _, b2, _ = pairs[b]
            if (a1 < b1 < a2 < b2) or (b1 < a1 < b2 < a2):
                union(a, b)
    
    comp = defaultdict(list)
    for c in cids:
        comp[find(c)].append(c)
    
    return list(comp.values())


def component_nested_pair_count(word, comp_cids):
    """Count R2-down moves involving only crossings within this component."""
    comp_set = set(comp_cids)
    actions = get_valid_actions(word, 999)
    r2 = [a for a in actions if a[0] == 'R2_down' and a[1] in comp_set and a[2] in comp_set]
    return len(r2)


def replay_d28_path():
    """Replay D28 monotone path and verify characterization at each step."""
    word = list(DIAGRAMS['D28'])
    next_id = 29
    
    moves = [
        ('R2_down', 1, 2),
        ('R2_down', 6, 5),
        ('R2_down', 3, 7),
        ('R2_down', 8, 9),
        ('R2_down', 10, 12),
        ('R2_down', 11, 13),
        ('R2_down', 15, 17),
        ('R2_down', 16, 21),
        ('R2_down', 18, 19),
        ('R2_down', 23, 24),
        ('R2_down', 22, 26),
        ('R2_down', 25, 27),
    ]
    
    print("=== D28 monotone path verification ===")
    for step, move in enumerate(moves):
        cn = crossing_number(word)
        has_r2, r2_count = has_nested_pair(word)
        comps = interleaving_components(word)
        comp_r2 = [component_nested_pair_count(word, c) for c in comps]
        
        print(f"Step {step:2d}: cn={cn:2d}, comps={len(comps)}, "
              f"sizes={[len(c) for c in comps]}, "
              f"comp_r2={comp_r2}, total_r2={r2_count}")
        
        actions = get_valid_actions(word, next_id)
        matching = [a for a in actions if a[0] == move[0] and a[1] == move[1] and a[2] == move[2]]
        assert matching, f"Move {move} not found at step {step}"
        word, next_id = apply_action(word, matching[0], next_id)
    
    # Final 4 R1-down moves
    cn = crossing_number(word)
    has_r2, r2_count = has_nested_pair(word)
    comps = interleaving_components(word)
    print(f"Step 12: cn={cn}, comps={len(comps)}, sizes={[len(c) for c in comps]}, "
          f"total_r2={r2_count}, R1 moves available={len([a for a in get_valid_actions(word, next_id) if a[0] == 'R1_down'])}")


def check_goeritz_culprit_stuck():
    """Verify that Goeritz/Culprit stuck states have no nested pairs in any component."""
    
    # Simulate greedy R2-down until stuck
    for name in ['Goeritz', 'Culprit']:
        word = list(DIAGRAMS[name])
        next_id = max(c for c, _ in word) + 1
        
        print(f"\n=== {name} greedy R2-down path ===")
        step = 0
        while word:
            cn = crossing_number(word)
            has_r2, r2_count = has_nested_pair(word)
            comps = interleaving_components(word)
            comp_r2 = [component_nested_pair_count(word, c) for c in comps]
            
            print(f"Step {step:2d}: cn={cn:2d}, comps={len(comps)}, "
                  f"sizes={[len(c) for c in comps]}, "
                  f"comp_r2={comp_r2}, total_r2={r2_count}")
            
            if not has_r2:
                r1_actions = [a for a in get_valid_actions(word, next_id) if a[0] == 'R1_down']
                if not r1_actions:
                    print(f"  STUCK: no R1 or R2 available!")
                    break
                else:
                    print(f"  No R2 but {len(r1_actions)} R1 available")
                    chosen = r1_actions[0]
            else:
                actions = get_valid_actions(word, next_id)
                r2_actions = [a for a in actions if a[0] == 'R2_down']
                chosen = r2_actions[0]
            
            word, next_id = apply_action(word, chosen, next_id)
            step += 1


def check_ochiaii_path():
    """Replay OchiaiII monotone path and verify."""
    import json
    from pathlib import Path
    
    path_file = Path(__file__).parent.parent / 'bridge' / 'ochiaiii_paths.json'
    with open(path_file) as f:
        data = json.load(f)
    
    moves = data['paths']['monotone_down']['moves']
    
    word = list(DIAGRAMS['OchiaiII'])
    next_id = 46
    
    print(f"\n=== OchiaiII monotone path verification ===")
    for step, move in enumerate(moves):
        cn = crossing_number(word)
        has_r2, r2_count = has_nested_pair(word)
        comps = interleaving_components(word)
        comp_r2 = [component_nested_pair_count(word, c) for c in comps]
        
        if step <= 3 or step >= len(moves) - 3 or not has_r2:
            print(f"Step {step:2d}: cn={cn:2d}, comps={len(comps)}, "
                  f"sizes={[len(c) for c in comps][:5]}..., "
                  f"comp_r2={comp_r2[:5]}..., total_r2={r2_count}")
        
        move_name = move[0]
        if move_name == 'R2_down':
            a, b = move[1], move[2]
            actions = get_valid_actions(word, next_id)
            matching = [m for m in actions if m[0] == 'R2_down' and m[1] == a and m[2] == b]
            if not matching:
                print(f"  WARNING: R2({a},{b}) not found at step {step}")
                break
            word, next_id = apply_action(word, matching[0], next_id)
        elif move_name == 'R1_down':
            actions = get_valid_actions(word, next_id)
            r1_actions = [m for m in actions if m[0] == 'R1_down']
            if r1_actions:
                word, next_id = apply_action(word, r1_actions[0], next_id)
            else:
                print(f"  WARNING: no R1 available at step {step}")
                break


if __name__ == '__main__':
    replay_d28_path()
    check_goeritz_culprit_stuck()
    check_ochiaii_path()
