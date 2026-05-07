"""
Gauss word utilities and Reidemeister moves for unknot certification.

A Gauss word is a cyclic list of tokens (crossing_id, sign).
Each crossing_id appears exactly twice: once with sign +1, once with -1.

Reidemeister moves in a Gauss word:
  R1_down: adjacent pair (a,+1)(a,-1) or (a,-1)(a,+1) — a bigon.
  R1_up:   insert an adjacent pair at any position.
  R2_down: two crossings a,b in nesting: a contains b.
           Removes both crossings (4 tokens).
  R2_up:   insert two nested pairs at a position.
  R3_A:    three mutually linked crossings in order a1 b1 c1 a2 b2 c2.
           Result: a1 c1 b1 a2 c2 b2 (swap b,c roles).
  R3_B:    three mutually linked crossings in order a1 c1 b1 a2 c2 b2.
           Result: a1 b1 c1 a2 b2 c2 (swap b,c roles).

Move descriptors identify crossings by ID, not position, for robustness.
"""

from typing import List, Tuple, Dict, Set

Token = Tuple[int, int]
MoveDescriptor = Tuple


def crossing_number(word: List[Token]) -> int:
    return len(set(c for c, _ in word))


def _pair_positions(word: List[Token]) -> Dict[int, Tuple[int, int, int, int]]:
    """
    For each crossing id, find positions and signs.
    Returns {cid: (pos1, sign1, pos2, sign2)} with pos1 < pos2.
    """
    first: Dict[int, Tuple[int, int]] = {}
    result: Dict[int, Tuple[int, int, int, int]] = {}
    for i, (cid, s) in enumerate(word):
        if cid not in first:
            first[cid] = (i, s)
        else:
            p1, s1 = first[cid]
            result[cid] = (p1, s1, i, s)
    return result


def _is_nested(pairs, a, b):
    """True if a's pair nests b's pair: a1 < b1 < b2 < a2."""
    a1, _, a2, _ = pairs[a]
    b1, _, b2, _ = pairs[b]
    return a1 < b1 < b2 < a2


def get_valid_actions(word: List[Token], next_id: int) -> List[MoveDescriptor]:
    """Detect all valid Reidemeister moves for a Gauss word.

    Returns list of move descriptors.  Down-moves use crossing IDs;
    up-moves use positions and new tokens.
    """
    if not word:
        return []

    L = len(word)
    W2 = word + word
    actions: List[MoveDescriptor] = []
    seen = set()

    pairs = _pair_positions(word)
    cids = sorted(pairs.keys())

    # ---- R1 down ----
    # Adjacent tokens (cyclic) with same crossing ID and opposite signs.
    for i in range(L):
        if W2[i][0] == W2[i + 1][0] and W2[i][1] == -W2[i + 1][1]:
            desc = ('R1_down', i % L)
            if desc not in seen:
                seen.add(desc)
                actions.append(desc)

    # ---- R2 down ----
    # Crossing a (outer) contains exactly one crossing b (inner), meaning:
    #   a1 < b1 < b2 < a2  AND  no other crossing c is nested in b
    #   while also nested in a (i.e., b is the *innermost* nested crossing
    #   that is directly nested in a without another crossing between them).
    #
    # Actually, R2_down removes any two crossings where one is directly
    # nested inside the other with no other crossing nested between them.
    # More precisely: a nests b, and there is no crossing c such that
    # a nests c and c nests b.
    # But for Gauss words, R2 means the two crossings form a bigon-like
    # region. The condition is: a nests b and they are "adjacent" in the
    # nesting hierarchy (no crossing in between).
    #
    # Simplification: a nests b, and b is directly nested in a
    # (no crossing c with a nesting c and c nesting b).
    for a in cids:
        a1, sa1, a2, sa2 = pairs[a]
        if sa1 != -sa2:
            continue
        directly_nested = []
        for b in cids:
            if b == a:
                continue
            b1, sb1, b2, sb2 = pairs[b]
            if sb1 != -sb2:
                continue
            if not (a1 < b1 < b2 < a2):
                continue
            # Check b is directly nested in a (no c between them)
            is_direct = True
            for c in cids:
                if c == a or c == b:
                    continue
                c1, sc1, c2, sc2 = pairs[c]
                if sc1 != -sc2:
                    continue
                if a1 < c1 < c2 < a2 and c1 < b1 < b2 < c2:
                    is_direct = False
                    break
                if a1 < c1 < b1 < b2 < c2 < a2:
                    is_direct = False
                    break
            if is_direct:
                directly_nested.append(b)
        for b in directly_nested:
            desc = ('R2_down', a, b)
            if desc not in seen:
                seen.add(desc)
                actions.append(desc)

    # ---- R3 ----
    # Three mutually linked crossings a, b, c where each pair is linked
    # (not nested, not disjoint). The six first-appearances in cyclic order
    # determine the type.
    #
    # Type A: a1 b1 c1 a2 b2 c2  ->  a1 c1 b1 a2 c2 b2
    # Type B: a1 c1 b1 a2 c2 b2  ->  a1 b1 c1 a2 b2 c2
    #
    # "Mutually linked" means each pair (a,b), (a,c), (b,c) is linked:
    # for each pair, one member's first appearance is between the other's
    # two appearances, but NOT nested.
    for ai, a in enumerate(cids):
        a1, sa1, a2, sa2 = pairs[a]
        if sa1 != -sa2:
            continue
        for bi in range(ai + 1, len(cids)):
            b = cids[bi]
            b1, sb1, b2, sb2 = pairs[b]
            if sb1 != -sb2:
                continue
            if not _is_linked(pairs, a, b):
                continue
            for ci in range(bi + 1, len(cids)):
                c = cids[ci]
                c1, sc1, c2, sc2 = pairs[c]
                if sc1 != -sc2:
                    continue
                if not _is_linked(pairs, a, c):
                    continue
                if not _is_linked(pairs, b, c):
                    continue
                # Three mutually linked crossings — check cyclic order
                six = [(a1, 'a1'), (b1, 'b1'), (c1, 'c1'),
                       (a2, 'a2'), (b2, 'b2'), (c2, 'c2')]
                six.sort()
                order = ''.join(label for _, label in six)
                if order == 'a1b1c1a2b2c2':
                    desc = ('R3_A', a, b, c)
                    if desc not in seen:
                        seen.add(desc)
                        actions.append(desc)
                elif order == 'a1c1b1a2c2b2':
                    desc = ('R3_B', a, b, c)
                    if desc not in seen:
                        seen.add(desc)
                        actions.append(desc)
                elif order == 'b1a1c1b2a2c2':
                    desc = ('R3_A', b, a, c)
                    if desc not in seen:
                        seen.add(desc)
                        actions.append(desc)
                elif order == 'c1a1b1c2a2b2':
                    desc = ('R3_B', c, a, b)
                    if desc not in seen:
                        seen.add(desc)
                        actions.append(desc)
                elif order == 'b1c1a1b2c2a2':
                    desc = ('R3_A', b, c, a)
                    if desc not in seen:
                        seen.add(desc)
                        actions.append(desc)
                elif order == 'c1b1a1c2b2a2':
                    desc = ('R3_B', c, b, a)
                    if desc not in seen:
                        seen.add(desc)
                        actions.append(desc)

    # ---- R1 up ----
    for pos in range(L + 1):
        new_id = next_id
        desc = ('R1_up', pos, ((new_id, 1), (new_id, -1)))
        actions.append(desc)

    # ---- R2 up ----
    for pos in range(L + 1):
        outer_id = next_id
        inner_id = next_id + 1
        desc = ('R2_up', pos, ((outer_id, 1), (inner_id, 1),
                               (inner_id, -1), (outer_id, -1)))
        actions.append(desc)

    return actions


