"""
Main experiment runner for unKnotCert.
Builds graph, injects bridge, runs explorer, computes persistence.
"""

import argparse
import json
import sys
from pathlib import Path
import numpy as np

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.gauss import Token, get_valid_actions, apply_action, crossing_number
from core.canonical import canonical
from core.env import KnotEnv
from tda.graph import StateGraph
from tda.persistence import compute_persistence, plot_diagram, summary
from bridge.inject import inject_path


# Built-in diagrams
DIAGRAMS = {
    'Goeritz': [
        (1, 1), (2, 1), (3, 1), (1, -1), (4, 1), (5, 1), (6, 1), (4, -1),
        (7, 1), (8, 1), (9, 1), (7, -1), (10, 1), (11, 1), (5, -1),
        (10, -1), (6, -1), (11, -1), (2, -1), (9, -1), (8, -1), (3, -1)
    ],
    'Trefoil': [
        (1, 1), (2, 1), (3, 1), (1, -1), (2, -1), (3, -1)
    ],
    'Unknot': []
}


def load_path_words(path_file: str) -> list:
    """Load path words from JSON file."""
    with open(path_file) as f:
        data = json.load(f)
    return [step['word'] for step in data['path']]


def random_explore(env: KnotEnv, graph: StateGraph, num_steps: int, seed: int = 42):
    """Run random exploration to populate the graph."""
    np.random.seed(seed)
    env.reset(DIAGRAMS['Goeritz'].copy())
    graph.add_state(env.state)

    for step in range(num_steps):
        actions = env.valid_actions()
        if not actions:
            break
        idx = np.random.randint(len(actions))
        obs, _, done, info = env.step(idx)
        graph.add_state(env.state)

        # Add edge from previous state
        prev_canon = canonical(obs['state'])
        curr_canon = canonical(env.state)
        if prev_canon in graph._node_index and curr_canon in graph._node_index:
            graph.add_edge(graph._node_index[prev_canon], graph._node_index[curr_canon])

        if done:
            break


def main():
    parser = argparse.ArgumentParser(description='Run unKnotCert experiment')
    parser.add_argument('--diagram', type=str, default='Goeritz',
                        choices=list(DIAGRAMS.keys()),
                        help='Diagram to analyze')
    parser.add_argument('--inject-bridge', action='store_true',
                        help='Inject known unknotting path')
    parser.add_argument('--explore-steps', type=int, default=5000,
                        help='Number of random exploration steps')
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed')
    args = parser.parse_args()

    # Initialize
    initial_word = DIAGRAMS[args.diagram].copy()
    env = KnotEnv()
    graph = StateGraph()

    print(f"Initial diagram: {args.diagram}")
    print(f"Initial crossing number: {crossing_number(initial_word)}")

    # Add initial state
    graph.add_state(initial_word)

    # Inject bridge if requested
    if args.inject_bridge:
        bridge_path = Path(__file__).parent.parent / 'bridge' / 'paths.json'
        if bridge_path.exists():
            print(f"Injecting bridge from {bridge_path}")
            path_words = load_path_words(str(bridge_path))
            inject_path(graph, path_words)
            print(f"Graph after bridge injection: {graph.num_nodes()} nodes, {graph.num_edges()} edges")
        else:
            print(f"Bridge path not found at {bridge_path}")
            print("Run: python bridge/generate_goeritz_path.py")

    # Run explorer
    if args.explore_steps > 0:
        print(f"Running random exploration for {args.explore_steps} steps...")
        random_explore(env, graph, args.explore_steps, args.seed)
        print(f"Graph after exploration: {graph.num_nodes()} nodes, {graph.num_edges()} edges")

    # Compute persistence
    nodes, edges, filtration = graph.get_graph()
    if graph.num_nodes() > 0:
        print("\nComputing persistence...")
        diagram = compute_persistence(nodes, edges, filtration)
        summ = summary(diagram)

        print("\nPersistence Summary:")
        for k, v in summ.items():
            print(f"  {k}: {v}")

        # Plot
        output_dir = Path(__file__).parent.parent / 'outputs'
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{args.diagram}_{args.seed}_bridge.png"
        plot_diagram(diagram, str(output_path),
                     title=f"{args.diagram} Persistence Diagram")
        print(f"\nSaved diagram to {output_path}")

        # Save graph
        graph.save(str(output_dir / 'state_graph.pkl'))
        print(f"Saved graph to {output_dir / 'state_graph.pkl'}")

        # Print Squeeze Lemma result
        if diagram:
            max_death = max(d for _, d in diagram)
            print(f"\nSqueeze Lemma: Upper bound on minimax barrier = {max_death}")
    else:
        print("No nodes in graph - nothing to compute")


if __name__ == '__main__':
    main()
