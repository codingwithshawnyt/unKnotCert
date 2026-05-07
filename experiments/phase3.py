"""Phase 3: Persistence invariance and bottleneck distance experiments.

Three experiments:
1. INVARIANCE: Build Reidemeister graphs for multiple unknot diagrams,
   compute persistence diagrams, and measure pairwise bottleneck distances.
   If invariance holds, all unknot diagrams should produce identical
   (or bottleneck-close) persistence diagrams.

2. SEPARATION: Compare persistence diagrams of different knot types
   (unknot vs trefoil vs figure-eight) via bottleneck distance.
   If separation holds, different knots should have large distances.

3. COMPLEXITY: Correlate bottleneck distance to the trivial unknot
   with the minimax barrier M(D). If correlated, bottleneck distance
   is a quantitative measure of unknotting hardness.
"""

import sys
import json
import time
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.gauss import crossing_number, get_valid_actions, apply_action
from core.canonical import canonical
from core.env import KnotEnv
from tda.graph import StateGraph
from tda.persistence import compute_persistence, squeeze_bound, summary
from tda.bottleneck import bottleneck_distance, wasserstein_distance
from experiments.diagrams import UNKNOT_VARIANTS, KNOT_VARIANTS, get_all_diagrams
from experiments.run import DIAGRAMS, HARDNESS, temperature_biased_explore


def build_reidemeister_graph(initial_word, explore_steps=10000, seed=42,
                             temperature=0.3, max_crossings=None):
    """Build a Reidemeister graph via temperature-biased exploration."""
    cn = crossing_number(initial_word)
    if max_crossings is None:
        max_crossings = cn + 5

    env = KnotEnv(max_crossings=max_crossings + 10)
    graph = StateGraph()
    graph.add_state(initial_word)

    resets, max_cn = temperature_biased_explore(
        env, graph, explore_steps, initial_word,
        seed=seed, max_crossings=max_crossings,
        temperature=temperature
    )

    nodes, edges, filtration = graph.get_graph()
    bound = squeeze_bound(nodes, edges, filtration,
                          unknot_filtration=0,
                          initial_filtration=cn)

    return {
        'graph': graph,
        'nodes': nodes,
        'edges': edges,
        'filtration': filtration,
        'squeeze_bound': bound,
        'num_nodes': graph.num_nodes(),
        'num_edges': graph.num_edges(),
    }


