"""
Generate the Goeritz unknotting path and save to paths.json.

Two A*-verified paths reaching the unknot without ever exceeding
the initial crossing number (cn=11):

- r1up_r2down: R2_down x3, then (R1_up + R2_down) x4, R1_down.
  12 moves. Each R1_up temporarily adds 1 crossing at a LOWER level
  (e.g., cn=5->6), then R2_down removes 2 crossings (cn=6->4).

- r2up_r2down: R2_down x3, then (R2_up + R2_down + R1_down) x4, R1_down.
  16 moves. R2_up adds 2 crossings, R2_down removes 2, then R1_down
  removes 1 leftover bigon from the inner pair.

The crossing-number barrier (m=1) from Dynnikov/Henrich applies to
R2+R3-only simplification. When R1 moves are allowed, the Goeritz
diagram can be simplified without exceeding its initial crossing number.
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

PATH_R1UP = [
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

PATH_R2UP = [
    ('R2_down', 5, 6),
    ('R2_down', 7, 10),
    ('R2_down', 8, 11),
    ('R2_up', 1, ((13, 1), (14, 1), (14, -1), (13, -1))),
    ('R2_down', 1, 13),
    ('R1_down', 0),
    ('R2_up', 1, ((15, 1), (16, 1), (16, -1), (15, -1))),
    ('R2_down', 2, 15),
    ('R1_down', 0),
    ('R2_up', 1, ((17, 1), (18, 1), (18, -1), (17, -1))),
    ('R2_down', 3, 17),
    ('R1_down', 0),
    ('R2_up', 1, ((19, 1), (20, 1), (20, -1), (19, -1))),
    ('R2_down', 4, 19),
    ('R1_down', 0),
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
        print(f" Step {step:2d}: {move[0]:8s} -> cn={cn}")

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
            print(f" Step {i}: INVALID - {move}")
            similar = [a for a in actions if a[0] == move[0]]
            print(f"  Available: {similar[:5]}")
            return False
        w, nid = apply_action(w, move, nid)
        print(f" Step {i}: cn={crossing_number(w)} [{move[0]}] OK")
    if crossing_number(w) != 0:
        print(f" Final cn={crossing_number(w)} != 0")
        return False
    print(f" Path VALID: reaches unknot in {len(moves)} moves")
    return True


def generate_goeritz_path():
    word = GOERITZ_WORD.copy()
    next_id = 13

    ok1 = _validate_path(list(word), PATH_R1UP, next_id, "R1_up path")
    ok2 = _validate_path(list(word), PATH_R2UP, next_id, "R2_up path")

    if not ok1:
        print("\nERROR: R1_up path validation failed")
        return None

    path1_words, max_cn1 = _apply_and_record(
        list(word), PATH_R1UP, next_id, "R1_up path"
    )
    if ok2:
        path2_words, max_cn2 = _apply_and_record(
            list(word), PATH_R2UP, next_id, "R2_up path"
        )
    else:
        print("\nWARNING: R2_up path validation failed, skipping")
        path2_words = []
        max_cn2 = None

    output = {
        'diagram': 'Goeritz',
        'source': 'A*-discovered and verified path',
        'initial_crossing_number': crossing_number(GOERITZ_WORD),
        'paths': {
            'r1up_r2down': {
                'max_crossings': max_cn1,
                'num_steps': len(PATH_R1UP),
                'moves': [list(m) for m in PATH_R1UP],
                'states': [
                    {
                        'step': i,
                        'word': w,
                        'crossing_number': crossing_number(w),
                        'canonical': str(canonical(w)),
                    }
                    for i, w in enumerate(path1_words)
                ],
            },
        },
    }

    if max_cn2 is not None:
        output['paths']['r2up_r2down'] = {
            'max_crossings': max_cn2,
            'num_steps': len(PATH_R2UP),
            'moves': [list(m) for m in PATH_R2UP],
            'states': [
                {
                    'step': i,
                    'word': w,
                    'crossing_number': crossing_number(w),
                    'canonical': str(canonical(w)),
                }
                for i, w in enumerate(path2_words)
            ],
        }

    output_path = Path(__file__).parent / 'paths.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved Goeritz paths to {output_path}")
    print(f" r1up_r2down: {max_cn1} max crossings, {len(PATH_R1UP)} steps")
    if max_cn2 is not None:
        print(f" r2up_r2down: {max_cn2} max crossings, {len(PATH_R2UP)} steps")
    return output


if __name__ == '__main__':
    generate_goeritz_path()
