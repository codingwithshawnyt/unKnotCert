"""
Generate the Goeritz unknotting path and save to paths.json.

Uses an A*-discovered 10-move sequence (3 R2_down, R2_up, R2_down,
R2_down, R2_up, R2_down, R2_down, R1_down) that reaches the unknot
with minimax barrier = 11 (the original crossing count).

Also generates a variant with initial R1_up (barrier = 12).
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

PATH_NO_R1UP = [
    ('R2_down', 10, 11),
    ('R2_down', 6, 9),
    ('R2_down', 5, 8),
    ('R2_up', 8, ((13, 1), (14, 1), (14, -1), (13, -1))),
    ('R2_down', 4, 13),
    ('R2_down', 7, 14),
    ('R2_up', 4, ((15, 1), (16, 1), (16, -1), (15, -1))),
    ('R2_down', 3, 15),
    ('R2_down', 2, 16),
    ('R1_down', 0),
]

PATH_WITH_R1UP = [
    ('R1_up', 1, ((12, 1), (12, -1))),
    ('R2_down', 10, 11),
    ('R2_down', 6, 9),
    ('R2_down', 5, 8),
    ('R2_down', 1, 12),
    ('R2_up', 6, ((13, 1), (14, 1), (14, -1), (13, -1))),
    ('R2_down', 4, 13),
    ('R2_down', 7, 14),
    ('R1_up', 3, ((15, 1), (15, -1))),
    ('R2_down', 3, 15),
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


def generate_goeritz_path():
    word = GOERITZ_WORD.copy()
    next_id = 13

    path1, max_cn1 = _apply_and_record(list(word), PATH_NO_R1UP, next_id, "Without R1_up")
    path2, max_cn2 = _apply_and_record(
        list(word), PATH_WITH_R1UP, next_id, "With R1_up"
    )

    output = {
        'diagram': 'Goeritz',
        'source': 'A*-discovered path',
        'initial_crossing_number': crossing_number(GOERITZ_WORD),
        'paths': {
            'no_r1up': {
                'max_crossings': max_cn1,
                'num_steps': len(PATH_NO_R1UP),
                'moves': [list(m) for m in PATH_NO_R1UP],
                'states': [
                    {
                        'step': i,
                        'word': w,
                        'crossing_number': crossing_number(w),
                        'canonical': str(canonical(w)),
                    }
                    for i, w in enumerate(path1)
                ],
            },
            'with_r1up': {
                'max_crossings': max_cn2,
                'num_steps': len(PATH_WITH_R1UP),
                'moves': [list(m) for m in PATH_WITH_R1UP],
                'states': [
                    {
                        'step': i,
                        'word': w,
                        'crossing_number': crossing_number(w),
                        'canonical': str(canonical(w)),
                    }
                    for i, w in enumerate(path2)
                ],
            },
        },
    }

    output_path = Path(__file__).parent / 'paths.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved Goeritz paths to {output_path}")
    print(f"  no_r1up:  {max_cn1} max crossings, {len(PATH_NO_R1UP)} steps")
    print(f"  with_r1up: {max_cn2} max crossings, {len(PATH_WITH_R1UP)} steps")
    return output


if __name__ == '__main__':
    generate_goeritz_path()