def _is_linked(pairs, a, b):
    """Two crossings are linked if each has one endpoint inside the other's span."""
    a1, _, a2, _ = pairs[a]
    b1, _, b2, _ = pairs[b]
    return (a1 < b1 < a2 < b2) or (b1 < a1 < b2 < a2)


def apply_action(word: List[Token], move: MoveDescriptor, next_id: int
                 ) -> Tuple[List[Token], int]:
    """Apply a Reidemeister move. Returns (new_word, new_next_id)."""
    move_type = move[0]

    if move_type == 'R1_down':
        pos = move[1]
        L = len(word)
        i1 = pos
        i2 = (pos + 1) % L
        if i1 < i2:
            new_word = word[:i1] + word[i2 + 1:]
        else:
            new_word = word[1:-1]
        return new_word, next_id

    elif move_type == 'R2_down':
        outer_cid = move[1]
        inner_cid = move[2]
        to_remove = {outer_cid, inner_cid}
        new_word = [(c, s) for c, s in word if c not in to_remove]
        return new_word, next_id

    elif move_type == 'R3_A':
        a_cid, b_cid, c_cid = move[1], move[2], move[3]
        pairs = _pair_positions(word)
        # R3_A: order a1 b1 c1 a2 b2 c2 -> a1 c1 b1 a2 c2 b2
        # Swap b and c tokens at their positions
        b_pos = sorted([i for i, (c, _) in enumerate(word) if c == b_cid])
        c_pos = sorted([i for i, (c, _) in enumerate(word) if c == c_cid])
        b_tokens = [word[i] for i in b_pos]
        c_tokens = [word[i] for i in c_pos]
        new_word = list(word)
        for i, tok in zip(b_pos, c_tokens):
            new_word[i] = tok
        for i, tok in zip(c_pos, b_tokens):
            new_word[i] = tok
        return new_word, next_id

    elif move_type == 'R3_B':
        a_cid, b_cid, c_cid = move[1], move[2], move[3]
        # R3_B: order a1 c1 b1 a2 c2 b2 -> a1 b1 c1 a2 b2 c2
        # Swap b and c tokens at their positions
        b_pos = sorted([i for i, (c, _) in enumerate(word) if c == b_cid])
        c_pos = sorted([i for i, (c, _) in enumerate(word) if c == c_cid])
        b_tokens = [word[i] for i in b_pos]
        c_tokens = [word[i] for i in c_pos]
        new_word = list(word)
        for i, tok in zip(b_pos, c_tokens):
            new_word[i] = tok
        for i, tok in zip(c_pos, b_tokens):
            new_word[i] = tok
        return new_word, next_id

    elif move_type == 'R1_up':
        pos = move[1]
        new_tokens = list(move[2])
        new_id = new_tokens[0][0]
        new_word = word[:pos] + new_tokens + word[pos:]
        return new_word, max(next_id, new_id + 1)

    elif move_type == 'R2_up':
        pos = move[1]
        new_tokens = list(move[2])
        max_id = max(t[0] for t in new_tokens)
        new_word = word[:pos] + new_tokens + word[pos:]
        return new_word, max(next_id, max_id + 1)

    else:
        raise ValueError(f"Unknown move type: {move_type}")
