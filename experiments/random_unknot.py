"""Random classical unknot Gauss word generator (Phase 3).

Two entry points:
- enumerate_classical_unknots(n): exhaustive for n <= 6.
- sample_classical_unknots(n, count, seed): random sample for n in 7..12.

Pipeline:
1. Generate unsigned double-occurrence words (chord diagrams)
2. Filter by Read--Rosenstiehl planarity
3. Assign alternating signs (+1 first appearance, -1 second)
4. Verify via BRS with bigon R2

Seed for reproducibility: 0xC0FFEE
"""

import sys
import json
import math
import random
import itertools
import time
from pathlib import Path
from typing import List, Tuple, Iterator, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.planarity import is_planar, assign_alternating_signs
from core.unknot_verify import verify_unknot
from core.gauss import Token, crossing_number


# ---------------------------------------------------------------------------
# Unsigned double-occurrence word generation
# ---------------------------------------------------------------------------

def _generate_unsigned_words(n: int) -> Iterator[List[int]]:
    """Generate all unsigned double-occurrence words for n chord labels.

    Yields lists of length 2n where each label 1..n appears exactly twice.
    Uses recursive backtracking.
    """
    labels = list(range(1, n + 1))
    counts = {k: 0 for k in labels}
    word = [0] * (2 * n)

    def backtrack(pos: int):
        if pos == 2 * n:
            yield word[:]
            return
        for label in labels:
            if counts[label] < 2:
                counts[label] += 1
                word[pos] = label
                yield from backtrack(pos + 1)
                counts[label] -= 1

    yield from backtrack(0)


def enumerate_unsigned_words(n: int) -> List[List[int]]:
    """Return all unsigned double-occurrence words for n labels."""
    return list(_generate_unsigned_words(n))


def _count_unsigned(n: int) -> int:
    """Number of unsigned double-occurrence words: (2n)! / 2^n."""
    return math.factorial(2 * n) // (2 ** n)


# ---------------------------------------------------------------------------
# Filtering and signing
# ---------------------------------------------------------------------------

def _make_signed(unsigned: List[int]) -> List[Token]:
    """Attach alternating signs: +1 on first appearance, -1 on second."""
    seen = set()
    result = []
    for cid in unsigned:
        if cid not in seen:
            result.append((cid, +1))
            seen.add(cid)
        else:
            result.append((cid, -1))
    return result


# ---------------------------------------------------------------------------
# Exhaustive enumeration
# ---------------------------------------------------------------------------

