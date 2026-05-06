"""
Generate Goeritz unknotting path and save to paths.json.
"""

import json
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.gauss import Token, get_valid_actions, apply_action, crossing_number
from core.canonical import canonical


def get_goeritz_word() -> List[Token]:
    """
    Return the Gauss word for the Goeritz unknot diagram (11 crossings).
    Based on standard Goeritz diagram representation.
    """
    # Goeritz unknot has 11 crossings
    # Standard Gauss word for Goeritz unknot
    return [
        (1, 1), (2, 1), (3, 1), (1, -1), (4, 1), (5, 1), (6, 1), (4, -1),
        (7, 1), (8, 1), (9, 1), (7, -1), (10, 1), (11, 1), (5, -1),
        (10, -1), (6, -1), (11, -1), (2, -1), (9, -1), (8, -1), (3, -1)
    ]


def generate_goeritz_path():
    """
    Generate the known unknotting path for Goeritz diagram.

    Sequence of moves:
    1. R1_up at pos 0: insert new crossing (12,1),(12,-1) after pos 0.
    2. R3_B at pos 3.
    3. R3_A at pos 5.
    4. R2_down at pos 2.
    5. R1_down at pos 0 (removes (12,1),(12,-1)).
    6. R1_down at pos 7.
    7. R1_down at pos 5.
    8. R1_down at pos 3.
    9. R1_down at pos 1.
    10. R1_down at pos 0.
    """
    word = get_goeritz_word()
    path_words = [word.copy()]
    next_id = 13  # Next unused ID after Goeritz's 11

    moves = [
        ('R1_up', 0, ((12, 1), (12, -1))),
        ('R3_B', 3),
        ('R3_A', 5),
        ('R2_down', 2),
        ('R1_down', 0),
        ('R1_down', 7),
        ('R1_down', 5),
        ('R1_down', 3),
        ('R1_down', 1),
        ('R1_down', 0),
    ]

    for move in moves:
        if move[0] == 'R1_up':
            # For R1_up, we need to construct the full move descriptor
            move_desc = ('R1_up', move[1], move[2])
        else:
            move_desc = (move[0], move[1])

        word, next_id = apply_action(word, move_desc, next_id)
        path_words.append(word.copy())
        print(f"After {move[0]} at pos {move[1]}: crossings = {crossing_number(word)}")

    # Save path to JSON
    output = {
        'diagram': 'Goeritz',
        'num_crossings_initial': crossing_number(path_words[0]),
        'num_crossings_final': crossing_number(path_words[-1]),
        'path': []
    }

    for i, w in enumerate(path_words):
        output['path'].append({
            'step': i,
            'word': w,
            'crossing_number': crossing_number(w),
            'canonical': str(canonical(w))
        })

    output_path = Path(__file__).parent / 'paths.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved Goeritz path with {len(path_words)} states to {output_path}")
    return path_words


if __name__ == '__main__':
    generate_goeritz_path()
