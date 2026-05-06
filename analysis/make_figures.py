"""
Generate publication-quality figures for SoCG paper.
"""

import json
import pickle
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

from tda.persistence import compute_persistence


def make_two_panel_figure(graph_pkl: str, output_path: str, diagram_name: str):
    """
    Generate two-panel figure:
    - Left: Persistence diagram
    - Right: State graph visualization (if networkx available)
    """
    # Load graph
    from tda.graph import StateGraph
    graph = StateGraph()
    graph.load(graph_pkl)
    nodes, edges, filtration = graph.get_graph()

    # Compute persistence
    diagram = compute_persistence(nodes, edges, filtration)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Panel 1: Persistence diagram
    if diagram:
        births = [d[0] for d in diagram]
        deaths = [d[1] for d in diagram]
        ax1.scatter(births, deaths, alpha=0.7, s=50, edgecolors='k', linewidth=0.5)

        all_vals = births + deaths
        min_val, max_val = min(all_vals), max(all_vals)
        ax1.plot([min_val, max_val], [min_val, max_val], 'r--', alpha=0.5, label='diagonal')

        ax1.set_xlabel('Birth (crossing number)', fontsize=12)
        ax1.set_ylabel('Death (crossing number)', fontsize=12)
        ax1.set_title(f'{diagram_name}: Persistence Diagram', fontsize=14)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_aspect('equal')

    # Panel 2: Graph visualization (simplified - histogram of filtration values)
    if filtration:
        unique_f, counts = np.unique(filtration, return_counts=True)
        ax2.bar(unique_f, counts, alpha=0.7, edgecolor='k')
        ax2.set_xlabel('Crossing Number', fontsize=12)
        ax2.set_ylabel('Number of States', fontsize=12)
        ax2.set_title(f'{diagram_name}: State Distribution', fontsize=14)
        ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved figure to {output_path}")


if __name__ == '__main__':
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))

    output_dir = Path(__file__).parent.parent / 'outputs'
    graph_path = output_dir / 'state_graph.pkl'

    if graph_path.exists():
        make_two_panel_figure(
            str(graph_path),
            str(output_dir / 'publication_figure.png'),
            'Goeritz'
        )
    else:
        print(f"Graph file not found at {graph_path}")
        print("Run experiments/run.py first")
