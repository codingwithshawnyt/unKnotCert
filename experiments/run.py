"""
Main experiment runner for unKnotCert.
Builds graph, injects bridge, runs temperature-biased explorer,
computes persistence, bridge-only comparator, and crossing-number stats.
"""

import argparse
import json
import sys
from pathlib import Path
from collections import Counter
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.gauss import Token, get_valid_actions, apply_action, crossing_number
from core.canonical import canonical, canonical_str
from core.env import KnotEnv
from tda.graph import StateGraph
from tda.persistence import compute_persistence, plot_diagram, summary, squeeze_bound
from bridge.inject import inject_path


def parse_gauss_code(code_str: str) -> list:
    """Parse a Gauss code string like '-1 2 -3 4' into [(1,-1),(2,1),(3,-1),(4,1)].
    
    The paper format lists signed crossing labels. Each crossing appears twice
    with opposite signs. We read the sign as the over/under indicator from the
    Gauss code, and the absolute value as the crossing ID.
    """
    tokens = code_str.split()
    word = []
    for t in tokens:
        val = int(t)
        cid = abs(val)
        sign = 1 if val > 0 else -1
        word.append((cid, sign))
    return word


DIAGRAMS = {
    'Goeritz': [
        (1,1),(2,-1),(3,1),(4,-1),(5,-1),(6,1),(7,-1),(8,1),(9,-1),(10,-1),
        (11,1),(1,-1),(2,1),(3,-1),(4,1),(11,-1),(10,1),(7,1),(8,-1),
        (9,1),(6,-1),(5,1),
    ],
    'Culprit': parse_gauss_code(
        '-1 2 -3 4 -5 6 7 8 -9 10 -4 5 -6 3 -2 -7 -10 1 -8 9'
    ),
    'D28': parse_gauss_code(
        '1 -4 -3 6 5 -2 -7 8 4 -5 -9 10 2 -1 -11 7 12 -13 '
        '-6 3 14 -12 -10 9 13 -14 -8 11 15 -18 -17 20 19 -16 '
        '-21 17 22 -23 -20 21 24 -15 -25 26 16 -19 -27 28 18 '
        '-24 -26 27 23 -22 -28 25'
    ),
    'OchiaiII': parse_gauss_code(
        '-1 2 -3 -4 5 -6 -7 8 -9 10 -11 -12 13 -14 15 16 4 '
        '-17 6 18 -19 11 20 21 -22 -23 24 25 -26 27 -28 29 14 '
        '30 -31 -13 -25 32 -33 -34 -27 28 35 36 -37 22 38 -39 '
        '12 -40 -41 42 -16 3 -2 1 -21 -38 23 37 45 -35 34 26 '
        '-29 -15 -42 43 -18 9 -8 7 17 -5 -43 41 -44 31 -30 44 '
        '40 19 -10 -20 39 -24 -32 33 -36 -45'
    ),
    'Unknot': [],
}

HARDNESS = {
    'Goeritz':  {'cr': 11, 'm': 1, 'ref': 'Burton et al., Goeritz [6]'},
    'Culprit':  {'cr': 10, 'm': 1, 'ref': 'Burton et al., Kauffman-Lambropoulou [12]'},
    'D28':      {'cr': 28, 'm': 3, 'ref': 'Burton et al., Section 3'},
    'OchiaiII': {'cr': 45, 'm': 0, 'ref': 'Burton et al., Ochiai [15, Fig 2] (reduced: m>=2)'},
    'Unknot':   {'cr': 0,  'm': 0, 'ref': 'Trivial control'},
}


def load_path_words(path_file: str, variant: str = 'r1up_r2down') -> list:
    with open(path_file) as f:
        data = json.load(f)
    if 'paths' in data and variant in data['paths']:
        return [s['word'] for s in data['paths'][variant]['states']]
    return [step['word'] for step in data.get('path', [])]


