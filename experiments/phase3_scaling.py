"""Phase 3 scaling experiment: No-Up conjecture test on classical unknots.

Pipeline:
1. For n = 2..6: enumerate all classical unknot Gauss words.
2. For n = 7..12: sample classical unknot Gauss words.
3. For each sample, run:
   a) greedy_bigon_peel_all_orderings  (bigon-R1+R2 reducibility)
   b) down_r3_only BRS with budget table (permissive-R2+R3 reducibility)
4. Save per-sample records and per-n aggregates.
5. If any exhaustive sample (n <= 6) is non-reducible, save as candidate
   No-Up counterexample.

Outputs:
- outputs/phase3_scaling_results.json   (all per-sample data)
- outputs/phase3_counterexamples.json   (candidate counterexamples)
"""

import sys
import json
import time
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.gauss import Token, crossing_number
from core.canonical import canonical
from algorithms.greedy_peeling import greedy_bigon_peel_all_orderings
from exact_barrier import bounded_bfs
from experiments.random_unknot import (
    enumerate_classical_unknots,
    sample_classical_unknots,
)

# ---------------------------------------------------------------------------
# Budget table for down_r3_only BRS (aligned with unknot_verify budget)
# ---------------------------------------------------------------------------

BRS_BUDGET = {
    (2, 4):  {'ceiling_offset': 2, 'timeout': 10},
    (5, 6):  {'ceiling_offset': 3, 'timeout': 30},
    (7, 9):  {'ceiling_offset': 3, 'timeout': 60},
    (10, 12): {'ceiling_offset': 3, 'timeout': 120},
}


def _budget_for(n: int) -> dict:
    for (lo, hi), cfg in BRS_BUDGET.items():
        if lo <= n <= hi:
            return cfg
    return {'ceiling_offset': 3, 'timeout': 120}


# ---------------------------------------------------------------------------
# Single-sample testing
# ---------------------------------------------------------------------------

def test_sample(word: List[Token], n: int, verbose: bool = False) -> dict:
    """Run both reducibility tests on a single Gauss word.

    Returns dict with keys:
        cr, bigon_reducible, bigon_states_explored,
        down_r3_reachable, down_r3_exhaustive,
        down_r3_states_visited, down_r3_wall_time,
        is_counterexample (candidate).
    """
    cfg = _budget_for(n)
    ceiling = n + cfg['ceiling_offset']
    timeout = cfg['timeout']

    cr = crossing_number(word)
    result = {
        "cr": cr,
        "ceiling": ceiling,
        "timeout": timeout,
    }

    # --- Greedy bigon peel ---
    t0 = time.time()
    bigon_ok, bigon_moves, bigon_stats = greedy_bigon_peel_all_orderings(word)
    result["bigon_reducible"] = bigon_ok
    result["bigon_states_explored"] = bigon_stats.get("states_explored", 0)
    result["bigon_wall_time"] = time.time() - t0

    # --- down_r3_only BRS ---
    if verbose:
        print(f"  BRS down_r3_only: ceiling={ceiling}, timeout={timeout}")
    brs = bounded_bfs(
        word, ceiling=ceiling, strategy="down_r3_only",
        time_limit=timeout, verbose=False,
    )
    result["down_r3_reachable"] = brs["reachable"]
    result["down_r3_exhaustive"] = brs.get("restricted_set_exhaustive", False)
    result["down_r3_states_visited"] = brs["states_visited"]
    result["down_r3_wall_time"] = brs["wall_time"]
    result["down_r3_timed_out"] = brs.get("timed_out", False)
    result["down_r3_note"] = brs.get("note", None)

    # Counterexample candidate: not bigon-reducible AND not down_r3-reachable
    result["is_counterexample"] = (not bigon_ok) and (not brs["reachable"])

    return result


# ---------------------------------------------------------------------------
# Per-n sweep
# ---------------------------------------------------------------------------

