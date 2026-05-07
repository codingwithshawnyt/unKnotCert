"""
Phase 2 figures: Exact minimax barriers via bounded BFS.

Produces:
1. barrier_comparison.pdf/.png — Phase 1 upper bounds vs Phase 2 exact barriers
2. bfs_performance.pdf/.png — BFS state-space size and time scaling
3. cn_trace.pdf/.png — CN traces along proven unknotting paths
"""

import sys
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.gauss import crossing_number, apply_action
from experiments.run import DIAGRAMS


def load_results():
    with open('outputs/combined_barrier_table.json') as f:
        return json.load(f)


def figure_barrier_comparison(table):
    fig, ax = plt.subplots(1, 1, figsize=(8, 5))

    names = [r['diagram'] for r in table['rows'] if r['cr'] > 0]
    crs = [r['cr'] for r in table['rows'] if r['cr'] > 0]
    explore_ubs = [r['exploration_ub'] for r in table['rows'] if r['cr'] > 0]
    bridge_ubs = [r['bridge_ub'] if r['bridge_ub'] is not None else r['cr'] for r in table['rows'] if r['cr'] > 0]
    exact = [r['exact_M'] for r in table['rows'] if r['cr'] > 0]
    m_s2 = [r['m_S2'] for r in table['rows'] if r['cr'] > 0]

    x = np.arange(len(names))
    width = 0.18

    bars1 = ax.bar(x - 2*width, explore_ubs, width, label='Phase 1: Exploration UB',
                   color='#6c757d', alpha=0.8)
    bars2 = ax.bar(x - width, bridge_ubs, width, label='Phase 1: Bridge UB',
                   color='#0d6efd', alpha=0.8)
    bars3 = ax.bar(x, exact, width, label='Phase 2: Exact M(D)',
                   color='#198754', alpha=0.9, edgecolor='black', linewidth=1.5)
    bars4 = ax.bar(x + width, m_s2, width, label='Known m (S²)',
                   color='#ffc107', alpha=0.8)
    ax.plot(x + 2*width, crs, 'D', color='#dc3545', markersize=8, label='cr(D)')

    for bar_group in [bars1, bars2, bars3, bars4]:
        for bar, val in zip(bar_group, [explore_ubs, bridge_ubs, exact, m_s2][bar_group == bars1]):
            pass

    ax.set_xlabel('Diagram')
    ax.set_ylabel('Crossing Number')
    ax.set_title('Exact Minimax Barriers for Hard Unknot Diagrams\n(Plane move set: R1+R2+R3)')
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.legend(loc='upper left', fontsize=8)
    ax.set_ylim(0, 52)

    for i, (e, b, m, s) in enumerate(zip(exact, bridge_ubs, m_s2, crs)):
        if e < b:
            ax.annotate('improved', xy=(i, e), xytext=(i + 0.3, e + 1),
                       fontsize=7, color='#198754', fontweight='bold')

    fig.tight_layout()
    for fmt in ['pdf', 'png']:
        fig.savefig('outputs/phase2_barrier_comparison.{}'.format(fmt), dpi=150)
    plt.close(fig)
    print('Saved phase2_barrier_comparison')


def figure_bfs_performance(table):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    rows = [r for r in table['rows'] if r['cr'] > 0]
    names = [r['diagram'] for r in rows]
    crs = [r['cr'] for r in rows]
    states = [r['bfs_states'] for r in rows]
    times = [r['bfs_time_s'] for r in rows]

    ax1.bar(names, states, color='#0d6efd', alpha=0.8)
    ax1.set_xlabel('Diagram')
    ax1.set_ylabel('States Visited')
    ax1.set_title('BFS State-Space Size\n(at ceiling N = cr(D))')
    ax1.set_yscale('log')
    for i, (n, s) in enumerate(zip(names, states)):
        ax1.text(i, s * 1.3, str(s), ha='center', fontsize=8)

    ax2.bar(names, times, color='#198754', alpha=0.8)
    ax2.set_xlabel('Diagram')
    ax2.set_ylabel('Wall Time (s)')
    ax2.set_title('BFS Runtime\n(at ceiling N = cr(D))')
    ax2.set_yscale('log')
    for i, (n, t) in enumerate(zip(names, times)):
        ax2.text(i, t * 1.5, '{:.3f}'.format(t), ha='center', fontsize=8)

    fig.suptitle('Phase 2: Bounded BFS Performance', fontsize=12, fontweight='bold')
    fig.tight_layout()
    for fmt in ['pdf', 'png']:
        fig.savefig('outputs/phase2_bfs_performance.{}'.format(fmt), dpi=150)
    plt.close(fig)
    print('Saved phase2_bfs_performance')


def figure_cn_traces():
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    axes = axes.flatten()

    paths_info = [
        ('bridge/paths.json', 'Goeritz'),
        ('bridge/culprit_paths.json', 'Culprit'),
        ('bridge/d28_paths.json', 'D28'),
        ('bridge/ochiaiii_paths.json', 'OchiaiII'),
    ]

    for ax, (path_file, name) in zip(axes, paths_info):
        try:
            with open(path_file) as f:
                pdata = json.load(f)
        except FileNotFoundError:
            ax.text(0.5, 0.5, 'Path not found', transform=ax.transAxes, ha='center')
            ax.set_title(name)
            continue

        word = list(DIAGRAMS[name])
        nid = max(c for c, _ in word) + 1
        cn_trace = [crossing_number(word)]

        path_key = None
        for key in pdata.get('paths', {}):
            path_key = key
            break

        if path_key is None:
            ax.text(0.5, 0.5, 'No path data', transform=ax.transAxes, ha='center')
            ax.set_title(name)
            continue

        moves = pdata['paths'][path_key]['moves']
        for mv in moves:
            word, nid = apply_action(word, tuple(mv), nid)
            cn_trace.append(crossing_number(word))

        ax.plot(range(len(cn_trace)), cn_trace, 'o-', color='#0d6efd',
                markersize=4, linewidth=1.5)
        ax.axhline(y=cn_trace[0], color='#dc3545', linestyle='--', alpha=0.5, label='cr(D)')
        ax.axhline(y=max(cn_trace), color='#ffc107', linestyle=':', alpha=0.5, label='max CN')
        ax.set_xlabel('Move step')
        ax.set_ylabel('Crossing Number')
        barrier = pdata['paths'][path_key]['barrier']
        ax.set_title('{}: M={}, max_cn={}'.format(name, barrier, max(cn_trace)))
        ax.legend(fontsize=7)

    fig.suptitle('CN Traces Along Proven Unknotting Paths', fontsize=12, fontweight='bold')
    fig.tight_layout()
    for fmt in ['pdf', 'png']:
        fig.savefig('outputs/phase2_cn_traces.{}'.format(fmt), dpi=150)
    plt.close(fig)
    print('Saved phase2_cn_traces')


if __name__ == '__main__':
    table = load_results()

    figure_barrier_comparison(table)
    figure_bfs_performance(table)
    figure_cn_traces()

    print('\nAll Phase 2 figures saved to outputs/')
