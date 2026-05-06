"""
Gauss word utilities and Reidemeister moves for unknot certification.
"""

from typing import List, Tuple, Optional

Token = Tuple[int, int]  # (crossing_id, sign) where sign = +1 (over) or -1 (under)
MoveDescriptor = Tuple  # First element is move type string


def get_valid_actions(word: List[Token], next_id: int) -> List[MoveDescriptor]:
    """
    Detect all valid Reidemeister moves for a Gauss word representation of a knot diagram.

    Move types:
    - 'R1_down': Remove a bigon (consecutive tokens with same ID, opposite signs)
    - 'R2_down': Remove two crossings in R2 configuration
    - 'R3_A', 'R3_B': Perform R3 move (type A or B)
    - 'R1_up': Insert a new bigon (R1 reverse)
    """
    if not word:
        return []

    L = len(word)
    W2 = word + word  # Handle cyclicity
    actions = []

    # Detect down moves (simplifications)
    for i in range(L):
        # R1 down: consecutive tokens with same crossing ID and opposite signs
        if W2[i][0] == W2[i+1][0] and W2[i][1] == -W2[i+1][1]:
            actions.append(('R1_down', i % L))

        # R2 down: pattern (a,s1)(b,s2)(a,-s1)(b,-s2) with a != b
        if i + 3 < len(W2):
            a1, s1 = W2[i]
            b1, s2 = W2[i+1]
            a2, ns1 = W2[i+2]
            b2, ns2 = W2[i+3]
            if (a1 == a2 and b1 == b2 and a1 != b1 and
                s1 == -ns1 and s2 == -ns2):
                actions.append(('R2_down', i % L))

        # R3 type A: (a,s1)(b,s2)(c,s3)(a,-s1)(b,-s2)(c,-s3)
        if i + 5 < len(W2):
            a1, s1 = W2[i]
            b1, s2 = W2[i+1]
            c1, s3 = W2[i+2]
            a2, ns1 = W2[i+3]
            b2, ns2 = W2[i+4]
            c2, ns3 = W2[i+5]
            if (a1 == a2 and b1 == b2 and c1 == c2 and
                a1 != b1 and a1 != c1 and b1 != c1 and
                s1 == -ns1 and s2 == -ns2 and s3 == -ns3):
                actions.append(('R3_A', i % L))

        # R3 type B: (a,s1)(c,s3)(b,s2)(a,-s1)(c,-s3)(b,-s2)
        if i + 5 < len(W2):
            a1, s1 = W2[i]
            c1, s3 = W2[i+1]
            b1, s2 = W2[i+2]
            a2, ns1 = W2[i+3]
            c2, ns3 = W2[i+4]
            b2, ns2 = W2[i+5]
            if (a1 == a2 and b1 == b2 and c1 == c2 and
                a1 != b1 and a1 != c1 and b1 != c1 and
                s1 == -ns1 and s2 == -ns2 and s3 == -ns3):
                actions.append(('R3_B', i % L))

    # Detect up moves (add complexity - not typically used for unknotting)
    # R1 up: insert a new bigon at any position
    for pos in range(L + 1):
        new_id = next_id
        actions.append(('R1_up', pos, ((new_id, 1), (new_id, -1))))

    return actions


def apply_action(word: List[Token], move: MoveDescriptor, next_id: int) -> Tuple[List[Token], int]:
    """
    Apply a Reidemeister move to the Gauss word.

    Returns:
        (new_word, new_next_id)
    """
    move_type = move[0]

    if move_type == 'R1_down':
        pos = move[1]
        # Remove two consecutive tokens at pos
        new_word = word[:pos] + word[pos+2:]
        return new_word, next_id

    elif move_type == 'R2_down':
        pos = move[1]
        # Remove four tokens at pos, pos+1, pos+2, pos+3
        # Need to handle wrap-around
        L = len(word)
        indices_to_remove = {(pos + i) % L for i in range(4)}
        new_word = [word[i] for i in range(L) if i not in indices_to_remove]
        return new_word, next_id

    elif move_type == 'R3_A':
        pos = move[1]
        # R3_A: reorder the 6 tokens from (a,b,c,a,b,c) to (a,c,b,a,c,b) pattern
        L = len(word)
        # Get the 6 tokens
        tokens = [word[(pos + i) % L] for i in range(6)]
        # New order for R3_A -> R3_B pattern
        # Original: (a,s1)(b,s2)(c,s3)(a,-s1)(b,-s2)(c,-s3)
        # After R3_A: (a,s1)(c,s3)(b,s2)(a,-s1)(c,-s3)(b,-s2)
        new_order = [0, 2, 1, 3, 5, 4]
        new_tokens = [tokens[i] for i in new_order]
        # Reconstruct word
        indices_to_replace = [(pos + i) % L for i in range(6)]
        new_word = word.copy()
        for idx, token in zip(indices_to_replace, new_tokens):
            new_word[idx] = token
        return new_word, next_id

    elif move_type == 'R3_B':
        pos = move[1]
        # R3_B: reorder from (a,c,b,a,c,b) to (a,b,c,a,b,c) pattern
        L = len(word)
        tokens = [word[(pos + i) % L] for i in range(6)]
        # Original: (a,s1)(c,s3)(b,s2)(a,-s1)(c,-s3)(b,-s2)
        # After R3_B: (a,s1)(b,s2)(c,s3)(a,-s1)(b,-s2)(c,-s3)
        new_order = [0, 2, 1, 3, 5, 4]
        new_tokens = [tokens[i] for i in new_order]
        indices_to_replace = [(pos + i) % L for i in range(6)]
        new_word = word.copy()
        for idx, token in zip(indices_to_replace, new_tokens):
            new_word[idx] = token
        return new_word, next_id

    elif move_type == 'R1_up':
        pos = move[1]
        new_tokens = list(move[2])
        new_id = new_tokens[0][0]
        new_word = word[:pos] + new_tokens + word[pos:]
        return new_word, max(next_id, new_id + 1)

    else:
        raise ValueError(f"Unknown move type: {move_type}")


def crossing_number(word: List[Token]) -> int:
    """Return the number of distinct crossing IDs in the word."""
    return len(set(c for c, _ in word))
