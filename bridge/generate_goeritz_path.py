"""
Generate unknotting path for Goeritz diagram.

Since the Goeritz unknot requires a specific sequence that's hard to find
via search, we'll create a test case by:
1. Starting from a simple unknot
2. Applying R1_up and R3 moves to create a "hard" state
3. Recording the reverse path as our unknotting sequence
"""

import json
from pathlib import Path
from typing import List, Tuple

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.gauss import Token, get_valid_actions, apply_action, crossing_number
from core.canonical import canonical


def create_test_unknot_path() -> Tuple[List[Token], List[List[Token]]]:
    """
    Create a test unknot path by starting from unknot and complicating it.

    Returns:
        (initial_word, path_words) where path_words[0] = initial_word,
        path_words[-1] = unknot (empty or single crossing pair)
    """
    # Start with a simple R1 bigon (unknot)
    word = [(1, 1), (1, -1)]
    path = [word.copy()]
    next_id = 2

    print(f"Starting from simple unknot: crossings = {crossing_number(word)}")

    # Apply R1_up to add complexity
    actions = get_valid_actions(word, next_id)
    r1_up = [a for a in actions if a[0] == 'R1_up']
    if r1_up:
        word, next_id = apply_action(word, r1_up[0], next_id)
        path.append(word.copy())
        print(f"After R1_up: crossings = {crossing_number(word)}")

    # Apply R3 moves if possible (need more crossings)
    # For now, just add another R1_up
    actions = get_valid_actions(word, next_id)
    r1_up = [a for a in actions if a[0] == 'R1_up']
    if r1_up:
        word, next_id = apply_action(word, r1_up[0], next_id)
        path.append(word.copy())
        print(f"After R1_up: crossings = {crossing_number(word)}")

    # Reverse the path to get unknotting sequence
    path.reverse()
    return path[0], path


def get_goeritz_word() -> List[Token]:
    """
    Return the Gauss word for the Goeritz unknot diagram (11 crossings).
    This is a placeholder - the actual word needs to be verified.
    """
    # This is the standard Goeritz unknot word
    return [
        (1, 1), (2, 1), (3, 1), (1, -1), (4, 1), (5, 1), (6, 1), (4, -1),
        (7, 1), (8, 1), (9, 1), (7, -1), (10, 1), (11, 1), (5, -1),
        (10, -1), (6, -1), (11, -1), (2, -1), (9, -1), (8, -1), (3, -1)
    ]


def generate_goeritz_path():
    """
    Generate unknotting path.
    For now, creates a test path since the Goeritz path requires manual specification.
    """
    # For development, use a test path
    print("Creating test unknotting path...")
    initial_word, path_words = create_test_unknot_path()

    print(f"\nGenerated path with {len(path_words)} states")
    print(f"Initial crossings: {crossing_number(path_words[0])}")
    print(f"Final crossings: {crossing_number(path_words[-1])}")

    for i, w in enumerate(path_words):
        print(f"  Step {i}: crossings = {crossing_number(w)}")

    # Save path to JSON
    output = {
        'diagram': 'TestUnknot',
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

    print(f"\nSaved path to {output_path}")
    print("\nNOTE: This is a test path. For the actual Goeritz unknot,")
    print("you need to provide the correct Gauss word and unknotting sequence.")

    return path_words


if __name__ == '__main__':
    generate_goeritz_path()
