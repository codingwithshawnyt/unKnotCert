"""Record non-peelable bigon kernels for all hard unknot diagrams."""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from experiments.run import DIAGRAMS
from core.gauss import (
    crossing_number, get_bigon_R2_pairs, get_R1_down_positions,
    get_valid_actions, _pair_positions
)
from algorithms.greedy_peeling import greedy_bigon_peel, greedy_bigon_peel_all_orderings

NAMES = ['Goeritz', 'Culprit', 'D28', 'D43', 'OchiaiII']

def interleaving_graph_stats(word):
    pairs = _pair_positions(word)
    cids = sorted(pairs.keys())
    n = len(cids)
    edges = 0
    for i in range(n):
        a = cids[i]
        a1, _, a2, _ = pairs[a]
        for j in range(i + 1, n):
            b = cids[j]
            b1, _, b2, _ = pairs[b]
            if (a1 < b1 < a2 < b2) or (b1 < a1 < b2 < a2):
                edges += 1
    max_edges = n * (n - 1) // 2
    density = edges / max_edges if max_edges > 0 else 0.0
    is_complete = edges == max_edges and n > 1
    return {'n': n, 'edges': edges, 'max_edges': max_edges, 'density': round(density, 3), 'fully_interleaved': is_complete}


results = {}

for name in NAMES:
    word = DIAGRAMS[name]
    cn = crossing_number(word)

    # Run greedy peeling
    success, moves, stats = greedy_bigon_peel(word, verbose=False)
    ok_all, moves_all, stats_all = greedy_bigon_peel_all_orderings(word)

    # Get stuck state from greedy
    stuck_word = stats.get('stuck_word', word if not success else [])

    # Compute permissive R2 count at initial word for comparison
    permissive_r2 = len([m for m in get_valid_actions(word, 100) if m[0] == 'R2_down'])
    bigon_r2 = len(get_bigon_R2_pairs(word))

    # Stuck state analysis
    stuck_cn = crossing_number(stuck_word)
    stuck_r1 = get_R1_down_positions(stuck_word)
    stuck_r2 = get_bigon_R2_pairs(stuck_word)
    stuck_igraph = interleaving_graph_stats(stuck_word)

    # Also compute interleaving graph at initial state
    initial_igraph = interleaving_graph_stats(word)

    results[name] = {
        'initial_cn': cn,
        'initial_permissive_r2': permissive_r2,
        'initial_bigon_r2': bigon_r2,
        'initial_igraph': initial_igraph,
        'greedy_success': success,
        'greedy_steps': stats['steps'],
        'greedy_r1_count': stats['r1_down_count'],
        'greedy_r2_count': stats['r2_down_count'],
        'greedy_cn_trace': stats['cn_trace'],
        'all_orderings_success': ok_all,
        'all_orderings_states_explored': stats_all['states_explored'],
        'stuck_cn': stuck_cn,
        'stuck_bigon_r2': len(stuck_r2),
        'stuck_r1': len(stuck_r1),
        'stuck_igraph': stuck_igraph,
        'stuck_word': str(stuck_word),
    }

    print(f"\n{'='*60}")
    print(f"{name} (cr={cn})")
    print(f"  Initial: permissive_R2={permissive_r2}, bigon_R2={bigon_r2}")
    print(f"  Initial igraph: n={initial_igraph['n']}, edges={initial_igraph['edges']}, density={initial_igraph['density']}")
    print(f"  Greedy: success={success}, steps={stats['steps']}, R1={stats['r1_down_count']}, R2={stats['r2_down_count']}")
    print(f"  CN trace: {stats['cn_trace']}")
    print(f"  All-orderings: success={ok_all}, states={stats_all['states_explored']}")
    print(f"  Stuck at cr={stuck_cn}: R1={len(stuck_r1)}, bigon_R2={len(stuck_r2)}")
    print(f"  Stuck igraph: n={stuck_igraph['n']}, edges={stuck_igraph['edges']}, density={stuck_igraph['density']}, fully_interleaved={stuck_igraph['fully_interleaved']}")

out_path = Path(__file__).parent.parent / 'outputs' / 'bigon_kernel_details.json'
out_path.parent.mkdir(exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nSaved to {out_path}")