def temperature_biased_explore(env: KnotEnv, graph: StateGraph, num_steps: int,
                                initial_word: list, seed: int = 42,
                                max_crossings: int = 30,
                                temperature: float = 0.3):
    """Temperature-biased random walk that prefers lower crossing numbers.
    
    At each step:
    - Compute crossing number delta for each valid action
    - Down moves (cn decrease) are always preferred
    - Up moves (cn increase) are accepted with Boltzmann probability:
      P(accept) = exp(-delta / temperature)
    - This allows occasional uphill moves to discover deeper valleys
    """
    rng = np.random.RandomState(seed)
    env.reset(initial_word)
    prev_id = graph.add_state(env.state)
    resets = 0
    max_cn_seen = crossing_number(env.state)

    for step in range(num_steps):
        actions = env.valid_actions()
        if not actions:
            env.reset(initial_word)
            prev_id = graph.add_state(env.state)
            resets += 1
            actions = env.valid_actions()
            if not actions:
                break

        cn = crossing_number(env.state)
        
        down_actions = []
        up_actions = []
        for idx, a in enumerate(actions):
            new_state, _ = apply_action(env.state, a, env._next_id)
            new_cn = crossing_number(new_state)
            delta = new_cn - cn
            if delta <= 0:
                down_actions.append((idx, delta))
            elif new_cn <= max_crossings:
                up_actions.append((idx, delta))

        chosen_idx = None
        
        if down_actions and (not up_actions or rng.random() < 0.7 + 0.3 * (1 - temperature)):
            weights = np.array([-d for _, d in down_actions], dtype=float)
            weights = np.maximum(weights, 0.1)
            weights = weights / weights.sum()
            choice = rng.choice(len(down_actions), p=weights)
            chosen_idx = down_actions[choice][0]
        elif up_actions:
            deltas = np.array([d for _, d in up_actions], dtype=float)
            probs = np.exp(-deltas / max(temperature, 0.01))
            probs = probs / probs.sum()
            if rng.random() < float(probs.max()):
                choice = rng.choice(len(up_actions), p=probs)
                chosen_idx = up_actions[choice][0]
            else:
                if down_actions:
                    chosen_idx = down_actions[rng.randint(len(down_actions))][0]
                else:
                    env.reset(initial_word)
                    prev_id = graph.add_state(env.state)
                    resets += 1
                    continue
        else:
            if down_actions:
                chosen_idx = down_actions[rng.randint(len(down_actions))][0]
            else:
                env.reset(initial_word)
                prev_id = graph.add_state(env.state)
                resets += 1
                continue

        obs, _, done, info = env.step(chosen_idx)
        curr_id = graph.add_state(env.state)
        curr_cn = crossing_number(env.state)
        max_cn_seen = max(max_cn_seen, curr_cn)
        if prev_id != curr_id:
            graph.add_edge(prev_id, curr_id)
        prev_id = curr_id

        if done:
            env.reset(initial_word)
            prev_id = graph.add_state(env.state)
            resets += 1

    return resets, max_cn_seen


def compute_cn_distribution(graph: StateGraph) -> dict:
    """Compute crossing number distribution in the graph."""
    _, _, filtration = graph.get_graph()
    if not filtration:
        return {}
    counter = Counter(filtration)
    return {str(k): v for k, v in sorted(counter.items())}


def compute_component_cn_distribution(graph: StateGraph, unknot_filtration: int = 0) -> dict:
    """Compute crossing number distribution in the component containing the unknot."""
    from collections import deque, defaultdict
    nodes, edges, filtration = graph.get_graph()
    n = len(filtration)
    if n == 0:
        return {}

    adj = defaultdict(set)
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    start = None
    for i, f in enumerate(filtration):
        if f == unknot_filtration:
            start = i
            break

    if start is None:
        return {}

    visited = {start}
    q = deque([start])
    while q:
        node = q.popleft()
        for nb in adj[node]:
            if nb not in visited:
                visited.add(nb)
                q.append(nb)

    component_filtration = [filtration[i] for i in visited]
    counter = Counter(component_filtration)
    return {str(k): v for k, v in sorted(counter.items())}


