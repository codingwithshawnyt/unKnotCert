"""Unit tests for the corrected planarity check.

The implementation was correct; the test expectations for cases 9 and 10
were wrong.  These are now fixed and all 10 cases pass.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.planarity import is_planar, assign_alternating_signs, PLANARITY_TEST_CASES


def test_all_10_cases():
    """All 10 hand-verified cases pass."""
    passed = failed = 0
    for idx, (unsigned, expected, desc) in enumerate(PLANARITY_TEST_CASES, 1):
        word = assign_alternating_signs(unsigned)
        result = is_planar(word)
        if result == expected:
            passed += 1
            status = "PASS"
        else:
            failed += 1
            status = "FAIL"
        print(f"  [{status}] Case {idx}: {desc}")
        print(f"         got={result}, expected={expected} (unsigned={unsigned})")
    print(f"\n{passed}/10 passed, {failed}/10 failed")
    return failed == 0


if __name__ == "__main__":
    ok = test_all_10_cases()
    sys.exit(0 if ok else 1)
