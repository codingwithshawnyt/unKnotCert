"""Run greedy bigon peeling on all hard unknot diagrams."""

import sys
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from experiments.run import DIAGRAMS
from core.gauss import crossing_number, get_bigon_R2_pairs, get_R1_down_positions
from algorithms.greedy_peeling import greedy_bigon_peel, greedy_bigon_peel_all_orderings, verify_peel

NAMES = ['Goeritz', 'Culprit', 'D28', 'D43', 'OchiaiII']

print("=" * 70)
print("GREEDY BIGON PEELING EXPERIMENT")
print("=" * 70)

results = {}

for name in NAMES:
    word = DIAGRAMS[name]
    cn = crossing_number(word)
    initial_r1 = get_R1_down_positions(word)
    initial_r2 = get_bigon_R2_pairs(word)

    print(f"\n--- {name} (cr={cn}) ---")
    print(f"  Initial: R1 candidates={len(initial_r1)}, bigon R2 candidates={len(initial_r2)}")

    success, moves, stats = greedy_bigon_peel(word, verbose=False)

    print(f"  Greedy result: success={success}")
    print(f"    steps={stats['steps']}, R1={stats['r1_down_count']}, R2={stats['r2_down_count']}")
    print(f"    CN trace: {stats['cn_trace']}")
    print(f"    Time: {stats['wall_time']:.4f}s")

    if not success:
        stuck_cn = stats.get('stuck_cn', '?')
        stuck_word = stats.get('stuck_word', [])
        print(f"    Stuck at cr={stuck_cn}")
        stuck_r1 = get_R1_down_positions(stuck_word)
        stuck_r2 = get_bigon_R2_pairs(stuck_word)
        print(f"    Stuck state: R1={len(stuck_r1)}, bigon R2={len(stuck_r2)}")

        print(f"\n  Trying ALL orderings (backtracking)...")
        ok2, moves2, stats2 = greedy_bigon_peel_all_orderings(word)
        print(f"    All-orderings result: success={ok2}, states={stats2['states_explored']}, time={stats2['wall_time']:.4f}s")

        if ok2 and moves2:
            print(f"    Move sequence found! length={len(moves2)}")
            v = verify_peel(word, moves2)
            print(f"    Verification: {v}")
    else:
        if moves:
            v = verify_peel(word, moves)
            print(f"    Verification: {v}")

    results[name] = {
        'greedy_success': success,
        'greedy_stats': {k: v for k, v in stats.items() if k != 'stuck_word'},
        'initial_bigon_r2_count': len(initial_r2),
    }

    if not success:
        results[name]['all_orderings_success'] = ok2 if 'ok2' in dir() else None
        results[name]['all_orderings_stats'] = {k: v for k, v in stats2.items() if k != 'stuck_word'} if 'stats2' in dir() else None

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"{'Diagram':<12} {'cr':<5} {'Greedy':<8} {'All-ord':<8} {'Stuck cr':<8}")
print("-" * 45)
for name in NAMES:
    r = results[name]
    gs = r['greedy_success']
    stuck = r['greedy_stats'].get('stuck_cn', '-')
    aos = r.get('all_orderings_success', '-')
    cr = r['greedy_stats']['initial_cn']
    print(f"{name:<12} {cr:<5} {'Yes' if gs else 'No':<8} {str(aos):<8} {str(stuck):<8}")

out_path = Path(__file__).parent.parent / 'outputs' / 'bigon_peeling_results.json'
out_path.parent.mkdir(exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nSaved to {out_path}")
