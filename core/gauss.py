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

from typing import List, Tuple, Dict, Set, Optional

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


def get_valid_actions(word: List[Token], next_id: int,
                     bigon_r2: bool = False) -> List[MoveDescriptor]:
    """Detect all valid Reidemeister moves for a Gauss word.

    Args:
        word: The Gauss word.
        next_id: Next available crossing ID for up-moves.
        bigon_r2: If True, use bigon condition for R2_down (classical Reidemeister
                  move). If False, use permissive direct-nesting condition
                  (algebraic/virtual move, the default for barrier computation).

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
    # R2-down is well-defined only on *nested* pairs: chord a directly
    # nests chord b (a1 < b1 < b2 < a2), with no third chord strictly
    # between them in the nesting hierarchy. Two interleaved chords
    # (a1 < b1 < a2 < b2) are NOT R2-eligible in any variant — deleting
    # them would collapse a genuine linking structure (e.g., the trefoil
    # pattern (1,2,3,1,2,3) has pairwise-interleaved chords but is not
    # R2-reducible in any step).
    #
    # The bigon_r2 flag switches the outer-arc emptiness condition:
    #   - bigon_r2=False (permissive): directly-nested pair suffices
    #     (the "algebraic virtual" R2-down used throughout this paper's
    #     barrier computations).
    #   - bigon_r2=True (bigon): additionally requires the two outer
    #     arcs (a1, b1) and (b2, a2) to be empty of other chord
    #     endpoints (genuine classical R2 on a chord diagram).
    if bigon_r2:
        # Classical (bigon) R2-down: nested + empty outer arcs.
        for outer, inner in get_bigon_R2_pairs(word):
            desc = ('R2_down', outer, inner)
            if desc not in seen:
                seen.add(desc)
                actions.append(desc)
    else:
        # Permissive R2-down: directly-nested pair with opposite signs,
        # no outer-arc condition.
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
                # Check b is directly nested in a (no c strictly between them)
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


def _cyclic_interval_empty(word_len: int, occupied: Set[int], start: int, end: int) -> bool:
    """Check if the open cyclic interval (start, end) contains no occupied positions.

    Positions are 0-indexed on a circle of length word_len.
    The interval is the set of positions strictly between start and end
    when traversing clockwise from start to end.
    """
    if start == end:
        return True
    pos = (start + 1) % word_len
    while pos != end:
        if pos in occupied:
            return False
        pos = (pos + 1) % word_len
    return True


def is_bigon_R2_down(word: List[Token], outer_cid: int, inner_cid: int) -> bool:
    """Check whether (outer, inner) is a bigon R2-down pair.

    Requires:
    1. outer nests inner in the cyclic order: i1 < j1 < j2 < i2
    2. The two outer arcs (i1, j1) and (j2, i2) contain no endpoints
       of any other chord (empty outer arcs = bigon condition).
    3. The sign condition: outer has opposite signs at its two endpoints,
       inner has opposite signs at its two endpoints.
    """
    if not word:
        return False
    L = len(word)
    pairs = _pair_positions(word)

    if outer_cid not in pairs or inner_cid not in pairs:
        return False

    i1, si1, i2, si2 = pairs[outer_cid]
    j1, sj1, j2, sj2 = pairs[inner_cid]

    if si1 != -si2:
        return False
    if sj1 != -sj2:
        return False

    if not (i1 < j1 < j2 < i2):
        return False

    occupied = set(range(L))
    occupied.discard(i1)
    occupied.discard(i2)
    occupied.discard(j1)
    occupied.discard(j2)

    if not _cyclic_interval_empty(L, occupied, i1, j1):
        return False
    if not _cyclic_interval_empty(L, occupied, j2, i2):
        return False

    return True


def get_bigon_R2_pairs(word: List[Token]) -> List[Tuple[int, int]]:
    """Return all (outer, inner) pairs eligible for bigon R2-down.

    A pair is bigon-R2-eligible if and only if:
    - The outer chord nests the inner chord (outer_1 < inner_1 < inner_2
      < outer_2 in cyclic order);
    - Both chords have opposite signs at their two endpoints;
    - The two outer arcs (outer_1, inner_1) and (inner_2, outer_2) are
      empty of other chord endpoints.

    Interleaved pairs are NOT R2-eligible: R2-down is defined only on
    nested pairs. Deleting an interleaved pair would collapse a genuine
    linking structure (cf. the trefoil pattern (1,2,3,1,2,3), where every
    pair is interleaved yet no R2-down is available).
    """
    if not word:
        return []
    pairs = _pair_positions(word)
    cids = sorted(pairs.keys())
    L = len(word)

    all_occupied = set(range(L))

    result = []
    for a in cids:
        a1, sa1, a2, sa2 = pairs[a]
        if sa1 != -sa2:
            continue
        for b in cids:
            if b == a:
                continue
            b1, sb1, b2, sb2 = pairs[b]
            if sb1 != -sb2:
                continue
            # a must directly nest b (nested, not interleaved)
            if not (a1 < b1 < b2 < a2):
                continue

            outer_occupied = set(all_occupied)
            outer_occupied.discard(a1)
            outer_occupied.discard(a2)
            outer_occupied.discard(b1)
            outer_occupied.discard(b2)

            if not _cyclic_interval_empty(L, outer_occupied, a1, b1):
                continue
            if not _cyclic_interval_empty(L, outer_occupied, b2, a2):
                continue

            result.append((a, b))

    return result


def get_R1_down_positions(word: List[Token]) -> List[int]:
    """Return positions where R1-down is applicable.

    Position i means word[i] and word[(i+1) % L] are the adjacent pair
    with the same crossing ID and opposite signs.
    """
    if not word:
        return []
    L = len(word)
    result = []
    W2 = word + word
    for i in range(L):
        if W2[i][0] == W2[i + 1][0] and W2[i][1] == -W2[i + 1][1]:
            result.append(i % L)
    return result


def get_bigon_actions(word: List[Token]) -> List[MoveDescriptor]:
    """Return all valid bigon R1-down and bigon R2-down moves.

    Bigon R1-down: adjacent pair with same crossing ID and opposite signs.
    Bigon R2-down: directly nested pair with empty outer arcs and opposite signs.
    """
    actions: List[MoveDescriptor] = []

    for pos in get_R1_down_positions(word):
        actions.append(('R1_down', pos))

    for outer, inner in get_bigon_R2_pairs(word):
        actions.append(('R2_down', outer, inner))

    return actions


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
