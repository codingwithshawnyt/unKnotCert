"""Library of Gauss word diagrams for invariance and separation testing.

Contains:
- Multiple unknot diagrams at various crossing numbers
- Trefoil (3_1) diagrams
- Figure-eight (4_1) diagrams
- Other knot types for separation experiments

All Gauss codes follow the convention: each crossing appears twice with
opposite signs. The sign convention follows the standard: +1 for over,
-1 for under (or vice versa, as long as each pair has opposite signs).

Sources: standard knot tables, Dynnikov listings, and synthetic
unknot diagrams obtained by applying Reidemeister moves.
"""

from typing import Dict

# ===== Unknot diagrams at various crossing numbers =====

UNKNOT_VARIANTS = {
    'unknot_0': {
        'knot_type': 'unknot',
        'crossing_number': 0,
        'word': [],
        'source': 'Trivial unknot (empty word)',
    },
    'unknot_R1a': {
        'knot_type': 'unknot',
        'crossing_number': 1,
        'word': [(1, 1), (1, -1)],
        'source': 'R1 kink (type a)',
    },
    'unknot_R1b': {
        'knot_type': 'unknot',
        'crossing_number': 1,
        'word': [(1, -1), (1, 1)],
        'source': 'R1 kink (type b, opposite sign)',
    },
    'unknot_R2a': {
        'knot_type': 'unknot',
        'crossing_number': 2,
        'word': [(1, 1), (2, 1), (2, -1), (1, -1)],
        'source': 'R2 bigon (type a: nested pair)',
    },
    'unknot_R2b': {
        'knot_type': 'unknot',
        'crossing_number': 2,
        'word': [(1, -1), (2, -1), (2, 1), (1, 1)],
        'source': 'R2 bigon (type b, opposite signs)',
    },
    'unknot_cn3_a': {
        'knot_type': 'unknot',
        'crossing_number': 3,
        'word': [(1, 1), (2, 1), (3, 1), (3, -1), (2, -1), (1, -1)],
        'source': 'Unknot with 3 crossings (nested)',
    },
    'unknot_cn3_b': {
        'knot_type': 'unknot',
        'crossing_number': 3,
        'word': [(1, 1), (2, 1), (2, -1), (3, 1), (3, -1), (1, -1)],
        'source': 'Unknot with 3 crossings (two nested pairs + outer)',
    },
    'unknot_cn4': {
        'knot_type': 'unknot',
        'crossing_number': 4,
        'word': [(1, 1), (2, 1), (3, 1), (4, 1), (4, -1), (3, -1), (2, -1), (1, -1)],
        'source': 'Unknot with 4 crossings (deeply nested)',
    },
    'unknot_cn4_b': {
        'knot_type': 'unknot',
        'crossing_number': 4,
        'word': [(1, 1), (2, 1), (2, -1), (3, 1), (3, -1), (4, 1), (4, -1), (1, -1)],
        'source': 'Unknot with 4 crossings (three nested pairs)',
    },
    'unknot_cn5': {
        'knot_type': 'unknot',
        'crossing_number': 5,
        'word': [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (5, -1), (4, -1), (3, -1), (2, -1), (1, -1)],
        'source': 'Unknot with 5 crossings (deeply nested)',
    },
    'unknot_Hardy': {
        'knot_type': 'unknot',
        'crossing_number': 11,
        'word': [
            (1,1),(2,-1),(3,1),(4,-1),(5,-1),(6,1),(7,-1),(8,1),(9,-1),(10,-1),
            (11,1),(1,-1),(2,1),(3,-1),(4,1),(11,-1),(10,1),(7,1),(8,-1),
            (9,1),(6,-1),(5,1),
        ],
        'source': 'Goeritz hard unknot (Burton et al.)',
    },
    'unknot_Culprit': {
        'knot_type': 'unknot',
        'crossing_number': 10,
        'word': [(-1, -1), (2, 1), (-3, -1), (4, 1), (-5, -1), (6, 1), (7, 1), (8, 1), (-9, -1), (10, 1), (-4, -1), (5, 1), (-6, -1), (3, 1), (-2, -1), (-7, -1), (-10, -1), (1, 1), (-8, -1), (9, 1)],
        'source': 'Culprit hard unknot (Burton et al.)',
    },
}

