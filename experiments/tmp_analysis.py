import sys
sys.path.insert(0, '.')
from core.gauss import _pair_positions, crossing_number, get_valid_actions, apply_action
from experiments.run import DIAGRAMS
from collections import defaultdict

def parallel_components(word):
    """Return the parallel (interleaving-connected) components of a Gauss word."""
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

# D28: verify that the two components are reduced independently
d28 = DIAGRAMS['D28']
comps = parallel_components(d28)
print(f"D28 parallel components:")
for i, comp in enumerate(comps):
    print(f"  Component {i}: crossings {sorted(comp)} ({len(comp)} crossings)")

# Replay the BFS path and check which component each removal comes from
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

comp_sets = [set(c) for c in comps]

print(f"\nBFS path move analysis:")
for move_type, a, b in moves:
    comp_a = None
    comp_b = None
    for i, cs in enumerate(comp_sets):
        if a in cs:
            comp_a = i
        if b in cs:
            comp_b = i
    same = "SAME" if comp_a == comp_b else "DIFFERENT"
    print(f"  R2({a},{b}): comp[{comp_a}] x comp[{comp_b}] = {same}")

# Now check the OchiaiII path too
print(f"\nOchiaiII: single component (all crossings interleaved)")
print(f"Yet it IS monotone-reducible. This means the single-component")
print(f"property does NOT prevent monotone reducibility.")

# Key insight: The property that distinguishes Goeritz/Culprit from D28/D43/OchiaiII
# is NOT the parallel component structure. It must be something else.

# Let me check: what happens at the Goeritz "stuck" state?
# The greedy reduction reduces Goeritz to 5 crossings with 100% interleaving density.
# This is a COMPLETE INTERLEAVING GRAPH - no pair can be de-nested by R2.
# 
# In D28, the greedy gets stuck at 6 crossings with 40% density - but the
# non-interleaved pairs are ALSO not R2-applicable (because they're "separated"
# in the nesting tree - they don't form a proper nested pair).
#
# The real question: in the stuck state, are there any crossing pairs where
# one nests the other? If YES, then an R2-down SHOULD be applicable.
# If NO, then all pairs are purely interleaved and no R2-down is possible.

# Let me check the Goeritz stuck state
from experiments.interleaving_graph import find_stuck_state_greedy

for name in ['Goeritz', 'Culprit']:
    word = DIAGRAMS[name]
    stuck, steps = find_stuck_state_greedy(word)
    pairs = _pair_positions(stuck)
    cids = sorted(pairs.keys())
    
    print(f"\n{name} stuck state (cr={crossing_number(stuck)}, {steps} steps):")
    
    # Check nesting
    for i in range(len(cids)):
        a = cids[i]
        a1, _, a2, _ = pairs[a]
        for j in range(i + 1, len(cids)):
            b = cids[j]
            b1, _, b2, _ = pairs[b]
            nested = (a1 < b1 < b2 < a2) or (b1 < a1 < a2 < b2)
            interleaved = (a1 < b1 < a2 < b2) or (b1 < a1 < b2 < a2)
            if nested:
                # Check if directly nested (no crossing between them in nesting tree)
                directly = True
                for k in range(len(cids)):
                    c = cids[k]
                    if c == a or c == b:
                        continue
                    c1, _, c2, _ = pairs[c]
                    # c is between a and b in nesting?
                    if a1 < c1 and c2 < a2 and b1 < c1 and c2 < b2:
                        directly = False
                        break
                    if b1 < c1 and c2 < b2 and a1 < c1 and c2 < a2:
                        directly = False
                        break
                print(f"  {a}-{b}: NESTED (directly={directly})")
            if interleaved:
                print(f"  {a}-{b}: INTERLEAVED")