def enumerate_classical_unknots(
    n: int,
    max_samples: Optional[int] = None,
    verbose: bool = False,
) -> List[dict]:
    """Exhaustively enumerate all classical unknot Gauss words with n crossings.

    Pipeline:
    1. Generate all unsigned double-occurrence words.
    2. Filter by planarity.
    3. Filter by BRS-verification (bigon R2, budget table).

    Returns list of dicts with keys:
        unsigned_word, word, is_unknot, states_visited, wall_time, size.
    """
    if n < 0 or n > 6:
        verbose_warn = f"  Warning: exhaustive enumeration for n={n} may be infeasible "
        if verbose:
            print(verbose_warn + str("({:.0e} unsigned words)".format(_count_unsigned(n))))

    total_unsigned = _count_unsigned(n)
    if verbose:
        print(f"  Unsigned words to enumerate: {total_unsigned:.0e}")

    results = []
    planar_count = 0
    unknot_count = 0
    t0 = time.time()

    for idx, unsigned in enumerate(_generate_unsigned_words(n)):
        if max_samples is not None and idx >= max_samples:
            break

        if verbose and idx > 0 and idx % max(1, total_unsigned // 20) == 0:
            elapsed = time.time() - t0
            pct = 100.0 * idx / total_unsigned
            print(f"    {idx}/{total_unsigned} ({pct:.0f}%), {elapsed:.1f}s")

        word = _make_signed(unsigned)
        planar = is_planar(word)
        if not planar:
            continue

        planar_count += 1

        vr = verify_unknot(word, verbose=False)
        record = {
            "unsigned_word": unsigned,
            "word": word,
            "cr": n,
            "is_unknot": vr["is_unknot"],
            "states_visited": vr["states_visited"],
            "wall_time": vr["wall_time"],
        }
        results.append(record)
        if vr["is_unknot"]:
            unknot_count += 1

    elapsed = time.time() - t0
    if verbose:
        print(f"  Done: {len(results)} planar words, {unknot_count} unknots, {elapsed:.1f}s")

    return results


# ---------------------------------------------------------------------------
# Random sampling
# ---------------------------------------------------------------------------

def _random_unsigned_word(n: int, rng: random.Random) -> List[int]:
    """Generate a uniformly random unsigned double-occurrence word of length 2n.

    Sampling is uniform over double-occurrence sequences of length 2n
    (not over chord diagrams modulo dihedral symmetry — this is acceptable
    for our use because we canonicalize downstream).

    Implementation: start with the multiset [1, 1, 2, 2, ..., n, n] and
    shuffle uniformly via Fisher--Yates.  Each distinct word occurs with
    probability (n! * 2^n) / (2n)!, reflecting the (n! * 2^n)-fold
    redundancy from label permutation and endpoint-swap symmetry.
    """
    word = [i for i in range(1, n + 1) for _ in range(2)]
    rng.shuffle(word)
    return word


def sample_classical_unknots(
    n: int,
    count: int,
    seed: int = 0xC0FFEE,
    max_attempts: Optional[int] = None,
    verbose: bool = False,
) -> List[dict]:
    """Sample *count* distinct classical unknot Gauss words with n crossings.

    Generates random unsigned words, filters by planarity and BRS-verification.
    Skips duplicates (by canonical form).

    Returns list of records (same format as enumerate_classical_unknots).
    """
    rng = random.Random(seed)
    max_attempts = max_attempts or 100 * count

    results = []
    seen_canonical = set()
    attempt = 0
    skipped_planar = 0
    skipped_nonunknot = 0
    t0 = time.time()

    while len(results) < count and attempt < max_attempts:
        attempt += 1
        unsigned = _random_unsigned_word(n, rng)
        word = _make_signed(unsigned)

        canon = tuple(word)
        if canon in seen_canonical:
            continue

        planar = is_planar(word)
        if not planar:
            continue

        skipped_planar += 1

        vr = verify_unknot(word, verbose=False)
        if not vr["is_unknot"]:
            skipped_nonunknot += 1
            continue

        seen_canonical.add(canon)
        record = {
            "unsigned_word": unsigned,
            "word": word,
            "cr": n,
            "is_unknot": True,
            "states_visited": vr["states_visited"],
            "wall_time": vr["wall_time"],
        }
        results.append(record)

        if verbose and len(results) % max(1, count // 10) == 0:
            print(f"    sampled {len(results)}/{count} (attempt {attempt})")

    elapsed = time.time() - t0
    if verbose:
        pct = 100.0 * count / attempt if attempt > 0 else 0
        print(f"  Sampled {len(results)}/{count} in {attempt} attempts "
              f"({pct:.1f}%), {elapsed:.1f}s")
        print(f"    planar skipped: {skipped_planar}, non-unknot skipped: {skipped_nonunknot}")

    return results


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate random classical unknots")
    parser.add_argument("mode", choices=["enumerate", "sample"],
                        help="exhaustive enumeration or random sampling")
    parser.add_argument("--n", type=int, default=3, help="crossing number")
    parser.add_argument("--count", type=int, default=10,
                        help="number of samples (sample mode)")
    parser.add_argument("--seed", type=int, default=0xC0FFEE)
    parser.add_argument("--max-samples", type=int, default=None,
                        help="max unsigned words to check (enumerate mode)")
    parser.add_argument("--output", type=str, default=None,
                        help="JSON output path")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if args.mode == "enumerate":
        results = enumerate_classical_unknots(
            args.n, max_samples=args.max_samples, verbose=args.verbose,
        )
    else:
        results = sample_classical_unknots(
            args.n, args.count, seed=args.seed, verbose=args.verbose,
        )

    print(f"\n{'='*60}")
    print(f"Total: {len(results)} classical unknot Gauss words (n={args.n})")
    if results:
        print(f"Example: cr={results[0]['cr']}, "
              f"unsigned={results[0]['unsigned_word']}")
        print(f"  states_visited={results[0]['states_visited']}, "
              f"time={results[0]['wall_time']:.3f}s")

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Saved to {out_path}")
    elif args.verbose:
        out_path = Path(__file__).parent.parent / "outputs" / f"phase3_unknots_n{args.n}.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Auto-saved to {out_path}")
