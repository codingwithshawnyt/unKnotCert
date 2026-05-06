"""
State-transition graph for TDA analysis of knot unknotting.
"""

import pickle
from typing import List, Tuple, Dict, Optional, Set
from pathlib import Path

from core.canonical import canonical, canonical_str
from core.gauss import crossing_number


class StateGraph:
    """Graph representing states and transitions of knot diagrams."""

    def __init__(self):
        self._node_index: Dict[tuple, int] = {}  # canonical tuple -> node id
        self._nodes: List[str] = []  # canonical strings
        self._filtration: List[int] = []  # crossing numbers
        self._edges: Set[Tuple[int, int]] = set()

    def add_state(self, word: list) -> int:
        """Add a state to the graph. Returns node id."""
        canon = canonical(word)
        if canon in self._node_index:
            return self._node_index[canon]

        node_id = len(self._nodes)
        self._node_index[canon] = node_id
        self._nodes.append(str(canon))
        self._filtration.append(crossing_number(word))
        return node_id

    def add_edge(self, id_from: int, id_to: int, bidirectional: bool = True):
        """Add an edge between two nodes."""
        if id_from == id_to:
            return
        edge = (min(id_from, id_to), max(id_from, id_to))
        self._edges.add(edge)
        if bidirectional and False:
            pass

    def get_graph(self) -> Tuple[List[str], List[Tuple[int, int]], List[int]]:
        """Return (nodes, edges, filtration_values)."""
        return self._nodes, list(self._edges), self._filtration

    def num_nodes(self) -> int:
        return len(self._nodes)

    def num_edges(self) -> int:
        return len(self._edges)

    def save(self, path: str):
        """Save graph to pickle file."""
        data = {
            'node_index': self._node_index,
            'nodes': self._nodes,
            'filtration': self._filtration,
            'edges': self._edges
        }
        with open(path, 'wb') as f:
            pickle.dump(data, f)

    def load(self, path: str):
        """Load graph from pickle file."""
        with open(path, 'rb') as f:
            data = pickle.load(f)
        self._node_index = data['node_index']
        self._nodes = data['nodes']
        self._filtration = data['filtration']
        self._edges = data['edges']
