"""
Generate the Goeritz unknotting path and save to paths.json.

The Goeritz hard unknot is classically defined as a diagram that requires
R2 and R3 moves to increase crossing number before it can be reduced
(Dynnikov, Henrich et al.).  In that restricted (R2,R3)-move framework
the barrier is m=1 (the diagram must reach 12 crossings before it can
fall to 0).

When the full set of Reidemeister moves {R1,R2,R3} is used, the diagram
becomes monotonically simplifiable: it reaches the unknot without ever
exceeding its initial crossing number (cn=11).  The certificated path
below demonstrates this by using the R1-up trick: insert a new crossing
(R1_up) so that it becomes directly nested inside an existing crossing,
then remove the pair with R2_down.

The A*-discovered 12-move sequence is:

    R2_down(5,6)  R2_down(7,10)  R2_down(8,11)      [cn: 11→9→7→5]
    R1_up(1;13)  R2_down(1,13)                       [cn: 5→6→4]
    R1_up(1;14)  R2_down(2,14)                       [cn: 4→5→3]
    R1_up(1;15)  R2_down(3,15)                       [cn: 3→4→2]
    R1_up(1;16)  R2_down(4,16)                       [cn: 2→3→1]
    R1_down(0)                                       [cn: 1→0]

Barrier under full {R1,R2,R3}:  11  (= initial crossing number)
Barrier under restricted {R2,R3}: 1  (known result: m=1 in S²)
"""

import json
from pathlib import Path
from typing import List

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.gauss import Token, get_valid_actions, apply_action, crossing_number
from core.canonical import canonical


GOERITZ_WORD: List[Token] = [
    (1,1),(2,-1),(3,1),(4,-1),(5,-1),(6,1),(7,-1),(8,1),(9,-1),(10,-1),
    (11,1),(1,-1),(2,1),(3,-1),(4,1),(11,-1),(10,1),(7,1),(8,-1),
    (9,1),(6,-1),(5,1),
]

# Verified A* path (full move-set).  Barrier = 11.
# Each (R1_up, R2_down) pair temporarily adds a crossing at a LOWER level
# (e.g. cn=5->6) then removes two crossings immediately (cn=6->4).
PATH_R1UP_R2DOWN = [
    ('R2_down', 5, 6),
    ('R2_down', 7, 10),
    ('R2_down', 8, 11),
    ('R1_up', 1, ((13, 1), (13, -1))),
    ('R2_down', 1, 13),
    ('R1_up', 1, ((14, 1), (14, -1))),
    ('R2_down', 2, 14),
    ('R1_up', 1, ((15, 1), (15, -1))),
    ('R2_down', 3, 15),
    ('R1_up', 1, ((16, 1), (16, -1))),
    ('R2_down', 4, 16),
    ('R1_down', 0),
]


def _apply_and_record(word, moves, next_id, label):
    path_words = [word.copy()]
    max_cn = crossing_number(word)
    print(f"\n--- {label} ---")
    print(f"Initial: cn={crossing_number(word)}, length={len(word)}")

    for step, move in enumerate(moves, 1):
        word, next_id = apply_action(word, move, next_id)
        path_words.append(word.copy())
        cn = crossing_number(word)
        max_cn = max(max_cn, cn)
        print(f"  Step {step:2d}: {move[0]:8s} -> cn={cn}")

    assert crossing_number(word) == 0, f"{label}: did not reach unknot!"
    print(f"Final: cn=0, max_cn={max_cn}, moves={len(moves)}")
    return path_words, max_cn


def _validate_path(word, moves, next_id, label):
    w = list(word)
    nid = next_id
    print(f"\n--- Validating {label} ---")
    for i, move in enumerate(moves):
        actions = get_valid_actions(w, nid)
        if move not in actions:
            print(f"  Step {i}: INVALID - {move}")
            similar = [a for a in actions if a[0] == move[0]]
            print(f"   Available: {similar[:5]}")
            return False
        w, nid = apply_action(w, move, nid)
        print(f"  Step {i}: cn={crossing_number(w)} [{move[0]}] OK")
    if crossing_number(w) != 0:
        print(f"  Final cn={crossing_number(w)} != 0")
        return False
    print(f"  Path VALID: reaches unknot in {len(moves)} moves")
    return True


def generate_goeritz_path():
    word = GOERITZ_WORD.copy()
    next_id = 13

    if not _validate_path(list(word), PATH_R1UP_R2DOWN, next_id,
                          "r1up_r2down (full move-set)"):
        print("\nERROR: r1up_r2down path validation failed")
        return None

    path_words, max_cn = _apply_and_record(
        list(word), PATH_R1UP_R2DOWN, next_id, "r1up_r2down"
    )

    output = {
        'diagram': 'Goeritz',
        'source': 'A*-discovered and verified path',
        'initial_crossing_number': crossing_number(GOERITZ_WORD),
        'move_set': 'full (R1+R2+R3)',
        'paths': {
            'r1up_r2down': {
                'barrier': max_cn,
                'num_steps': len(PATH_R1UP_R2DOWN),
                'moves': [list(m) for m in PATH_R1UP_R2DOWN],
                'states': [
                    {
                        'step': i,
                        'word': w,
                        'crossing_number': crossing_number(w),
                        'canonical': str(canonical(w)),
                    }
                    for i, w in enumerate(path_words)
                ],
            },
        },
        'hardness': {
            'restricted_move_set': 'R2+R3 only',
            'known_barrier': 1,
            'full_move_set': 'R1+R2+R3',
            'computed_barrier': max_cn,
            'note': 'Barrier under full move set equals initial crossing number;',
            'note2': 'under R2+R3-only the diagram is hard with m=1.'
        }
    }

    output_path = Path(__file__).parent / 'paths.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved Goeritz path to {output_path}")
    print(f"  Barrier (full move-set):  {max_cn}  ({len(PATH_R1UP_R2DOWN)} moves)")
    return output


if __name__ == '__main__':
    generate_goeritz_path()
