"""
Bridge injection - populates a StateGraph with known unknotting paths.
"""

from typing import List, List as ListType
from core.gauss import Token


def inject_path(graph, path_words: ListType[ListType[Token]]):
    """
    Inject a known unknotting path into the state graph.

    For each consecutive pair (w_i, w_{i+1}), add both states
    (they get canonicalized) and add an edge between them.
    """
    if not path_words or len(path_words) < 2:
        return

    prev_id = None
    for word in path_words:
        curr_id = graph.add_state(word)
        if prev_id is not None and prev_id != curr_id:
            graph.add_edge(prev_id, curr_id)
        prev_id = curr_id