def sweep_n(
    n: int,
    sample_count: int = 50,
    seed: int = 0xC0FFEE,
    exhaustive: bool = True,
    verbose: bool = False,
) -> dict:
    """Run the full sweep for a single crossing number n.

    Args:
        n: crossing number.
        sample_count: number of random samples (ignored if exhaustive=True).
        seed: RNG seed for sampling.
        exhaustive: if True, use exhaustive enumeration (n <= 6).
        verbose: print progress.

    Returns dict with per-sample records and aggregates.
    """
    if exhaustive and n <= 4:
        if verbose:
            print(f"\n{'='*60}")
            print(f"n={n}: exhaustive enumeration")
        samples = enumerate_classical_unknots(n, verbose=verbose)
    else:
        if verbose:
            print(f"\n{'='*60}")
            print(f"n={n}: random sampling ({sample_count} samples)")
        samples = sample_classical_unknots(n, sample_count, seed=seed, verbose=verbose)

    # Only test confirmed classical unknots (enumerate returns all planar words,
    # which may include non-unknots like trefoil; sample_classical_unknots already
    # filters by unknot verification).
    unknot_samples = [s for s in samples if s.get("is_unknot", True)]
    if verbose:
        total_planar = len(samples)
        print(f"  Testing {len(unknot_samples)}/{total_planar} unknots")

    records = []
    bigon_reducible_count = 0
    down_r3_reachable_count = 0
    counterexample_count = 0

    for idx, sample in enumerate(unknot_samples):
        word = sample["word"]
        result = test_sample(word, n, verbose=verbose)
        result["canonical"] = list(canonical(word))
        records.append(result)

        if result["bigon_reducible"]:
            bigon_reducible_count += 1
        if result["down_r3_reachable"]:
            down_r3_reachable_count += 1
        if result["is_counterexample"]:
            counterexample_count += 1

        if verbose and (idx + 1) % max(1, len(unknot_samples) // 5) == 0:
            print(f"    {idx+1}/{len(unknot_samples)} tested")

    total = len(records)
    aggregates = {
        "n": n,
        "total_samples": total,
        "bigon_reducible": bigon_reducible_count,
        "down_r3_reachable": down_r3_reachable_count,
        "counterexample_candidates": counterexample_count,
        "pct_bigon_reducible": 100.0 * bigon_reducible_count / total if total else 0,
        "pct_down_r3_reachable": 100.0 * down_r3_reachable_count / total if total else 0,
        "pct_counterexample": 100.0 * counterexample_count / total if total else 0,
    }

    if verbose:
        print(f"\n  n={n} aggregates:")
        print(f"    Total: {total}")
        print(f"    Bigon-reducible: {bigon_reducible_count}/{total} "
              f"({aggregates['pct_bigon_reducible']:.1f}%)")
        print(f"    Down-R3-reachable: {down_r3_reachable_count}/{total} "
              f"({aggregates['pct_down_r3_reachable']:.1f}%)")
        print(f"    Counterexample candidates: {counterexample_count}/{total} "
              f"({aggregates['pct_counterexample']:.1f}%)")

    return {
        "n": n,
        "exhaustive": exhaustive and n <= 4,
        "aggregates": aggregates,
        "records": records,
    }


# ---------------------------------------------------------------------------
# Full sweep
# ---------------------------------------------------------------------------

def run_full_sweep(
    n_range: List[int] = None,
    sample_count: int = 50,
    seed: int = 0xC0FFEE,
    verbose: bool = True,
) -> dict:
    """Run sweep over all n in n_range."""
    if n_range is None:
        n_range = list(range(2, 13))

    all_results = {}
    all_counterexamples = []

    for n in n_range:
        # Exhaustive enumeration is only feasible for n <= 4 (at n=5 there are
        # ~113k unsigned words, and at n=6 there are ~39M, making full
        # enumeration impractical even with planarity filtering). For n >= 5
        # we use random sampling via sample_count.
        exhaustive = n <= 4
        data = sweep_n(n, sample_count=sample_count, seed=seed,
                       exhaustive=exhaustive, verbose=verbose)
        all_results[str(n)] = data

        # Collect counterexample candidates
        for rec in data["records"]:
            if rec["is_counterexample"]:
                all_counterexamples.append({
                    "n": n,
                    "canonical": rec["canonical"],
                    "cr": rec["cr"],
                    "bigon_reducible": rec["bigon_reducible"],
                    "down_r3_reachable": rec["down_r3_reachable"],
                })

    # Save counterexamples
    if all_counterexamples:
        ce_path = Path(__file__).parent.parent / "outputs" / "phase3_counterexamples.json"
        ce_path.parent.mkdir(parents=True, exist_ok=True)
        with open(ce_path, "w") as f:
            json.dump(all_counterexamples, f, indent=2)
        if verbose:
            print(f"\n{'='*60}")
            print(f"COUNTEREXAMPLE CANDIDATES: {len(all_counterexamples)}")
            for ce in all_counterexamples:
                print(f"  n={ce['n']}, canonical={ce['canonical']}")
            print(f"Saved to {ce_path}")
    else:
        if verbose:
            print(f"\nNo counterexample candidates found.")

    all_results["_meta"] = {
        "counterexample_count": len(all_counterexamples),
        "counterexample_file": "outputs/phase3_counterexamples.json"
        if all_counterexamples else None,
    }

    return all_results


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Phase 3 scaling experiment")
    parser.add_argument("--n-min", type=int, default=2,
                        help="Minimum crossing number (default: 2)")
    parser.add_argument("--n-max", type=int, default=6,
                        help="Maximum crossing number (default: 6)")
    parser.add_argument("--sample-count", type=int, default=50,
                        help="Samples per n for n > 6")
    parser.add_argument("--seed", type=int, default=0xC0FFEE)
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    n_range = list(range(args.n_min, args.n_max + 1))
    print(f"Phase 3 scaling sweep: n = {n_range}")
    print(f"  Sample count (for n > 6): {args.sample_count}")
    print(f"  Seed: {args.seed}")

    results = run_full_sweep(
        n_range=n_range, sample_count=args.sample_count,
        seed=args.seed, verbose=args.verbose,
    )

    out_path = args.output or (
        Path(__file__).parent.parent / "outputs" / "phase3_scaling_results.json"
    )
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Remove word lists from records to keep output manageable
    slim = {}
    for k, v in results.items():
        if k == "_meta":
            slim[k] = v
        else:
            slim[k] = {
                "n": v["n"],
                "exhaustive": v["exhaustive"],
                "aggregates": v["aggregates"],
                "num_records": len(v["records"]),
            }

    with open(out_path, "w") as f:
        json.dump(slim, f, indent=2)
    print(f"\nAggregates saved to {out_path}")

    # Print summary table
    print(f"\n{'='*80}")
    print(f"{'n':>4} {'Type':<12} {'Total':>8} {'Bigon-Red':>12} "
          f"{'Down-R3':>12} {'Candidates':>12}")
    print(f"{'-'*80}")
    for n in sorted(int(k) for k in results if k != "_meta"):
        data = results[str(n)]
        agg = data["aggregates"]
        etype = "exhaustive" if data["exhaustive"] else "sampled"
        print(f"{n:>4} {etype:<12} {agg['total_samples']:>8} "
              f"{agg['bigon_reducible']:>8}/{agg['total_samples']:<3} "
              f"{agg['down_r3_reachable']:>8}/{agg['total_samples']:<3} "
              f"{agg['counterexample_candidates']:>8}/{agg['total_samples']:<3}")