def main():
    parser = argparse.ArgumentParser(description='Run unKnotCert experiment')
    parser.add_argument('--diagram', type=str, default='all',
                        choices=list(DIAGRAMS.keys()) + ['all'])
    parser.add_argument('--inject-bridge', action='store_true',
                        help='Inject known monotonic path (bridge) into graph')
    parser.add_argument('--bridge-variant', type=str, default='r1up_r2down',
                        choices=['r1up_r2down'])
    parser.add_argument('--explore-steps', type=int, default=50000,
                        help='Total exploration steps (temperature-biased walk)')
    parser.add_argument('--seeds', type=str, default='0,1,2',
                        help='Comma-separated random seeds')
    parser.add_argument('--max-crossings', type=int, default=0,
                        help='Max crossings allowed (0=auto: initial_cn + m + 5)')
    parser.add_argument('--temperature', type=float, default=0.3,
                        help='Temperature for biased walk (lower=greedier)')
    parser.add_argument('--bridge-comparator', action='store_true',
                        help='Also compute bridge-only bound (no exploration)')
    args = parser.parse_args()

    seeds = [int(s.strip()) for s in args.seeds.split(',')]
    
    diagrams_to_run = list(DIAGRAMS.keys()) if args.diagram == 'all' else [args.diagram]
    all_results = {}

    for diagram_name in diagrams_to_run:
        initial_word = DIAGRAMS[diagram_name].copy()
        initial_cn = crossing_number(initial_word)
        hardness = HARDNESS.get(diagram_name, {})

        if args.max_crossings > 0:
            max_cn = args.max_crossings
        else:
            m_val = hardness.get('m', 0)
            max_cn = initial_cn + m_val + 5

        print(f"\n{'='*60}")
        print(f"Diagram: {diagram_name}")
        print(f"Initial crossing number: {initial_cn}")
        print(f"Known m(D): {hardness.get('m', '?')}")
        print(f"Max crossings: {max_cn}")
        print(f"Temperature: {args.temperature}")
        print(f"Seeds: {seeds}")
        print(f"{'='*60}")

        diagram_results = {
            "diagram": diagram_name,
            "initial_crossing_number": initial_cn,
            "known_hardness_m": hardness.get('m', None),
            "reference": hardness.get('ref', ''),
            "max_crossings": max_cn,
            "temperature": args.temperature,
            "seeds": seeds,
            "explore_steps": args.explore_steps,
        }

        # --- Bridge-only comparator ---
        if args.bridge_comparator or args.inject_bridge:
            bridge_path_file = Path(__file__).parent.parent / 'bridge' / 'paths.json'
            if diagram_name == 'Goeritz' and bridge_path_file.exists():
                bridge_graph = StateGraph()
                bridge_graph.add_state(initial_word)
                path_words = load_path_words(str(bridge_path_file),
                                             variant=args.bridge_variant)
                inject_path(bridge_graph, path_words)
                b_nodes, b_edges, b_filt = bridge_graph.get_graph()
                bridge_bound = squeeze_bound(b_nodes, b_edges, b_filt,
                                             unknot_filtration=0,
                                             initial_filtration=initial_cn)
                bridge_cn_dist = compute_cn_distribution(bridge_graph)
                diagram_results["bridge_only"] = {
                    "squeeze_bound": float(bridge_bound),
                    "num_nodes": bridge_graph.num_nodes(),
                    "num_edges": bridge_graph.num_edges(),
                    "cn_distribution": bridge_cn_dist,
                    "note": "Lower envelope from known monotonic path only"
                }
                print(f"  Bridge-only bound: {bridge_bound} "
                      f"({bridge_graph.num_nodes()} nodes, "
                      f"{bridge_graph.num_edges()} edges)")
            else:
                diagram_results["bridge_only"] = None
                if diagram_name != 'Unknot':
                    print(f"  No bridge path available for {diagram_name}")

        # --- Multi-seed exploration ---
        seed_bounds = []
        seed_data = []

        for seed in seeds:
            print(f"\n  Seed {seed}:")
            env = KnotEnv(max_crossings=max_cn + 10)
            graph = StateGraph()
            graph.add_state(initial_word)

            if args.inject_bridge and diagram_name == 'Goeritz':
                bridge_path_file = Path(__file__).parent.parent / 'bridge' / 'paths.json'
                if bridge_path_file.exists():
                    path_words = load_path_words(str(bridge_path_file),
                                                 variant=args.bridge_variant)
                    inject_path(graph, path_words)

            resets, max_cn_seen = temperature_biased_explore(
                env, graph, args.explore_steps, initial_word,
                seed=seed, max_crossings=max_cn,
                temperature=args.temperature
            )

            nodes, edges, filtration = graph.get_graph()
            bound = squeeze_bound(nodes, edges, filtration, unknot_filtration=0,
                               initial_filtration=initial_cn)
            diagram_pd = compute_persistence(nodes, edges, filtration)
            pd_summary = summary(diagram_pd)
            cn_dist = compute_cn_distribution(graph)
            comp_cn_dist = compute_component_cn_distribution(graph)

            seed_bounds.append(bound)

            seed_info = {
                "seed": seed,
                "squeeze_bound": float(bound),
                "resets": resets,
                "max_cn_seen": max_cn_seen,
                "graph_nodes": graph.num_nodes(),
                "graph_edges": graph.num_edges(),
                "persistence_summary": {
                    k: (float(v) if hasattr(v, '__float__') else v)
                    for k, v in pd_summary.items()
                },
                "persistence_pairs": [[float(b), float(d)] for b, d in diagram_pd],
                "cn_distribution_full": cn_dist,
                "cn_distribution_component": comp_cn_dist,
            }
            seed_data.append(seed_info)

            print(f"    Squeeze bound: {bound}")
            print(f"    Graph: {graph.num_nodes()} nodes, {graph.num_edges()} edges")
            print(f"    Resets: {resets}, max_cn_seen: {max_cn_seen}")
            print(f"    Features: {pd_summary.get('num_features', 0)}")

            output_dir = Path(__file__).parent.parent / 'outputs'
            output_dir.mkdir(exist_ok=True)

            pd_path = output_dir / f"{diagram_name}_seed{seed}_pd.png"
            plot_diagram(diagram_pd, str(pd_path),
                         title=f"{diagram_name} (seed={seed}) Persistence Diagram")

            graph.save(str(output_dir / f"{diagram_name}_seed{seed}_graph.pkl"))

        diagram_results["seeds"] = seed_data
        diagram_results["squeeze_bound_best"] = float(min(seed_bounds)) if seed_bounds else None
        diagram_results["squeeze_bound_mean"] = float(np.mean(seed_bounds)) if seed_bounds else None
        diagram_results["squeeze_bound_std"] = float(np.std(seed_bounds)) if seed_bounds else None

        print(f"\n  Summary for {diagram_name}:")
        print(f"    Best bound: {diagram_results['squeeze_bound_best']}")
        print(f"    Mean bound: {diagram_results['squeeze_bound_mean']:.1f} +/- {diagram_results['squeeze_bound_std']:.1f}")

        all_results[diagram_name] = diagram_results

    # --- Save combined results ---
    output_dir = Path(__file__).parent.parent / 'outputs'
    output_dir.mkdir(exist_ok=True)

    results_path = output_dir / 'full_experiment_results.json'
    with open(results_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\nSaved combined results to {results_path}")

    # --- Print comparison table ---
    print(f"\n{'='*80}")
    print(f"{'Diagram':<12} {'cr(D)':<7} {'m(D)':<6} {'Bridge':<8} "
          f"{'Best':<8} {'Mean':<10} {'Std':<8} {'Nodes':<8}")
    print(f"{'-'*80}")
    for name, res in all_results.items():
        cr = res['initial_crossing_number']
        m = res.get('known_hardness_m', '?')
        bridge = res.get('bridge_only', {})
        bridge_b = bridge.get('squeeze_bound', 'N/A') if bridge else 'N/A'
        best = res.get('squeeze_bound_best', 'N/A')
        mean = res.get('squeeze_bound_mean', 'N/A')
        std = res.get('squeeze_bound_std', 'N/A')
        nodes = res['seeds'][0]['graph_nodes'] if res.get('seeds') else 'N/A'
        if isinstance(mean, float):
            mean = f"{mean:.1f}"
        if isinstance(std, float):
            std = f"{std:.1f}"
        print(f"{name:<12} {cr:<7} {str(m):<6} {str(bridge_b):<8} "
              f"{str(best):<8} {str(mean):<10} {str(std):<8} {str(nodes):<8}")
    print(f"{'='*80}")


if __name__ == '__main__':
    main()