def run_invariance_experiment(explore_steps=10000, seeds_per_diagram=3):
    """Experiment 1: Invariance within knot type.

    For each knot type, build graphs for all diagram variants and
    compare their persistence diagrams pairwise.
    """
    print("=" * 70)
    print("EXPERIMENT 1: PERSISTENCE INVARIANCE WITHIN KNOT TYPE")
    print("=" * 70)

    all_diagrams = get_all_diagrams()
    results = {}

    for knot_type, variants in all_diagrams.items():
        print("\n--- Knot type: {} ({} variants) ---".format(
            knot_type, len(variants)))

        diagram_data = {}

        for name, data in variants.items():
            word = data['word']
            cn = crossing_number(word)
            print("  Building graph: {} (cn={})...".format(name, cn), end=" ")

            # Build graph with multiple seeds, take the best
            best_pd = None
            best_bound = float('inf')
            best_graph_data = None

            for seed in range(seeds_per_diagram):
                t0 = time.time()
                gd = build_reidemeister_graph(
                    word, explore_steps=explore_steps, seed=seed,
                    temperature=0.5 if cn > 5 else 0.3,
                    max_crossings=max(cn + 3, cn * 2)
                )
                elapsed = time.time() - t0

                if gd['squeeze_bound'] < best_bound:
                    best_bound = gd['squeeze_bound']
                    best_graph_data = gd

            nodes, edges, filtration = best_graph_data['graph'].get_graph()
            pd = compute_persistence(nodes, edges, filtration)
            pd_summary = summary(pd)

            diagram_data[name] = {
                'crossing_number': cn,
                'persistence_diagram': pd,
                'persistence_summary': pd_summary,
                'squeeze_bound': best_bound,
                'num_nodes': best_graph_data['num_nodes'],
                'num_edges': best_graph_data['num_edges'],
            }

            print("nodes={}, bound={}, features={}".format(
                best_graph_data['num_nodes'], best_bound,
                pd_summary['num_features']))

        # Pairwise bottleneck distances within this knot type
        names = list(diagram_data.keys())
        pairwise = {}

        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                n1, n2 = names[i], names[j]
                pd1 = diagram_data[n1]['persistence_diagram']
                pd2 = diagram_data[n2]['persistence_diagram']

                if pd1 and pd2:
                    bd = bottleneck_distance(pd1, pd2)
                    wd = wasserstein_distance(pd1, pd2)
                else:
                    bd = float('inf')
                    wd = float('inf')

                pairwise[(n1, n2)] = {
                    'bottleneck': bd,
                    'wasserstein': wd,
                }

        results[knot_type] = {
            'variants': {k: {
                'crossing_number': v['crossing_number'],
                'persistence_summary': v['persistence_summary'],
                'squeeze_bound': v['squeeze_bound'],
                'num_nodes': v['num_nodes'],
                'persistence_diagram': v['persistence_diagram'],
            } for k, v in diagram_data.items()},
            'pairwise_distances': {
                '{}__{}'.format(k[0], k[1]): v
                for k, v in pairwise.items()
            },
        }

    # Print invariance summary
    print("\n" + "=" * 70)
    print("INVARIANCE SUMMARY")
    print("=" * 70)

    for knot_type, data in results.items():
        pairs = data['pairwise_distances']
        if pairs:
            bd_vals = [v['bottleneck'] for v in pairs.values()
                       if v['bottleneck'] != float('inf')]
            wd_vals = [v['wasserstein'] for v in pairs.values()
                       if v['wasserstein'] != float('inf')]
            print("\n{} ({} pairs):".format(knot_type, len(pairs)))
            if bd_vals:
                print("  Bottleneck: max={:.2f}, mean={:.2f}".format(
                    max(bd_vals), np.mean(bd_vals)))
                print("  Wasserstein: max={:.2f}, mean={:.2f}".format(
                    max(wd_vals), np.mean(wd_vals)))
            else:
                print("  No finite distances (some diagrams have empty PDs)")

    return results


