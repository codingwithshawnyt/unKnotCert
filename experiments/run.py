"""
Main experiment runner for unKnotCert.
Builds graph, injects bridge, runs explorer, computes persistence.
"""

import argparse
import json
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.gauss import Token, get_valid_actions, apply_action, crossing_number
from core.canonical import canonical
from core.env import KnotEnv
from tda.graph import StateGraph
from tda.persistence import compute_persistence, plot_diagram, summary, squeeze_bound
from bridge.inject import inject_path


DIAGRAMS = {
    'Goeritz': [
        (1,1),(2,-1),(3,1),(4,-1),(5,-1),(6,1),(7,-1),(8,1),(9,-1),(10,-1),
        (11,1),(1,-1),(2,1),(3,-1),(4,1),(11,-1),(10,1),(7,1),(8,-1),
        (9,1),(6,-1),(5,1),
    ],
    'Trefoil': [
        (1, 1), (2, 1), (3, 1), (1, -1), (2, -1), (3, -1)
    ],
    'Unknot': []
}


def load_path_words(path_file: str, variant: str = 'no_r1up') -> list:
    with open(path_file) as f:
        data = json.load(f)
    if 'paths' in data:
        return [s['word'] for s in data['paths'][variant]['states']]
    return [step['word'] for step in data['path']]


def random_explore(env: KnotEnv, graph: StateGraph, num_steps: int,
                    initial_word: list, seed: int = 42,
                    max_crossings: int = 15):
    """Run random exploration, preferring down-moves and capping crossings."""
    np.random.seed(seed)
    env.reset(initial_word)
    prev_id = graph.add_state(env.state)

    for step in range(num_steps):
        actions = env.valid_actions()
        if not actions:
            env.reset(initial_word)
            prev_id = graph.add_state(env.state)
            actions = env.valid_actions()
            if not actions:
                break

        down = [a for a in actions if not a[0].endswith('_up')]
        cn = crossing_number(env.state)

        if down and (cn >= max_crossings or np.random.random() < 0.9):
            idx = np.random.randint(len(down))
            move = down[idx]
            action_idx = actions.index(move)
        elif cn < max_crossings:
            action_idx = np.random.randint(len(actions))
        else:
            action_idx = np.random.randint(len(down)) if down else 0

        obs, _, done, info = env.step(action_idx)
        curr_id = graph.add_state(env.state)
        if prev_id != curr_id:
            graph.add_edge(prev_id, curr_id)
        prev_id = curr_id

        if done:
            env.reset(initial_word)
            prev_id = graph.add_state(env.state)


def main():
    parser = argparse.ArgumentParser(description='Run unKnotCert experiment')
    parser.add_argument('--diagram', type=str, default='Goeritz',
                        choices=list(DIAGRAMS.keys()))
    parser.add_argument('--inject-bridge', action='store_true')
    parser.add_argument('--explore-steps', type=int, default=5000)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--max-crossings', type=int, default=15)
    args = parser.parse_args()

    initial_word = DIAGRAMS[args.diagram].copy()
    env = KnotEnv()
    graph = StateGraph()

    print(f"Initial diagram: {args.diagram}")
    print(f"Initial crossing number: {crossing_number(initial_word)}")

    graph.add_state(initial_word)

    if args.inject_bridge:
        bridge_path = Path(__file__).parent.parent / 'bridge' / 'paths.json'
        if bridge_path.exists():
            print(f"Injecting bridge from {bridge_path}")
            path_words = load_path_words(str(bridge_path), variant='no_r1up')
            inject_path(graph, path_words)
            print(f"Graph after bridge: {graph.num_nodes()} nodes, {graph.num_edges()} edges")
        else:
            print(f"Bridge path not found at {bridge_path}")
            print("Run: python bridge/generate_goeritz_path.py")

    if args.explore_steps > 0:
        print(f"Running exploration for {args.explore_steps} steps...")
        random_explore(env, graph, args.explore_steps, initial_word,
                        args.seed, args.max_crossings)
        print(f"Graph after exploration: {graph.num_nodes()} nodes, {graph.num_edges()} edges")

    nodes, edges, filtration = graph.get_graph()
    if graph.num_nodes() > 0:
        print("\nComputing persistence...")
        diagram = compute_persistence(nodes, edges, filtration)
        summ = summary(diagram)

        print("\nPersistence Summary:")
        for k, v in summ.items():
            print(f"  {k}: {v}")

        output_dir = Path(__file__).parent.parent / 'outputs'
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{args.diagram}_{args.seed}_bridge.png"
        plot_diagram(diagram, str(output_path),
                     title=f"{args.diagram} Persistence Diagram")
        print(f"\nSaved diagram to {output_path}")

        graph.save(str(output_dir / 'state_graph.pkl'))

    if diagram:
        bound = squeeze_bound(nodes, edges, filtration, unknot_filtration=0)
        print(f"\nSqueeze Lemma: Upper bound on minimax barrier = {bound}")
    else:
        print("No persistence pairs")
        return

    experiment_json_path = output_dir / f"{args.diagram}_{args.seed}_bridge.json"
    experiment_data = {
        "diagram": args.diagram,
        "seed": args.seed,
        "inject_bridge": args.inject_bridge,
        "explore_steps": args.explore_steps,
        "initial_crossing_number": crossing_number(initial_word),
        "graph": {
            "num_nodes": graph.num_nodes(),
            "num_edges": graph.num_edges()
        },
        "persistence_summary": {
            k: (float(v) if hasattr(v, '__float__') else v)
            for k, v in summ.items()
        },
        "squeeze_lemma_bound": float(bound),
        "persistence_pairs": [[float(b), float(d)] for b, d in diagram]
    }
        with open(experiment_json_path, 'w') as f:
            json.dump(experiment_data, f, indent=2)
        print(f"Saved experiment data to {experiment_json_path}")
    else:
        print("No nodes in graph - nothing to compute")


if __name__ == '__main__':
    main()
