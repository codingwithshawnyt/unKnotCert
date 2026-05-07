"""
Generate publication-quality figures for SoCG paper.
"""

import json
import os
import pickle
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from tda.persistence import compute_persistence


def make_two_panel_figure(graph_pkl: str, output_path: str, diagram_name: str):
    """
    Generate two-panel figure:
    - Left: Persistence diagram
    - Right: State graph visualization (histogram of filtration values)

    Also saves a JSON file with all data used in both panels.
    """
    from tda.graph import StateGraph
    from tda.persistence import summary as pd_summary

    graph = StateGraph()
    graph.load(graph_pkl)
    nodes, edges, filtration = graph.get_graph()

    diagram = compute_persistence(nodes, edges, filtration)

    # Prepare data for both panels
    births = [d[0] for d in diagram] if diagram else []
    deaths = [d[1] for d in diagram] if diagram else []
    all_vals = births + deaths if (births or deaths) else [0]
    min_val, max_val = min(all_vals), max(all_vals)

    hist_unique = []
    hist_counts = []
    if filtration:
        hist_unique, hist_counts = np.unique(filtration, return_counts=True)
        hist_unique = hist_unique.tolist()
        hist_counts = hist_counts.tolist()

    # --- Save JSON text-dump (source of truth) ---
    base = os.path.splitext(output_path)[0]
    json_path = base + '.json'
    json_data = {
        "title": f"{diagram_name}: Two-Panel Figure",
        "panel_left": {
            "title": f"{diagram_name}: Persistence Diagram",
            "x_label": "Birth (crossing number)",
            "y_label": "Death (crossing number)",
            "points": [[b, d] for b, d in diagram],
            "diagonal": True,
            "axis_range": [min_val, max_val]
        },
        "panel_right": {
            "title": f"{diagram_name}: State Distribution",
            "x_label": "Crossing Number",
            "y_label": "Number of States",
            "histogram": {
                "bin_values": hist_unique,
                "counts": hist_counts
            }
        },
        "metadata": {
            "num_nodes": len(nodes),
            "num_edges": len(edges),
            "diagram_name": diagram_name
        }
    }
    if diagram:
        json_data["metadata"]["persistence_summary"] = pd_summary(diagram)

    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2)

    # --- Render image ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    if diagram:
        ax1.scatter(births, deaths, alpha=0.7, s=50, edgecolors='k', linewidth=0.5)
        ax1.plot([min_val, max_val], [min_val, max_val], 'r--', alpha=0.5, label='diagonal')
        ax1.set_xlabel('Birth (crossing number)', fontsize=12)
        ax1.set_ylabel('Death (crossing number)', fontsize=12)
        ax1.set_title(f'{diagram_name}: Persistence Diagram', fontsize=14)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_aspect('equal')

    if filtration:
        ax2.bar(hist_unique, hist_counts, alpha=0.7, edgecolor='k')
        ax2.set_xlabel('Crossing Number', fontsize=12)
        ax2.set_ylabel('Number of States', fontsize=12)
        ax2.set_title(f'{diagram_name}: State Distribution', fontsize=14)
        ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved figure to {output_path}")
    print(f"Saved data  to {json_path}")


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