def run_separation_experiment(explore_steps=10000, seeds=3):
    """Experiment 2: Separation between knot types.

    Pick one representative diagram per knot type and compute
    bottleneck distances between all pairs.
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 2: SEPARATION BETWEEN KNOT TYPES")
    print("=" * 70)

    representatives = {
        'unknot': 'unknot_R2a',
        'trefoil': 'trefoil_standard',
        'figure_eight': 'figure_eight',
        'cinquefoil': 'cinquefoil',
        'three_twist': 'three_twist',
        'unknot_hard': 'unknot_Hardy',
    }

    diagrams = {**UNKNOT_VARIANTS, **KNOT_VARIANTS}
    persistence_data = {}

    for knot_type, diag_name in representatives.items():
        word = diagrams[diag_name]['word']
        cn = crossing_number(word)
        print("  Building graph: {} ({}, cn={})...".format(
            diag_name, knot_type, cn))

        best_pd = None
        best_bound = float('inf')
        best_data = None

        for seed in range(seeds):
            gd = build_reidemeister_graph(
                word, explore_steps=explore_steps, seed=seed,
                temperature=0.5 if cn > 5 else 0.3,
                max_crossings=max(cn + 3, cn * 2)
            )
            if gd['squeeze_bound'] < best_bound:
                best_bound = gd['squeeze_bound']
                best_data = gd

        nodes, edges, filtration = best_data['graph'].get_graph()
        pd = compute_persistence(nodes, edges, filtration)
        pd_summary = summary(pd)

        persistence_data[knot_type] = {
            'diagram_name': diag_name,
            'crossing_number': cn,
            'persistence_diagram': pd,
            'persistence_summary': pd_summary,
            'squeeze_bound': best_bound,
            'num_nodes': best_data['num_nodes'],
        }
        print("    nodes={}, features={}, bound={}".format(
            best_data['num_nodes'], pd_summary['num_features'], best_bound))

    # Cross-type pairwise distances
    types = list(persistence_data.keys())
    cross_distances = {}

    print("\nPairwise bottleneck distances:")
    header = "{:<15}".format("")
    for t in types:
        header += " {:>12}".format(t[:12])
    print(header)
    print("-" * (15 + 13 * len(types)))

    for i, t1 in enumerate(types):
        row = "{:<15}".format(t1[:15])
        for j, t2 in enumerate(types):
            if i == j:
                row += " {:>12}".format("0.00")
            elif i > j:
                key = (t2, t1)
                if key in cross_distances:
                    row += " {:>12.2f}".format(cross_distances[key]['bottleneck'])
                else:
                    row += " {:>12}".format("--")
            else:
                pd1 = persistence_data[t1]['persistence_diagram']
                pd2 = persistence_data[t2]['persistence_diagram']

                if pd1 and pd2:
                    bd = bottleneck_distance(pd1, pd2)
                    wd = wasserstein_distance(pd1, pd2)
                else:
                    bd = float('inf')
                    wd = float('inf')

                cross_distances[(t1, t2)] = {
                    'bottleneck': bd,
                    'wasserstein': wd,
                }
                row += " {:>12.2f}".format(bd)

        print(row)

    return {
        'representatives': {k: {
            'diagram_name': v['diagram_name'],
            'crossing_number': v['crossing_number'],
            'persistence_summary': v['persistence_summary'],
            'squeeze_bound': v['squeeze_bound'],
            'persistence_diagram': v['persistence_diagram'],
            'num_nodes': v['num_nodes'],
        } for k, v in persistence_data.items()},
        'cross_distances': {
            '{}__{}'.format(k[0], k[1]): v
            for k, v in cross_distances.items()
        },
    }


def run_complexity_experiment(explore_steps=10000, seeds=3):
    """Experiment 3: Bottleneck distance as complexity measure.

    Compute bottleneck distance from each hard unknot diagram to
    the trivial unknot, and correlate with M(D).
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 3: BOTTLENECK DISTANCE AS COMPLEXITY MEASURE")
    print("=" * 70)

    # First build graph for trivial unknot
    unknot_graph_data = build_reidemeister_graph(
        [], explore_steps=0, seed=0
    )
    unknot_pd = [(0.0, 1.0)]  # Essential class: birth=0, death=inf -> 1

    # For each hard unknot diagram, build graph and compute PD
    hard_diagrams = {
        'Goeritz': DIAGRAMS['Goeritz'],
        'Culprit': DIAGRAMS['Culprit'],
        'D28': DIAGRAMS['D28'],
        'OchiaiII': DIAGRAMS['OchiaiII'],
    }

    known_barriers = {
        'Goeritz': 11, 'Culprit': 10, 'D28': 28, 'OchiaiII': 45
    }

    complexity_data = {}

    for name, word in hard_diagrams.items():
        cn = crossing_number(word)
        print("  {}: cn={}, M={}...".format(name, cn, known_barriers[name]))

        best_pd = None
        best_bound = float('inf')
        best_data = None

        for seed in range(seeds):
            gd = build_reidemeister_graph(
                word, explore_steps=explore_steps, seed=seed,
                temperature=0.5,
                max_crossings=cn + 5
            )
            if gd['squeeze_bound'] < best_bound:
                best_bound = gd['squeeze_bound']
                best_data = gd

        nodes, edges, filtration = best_data['graph'].get_graph()
        pd = compute_persistence(nodes, edges, filtration)
        pd_summary = summary(pd)

        # Distance to unknot PD
        if pd and unknot_pd:
            bd_to_unknot = bottleneck_distance(pd, unknot_pd)
            wd_to_unknot = wasserstein_distance(pd, unknot_pd)
        else:
            bd_to_unknot = float('inf')
            wd_to_unknot = float('inf')

        complexity_data[name] = {
            'crossing_number': cn,
            'exact_barrier': known_barriers[name],
            'persistence_summary': pd_summary,
            'squeeze_bound': best_bound,
            'bottleneck_to_unknot': bd_to_unknot,
            'wasserstein_to_unknot': wd_to_unknot,
            'persistence_diagram': pd,
            'num_nodes': best_data['num_nodes'],
        }

        print("    bound={}, bdist={:.2f}, wdist={:.2f}".format(
            best_bound, bd_to_unknot, wd_to_unknot))

    # Correlation analysis
    barriers = [complexity_data[n]['exact_barrier'] for n in complexity_data]
    bdists = [complexity_data[n]['bottleneck_to_unknot'] for n in complexity_data]
    cns = [complexity_data[n]['crossing_number'] for n in complexity_data]

    if len(barriers) > 2:
        corr_barrier = np.corrcoef(barriers, bdists)[0, 1]
        corr_cn = np.corrcoef(cns, bdists)[0, 1]
        print("\nCorrelation(M, bottleneck_dist) = {:.3f}".format(corr_barrier))
        print("Correlation(cr, bottleneck_dist) = {:.3f}".format(corr_cn))

    print("\n{:<12} {:>4} {:>8} {:>12} {:>12}".format(
        'Diagram', 'cr', 'M(D)', 'Bdist', 'Wdist'))
    print('-' * 50)
    for name, data in complexity_data.items():
        print("{:<12} {:>4} {:>8} {:>12.2f} {:>12.2f}".format(
            name, data['crossing_number'], data['exact_barrier'],
            data['bottleneck_to_unknot'], data['wasserstein_to_unknot']))

    return complexity_data


