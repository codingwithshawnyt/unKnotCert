import sys
sys.path.insert(0, '.')
from core.gauss import _pair_positions, crossing_number
from experiments.run import DIAGRAMS
from collections import defaultdict

for name in ['Goeritz', 'Culprit', 'D28', 'D43', 'OchiaiII']:
    word = DIAGRAMS[name]
    n = crossing_number(word)
    pairs = _pair_positions(word)
    cids = sorted(pairs.keys())
    
    # Union-Find for interleaving connectivity
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
    
    sizes = sorted([len(v) for v in comp.values()], reverse=True)
    
    # Nesting pairs (non-interleaving)
    nested_count = 0
    for i in range(len(cids)):
        a = cids[i]
        a1, _, a2, _ = pairs[a]
        for j in range(i + 1, len(cids)):
            b = cids[j]
            b1, _, b2, _ = pairs[b]
            if a1 < b1 < b2 < a2 or b1 < a1 < a2 < b2:
                nested_count += 1
    
    total = n * (n - 1) // 2
    interleaved_count = total - nested_count
    
    print(f'{name}: cr={n}, components={len(comp)}, sizes={sizes}, '
          f'nested_pairs={nested_count}, interleaved_pairs={interleaved_count}, '
          f'total_pairs={total}')
