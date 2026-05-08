"""Unit tests for BRS-based unknot verification.

Includes hand-verified positive controls (empty, simple unknots) and
negative controls (trefoil variants).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.unknot_verify import verify_unknot, UNKNOT_TEST_CASES


def test_all_cases():
    passed = failed = 0
    for idx, (word, expected, desc) in enumerate(UNKNOT_TEST_CASES, 1):
        result = verify_unknot(word, verbose=False, custom_timeout=5)
        result_ok = result['is_unknot']
        if result_ok == expected:
            passed += 1
            status = "PASS"
        else:
            failed += 1
            status = "FAIL"
        print(f"  [{status}] Case {idx}: {desc}")
        print(
            f"         is_unknot={result_ok}, expected={expected} "
            f"(visited={result['states_visited']}, "
            f"time={result['wall_time']:.2f}s)"
        )
    print(f"\n{passed}/{passed+failed} passed, {failed}/{passed+failed} failed")
    return failed == 0


if __name__ == "__main__":
    ok = test_all_cases()
    sys.exit(0 if ok else 1)