# Fix the Culprit word - it uses negative IDs which aren't valid
# Re-parse using the same parser from run.py
def _parse_gauss(code_str: str) -> list:
    tokens = code_str.split()
    word = []
    for t in tokens:
        val = int(t)
        cid = abs(val)
        sign = 1 if val > 0 else -1
        word.append((cid, sign))
    return word

UNKNOT_VARIANTS['unknot_Culprit']['word'] = _parse_gauss(
    '-1 2 -3 4 -5 6 7 8 -9 10 -4 5 -6 3 -2 -7 -10 1 -8 9'
)


# ===== Trefoil (3_1) diagrams =====

KNOT_VARIANTS = {
    'trefoil_standard': {
        'knot_type': 'trefoil',
        'crossing_number': 3,
        'word': [(1, 1), (2, 1), (3, 1), (1, -1), (2, -1), (3, -1)],
        'source': 'Standard right-hand trefoil',
    },
    'trefoil_alt': {
        'knot_type': 'trefoil',
        'crossing_number': 3,
        'word': [(1, -1), (2, -1), (3, -1), (1, 1), (2, 1), (3, 1)],
        'source': 'Left-hand trefoil (mirror)',
    },
    'trefoil_cn4': {
        'knot_type': 'trefoil',
        'crossing_number': 4,
        'word': [(1, 1), (2, 1), (3, 1), (4, 1), (4, -1), (1, -1), (2, -1), (3, -1)],
        'source': 'Trefoil with R1 kink added (cn=4)',
    },
    'trefoil_cn5': {
        'knot_type': 'trefoil',
        'crossing_number': 5,
        'word': [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (5, -1), (4, -1), (1, -1), (2, -1), (3, -1)],
        'source': 'Trefoil with 2 R1 kinks added (cn=5)',
    },

    'figure_eight': {
        'knot_type': 'figure_eight',
        'crossing_number': 4,
        'word': [(1, 1), (2, -1), (3, 1), (4, -1), (2, 1), (3, -1), (1, -1), (4, 1)],
        'source': 'Standard figure-eight knot (4_1)',
    },
    'figure_eight_alt': {
        'knot_type': 'figure_eight',
        'crossing_number': 4,
        'word': [(1, -1), (2, 1), (3, -1), (4, 1), (2, -1), (3, 1), (1, 1), (4, -1)],
        'source': 'Figure-eight mirror',
    },
    'figure_eight_cn5': {
        'knot_type': 'figure_eight',
        'crossing_number': 5,
        'word': [(1, 1), (2, -1), (3, 1), (4, -1), (5, 1), (5, -1), (2, 1), (3, -1), (1, -1), (4, 1)],
        'source': 'Figure-eight with R1 kink (cn=5)',
    },

    'cinquefoil': {
        'knot_type': 'cinquefoil',
        'crossing_number': 5,
        'word': [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (1, -1), (2, -1), (3, -1), (4, -1), (5, -1)],
        'source': 'Cinquefoil / torus knot T(2,5) (5_1)',
    },

    'three_twist': {
        'knot_type': 'three_twist',
        'crossing_number': 5,
        'word': [(1, 1), (2, -1), (3, 1), (4, -1), (5, 1), (2, 1), (3, -1), (4, 1), (5, -1), (1, -1)],
        'source': 'Three-twist knot (5_2)',
    },
}


def get_all_diagrams() -> Dict:
    """Return all diagram variants grouped by knot type."""
    all_diagrams = {}
    for name, data in UNKNOT_VARIANTS.items():
        kt = data['knot_type']
        all_diagrams.setdefault(kt, {})[name] = data
    for name, data in KNOT_VARIANTS.items():
        kt = data['knot_type']
        all_diagrams.setdefault(kt, {})[name] = data
    return all_diagrams


def get_unknot_diagrams() -> Dict:
    return dict(UNKNOT_VARIANTS)


def get_knot_diagrams() -> Dict:
    return dict(KNOT_VARIANTS)