def make_phase3_figures(inv_results, sep_results, comp_results):
    """Generate Phase 3 figures."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    # Figure 1: Invariance heatmap for unknot variants
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    unknot_data = inv_results.get('unknot', {})
    variants = unknot_data.get('variants', {})
    names = sorted(variants.keys())

    if len(names) > 1:
        dist_matrix = np.zeros((len(names), len(names)))
        pairs = unknot_data.get('pairwise_distances', {})

        for i, n1 in enumerate(names):
            for j, n2 in enumerate(names):
                if i == j:
                    dist_matrix[i, j] = 0
                elif i < j:
                    key = '{}__{}'.format(n1, n2)
                    dist_matrix[i, j] = pairs.get(key, {}).get('bottleneck', 0)
                    dist_matrix[j, i] = dist_matrix[i, j]

        im = ax.imshow(dist_matrix, cmap='viridis')
        ax.set_xticks(range(len(names)))
        ax.set_yticks(range(len(names)))
        short_names = [n.replace('unknot_', 'U_')[:10] for n in names]
        ax.set_xticklabels(short_names, rotation=45, ha='right', fontsize=7)
        ax.set_yticklabels(short_names, fontsize=7)
        plt.colorbar(im, ax=ax, label='Bottleneck distance')
        ax.set_title('Bottleneck Distances Between Unknot Diagrams\n(Invariance Test)')

    fig.tight_layout()
    for fmt in ['pdf', 'png']:
        fig.savefig('outputs/phase3_invariance_heatmap.{}'.format(fmt), dpi=150)
    plt.close(fig)
    print('Saved phase3_invariance_heatmap')

    # Figure 2: Cross-type separation heatmap
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    reps = sep_results.get('representatives', {})
    types = sorted(reps.keys())

    if len(types) > 1:
        cross = sep_results.get('cross_distances', {})
        dist_matrix = np.zeros((len(types), len(types)))

        for i, t1 in enumerate(types):
            for j, t2 in enumerate(types):
                if i == j:
                    dist_matrix[i, j] = 0
                else:
                    key1 = '{}__{}'.format(t1, t2)
                    key2 = '{}__{}'.format(t2, t1)
                    d = cross.get(key1, cross.get(key2, {}))
                    dist_matrix[i, j] = d.get('bottleneck', 0)

        im = ax.imshow(dist_matrix, cmap='magma')
        ax.set_xticks(range(len(types)))
        ax.set_yticks(range(len(types)))
        ax.set_xticklabels([t[:8] for t in types], rotation=45, ha='right')
        ax.set_yticklabels([t[:8] for t in types])
        plt.colorbar(im, ax=ax, label='Bottleneck distance')
        ax.set_title('Bottleneck Distances Between Knot Types\n(Separation Test)')

    fig.tight_layout()
    for fmt in ['pdf', 'png']:
        fig.savefig('outputs/phase3_separation_heatmap.{}'.format(fmt), dpi=150)
    plt.close(fig)
    print('Saved phase3_separation_heatmap')

    # Figure 3: Complexity correlation scatter
    fig, ax = plt.subplots(1, 1, figsize=(7, 5))
    barriers = [comp_results[n]['exact_barrier'] for n in comp_results]
    bdists = [comp_results[n]['bottleneck_to_unknot'] for n in comp_results]
    names_comp = list(comp_results.keys())

    ax.scatter(barriers, bdists, s=100, c='#0d6efd', edgecolors='k',
               linewidth=1, zorder=5)
    for i, name in enumerate(names_comp):
        ax.annotate(name, (barriers[i], bdists[i]),
                   textcoords='offset points', xytext=(8, 5), fontsize=9)

    if len(barriers) > 2:
        corr = np.corrcoef(barriers, bdists)[0, 1]
        ax.set_title('Bottleneck Distance to Unknot vs Minimax Barrier\nr = {:.3f}'.format(corr))
    else:
        ax.set_title('Bottleneck Distance to Unknot vs Minimax Barrier')

    ax.set_xlabel('Exact Barrier M(D)')
    ax.set_ylabel('Bottleneck distance to unknot PD')
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    for fmt in ['pdf', 'png']:
        fig.savefig('outputs/phase3_complexity_scatter.{}'.format(fmt), dpi=150)
    plt.close(fig)
    print('Saved phase3_complexity_scatter')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Phase 3 experiments')
    parser.add_argument('--explore-steps', type=int, default=5000,
                        help='Steps per graph exploration')
    parser.add_argument('--seeds', type=int, default=2,
                        help='Seeds per diagram')
    parser.add_argument('--experiment', type=str, default='all',
                        choices=['invariance', 'separation', 'complexity', 'all'])
    args = parser.parse_args()

    all_results = {}

    if args.experiment in ('invariance', 'all'):
        inv = run_invariance_experiment(
            explore_steps=args.explore_steps,
            seeds_per_diagram=args.seeds
        )
        # Convert persistence diagrams for JSON serialization
        inv_serializable = {}
        for kt, data in inv.items():
            inv_serializable[kt] = {
                'variants': {k: {kk: vv for kk, vv in v.items()
                                  if kk != 'persistence_diagram'}
                             for k, v in data['variants'].items()},
                'pairwise_distances': data['pairwise_distances'],
            }
            # Add PD as serializable lists
            for k, v in data['variants'].items():
                inv_serializable[kt]['variants'][k]['persistence_diagram'] = [
                    [float(b), float(d)] for b, d in v['persistence_diagram']
                ]
        all_results['invariance'] = inv_serializable

    if args.experiment in ('separation', 'all'):
        sep = run_separation_experiment(
            explore_steps=args.explore_steps,
            seeds=args.seeds
        )
        sep_serializable = {}
        for k, v in sep['representatives'].items():
            sep_serializable[k] = {kk: vv for kk, vv in v.items()
                                    if kk != 'persistence_diagram'}
            sep_serializable[k]['persistence_diagram'] = [
                [float(b), float(d)] for b, d in v['persistence_diagram']
            ]
        all_results['separation'] = {
            'representatives': sep_serializable,
            'cross_distances': sep['cross_distances'],
        }

    if args.experiment in ('complexity', 'all'):
        comp = run_complexity_experiment(
            explore_steps=args.explore_steps,
            seeds=args.seeds
        )
        comp_serializable = {}
        for k, v in comp.items():
            comp_serializable[k] = {kk: vv for kk, vv in v.items()
                                     if kk != 'persistence_diagram'}
            comp_serializable[k]['persistence_diagram'] = [
                [float(b), float(d)] for b, d in v['persistence_diagram']
            ]
        all_results['complexity'] = comp_serializable

    # Save results
    with open('outputs/phase3_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    print('\nSaved to outputs/phase3_results.json')

    # Generate figures
    if args.experiment == 'all':
        make_phase3_figures(
            inv if args.experiment == 'all' else {},
            sep if args.experiment == 'all' else {},
            comp if args.experiment == 'all' else {},
        )
