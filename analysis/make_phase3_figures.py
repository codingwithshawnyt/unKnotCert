"""Phase 3 figures: persistence invariance, separation, and complexity."""

import sys
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def make_all_figures():
    with open('outputs/phase3_results.json') as f:
        results = json.load(f)

    # Figure 1: Convergence - Squeeze bound vs exploration steps
    fig, ax = plt.subplots(1, 1, figsize=(8, 5))
    
    convergence = results['experiments']['convergence']
    for name, data in convergence.items():
        steps = [d['steps'] for d in data]
        bounds = [d['squeeze_bound'] for d in data]
        ax.plot(steps, bounds, 'o-', label=name, linewidth=2, markersize=6)
        # Mark exact barrier
        exact = {'Goeritz': 11, 'D28': 28}[name]
        ax.axhline(y=exact, color='gray', linestyle='--', alpha=0.5)
    
    ax.set_xlabel('Exploration Steps')
    ax.set_ylabel('Squeeze Lemma Bound')
    ax.set_title('Convergence of Squeeze Lemma Bound\nwith Increasing Exploration')
    ax.set_xscale('log')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    fig.tight_layout()
    for fmt in ['pdf', 'png']:
        fig.savefig('outputs/phase3_convergence.{}'.format(fmt), dpi=150)
    plt.close(fig)
    print('Saved phase3_convergence')

    # Figure 2: Separation heatmap
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    
    sep = results['experiments']['separation']
    pairs = sep['pairwise_distances']
    
    all_names = set()
    for key in pairs:
        n1, n2 = key.split('__')
        all_names.add(n1)
        all_names.add(n2)
    names = sorted(all_names)
    
    dist_matrix = np.zeros((len(names), len(names)))
    for key, val in pairs.items():
        n1, n2 = key.split('__')
        i, j = names.index(n1), names.index(n2)
        dist_matrix[i, j] = val['bottleneck']
        dist_matrix[j, i] = val['bottleneck']
    
    im = ax.imshow(dist_matrix, cmap='viridis')
    
    # Annotate same-knot pairs
    for i in range(len(names)):
        for j in range(len(names)):
            kt_i = {'unknot_simple': 'unknot', 'unknot_hard': 'unknot',
                    'trefoil': 'trefoil', 'trefoil_R1': 'trefoil',
                    'figure_eight': 'fig8', 'cinquefoil': '5_1'}.get(names[i], '?')
            kt_j = {'unknot_simple': 'unknot', 'unknot_hard': 'unknot',
                    'trefoil': 'trefoil', 'trefoil_R1': 'trefoil',
                    'figure_eight': 'fig8', 'cinquefoil': '5_1'}.get(names[j], '?')
            
            if i != j:
                color = 'white' if dist_matrix[i, j] > 3 else 'black'
                ax.text(j, i, '{:.0f}'.format(dist_matrix[i, j]),
                       ha='center', va='center', fontsize=8, color=color)
    
    ax.set_xticks(range(len(names)))
    ax.set_yticks(range(len(names)))
    short = {'unknot_simple': 'U_simple', 'unknot_hard': 'U_hard',
             'trefoil': 'Tref', 'trefoil_R1': 'Tref+R1',
             'figure_eight': 'Fig8', 'cinquefoil': '5_1'}
    ax.set_xticklabels([short.get(n, n[:8]) for n in names], rotation=45, ha='right')
    ax.set_yticklabels([short.get(n, n[:8]) for n in names])
    plt.colorbar(im, ax=ax, label='Bottleneck distance')
    ax.set_title('Bottleneck Distances Between Knot Diagrams\n(Separation Test)')
    
    fig.tight_layout()
    for fmt in ['pdf', 'png']:
        fig.savefig('outputs/phase3_separation.{}'.format(fmt), dpi=150)
    plt.close(fig)
    print('Saved phase3_separation')

    # Figure 3: Complexity scatter
    fig, ax = plt.subplots(1, 1, figsize=(7, 5))
    
    comp = results['experiments']['complexity']['data']
    diagram_names = [n for n in comp if n != 'Unknot']
    barriers = [comp[n]['M'] for n in diagram_names]
    bdists = [comp[n]['bottleneck_to_unknot'] for n in diagram_names]
    squeeze = [comp[n]['squeeze_bound'] for n in diagram_names]
    
    ax.scatter(barriers, bdists, s=100, c='#0d6efd', edgecolors='k',
               linewidth=1, zorder=5, label='BD to unknot')
    ax.scatter(barriers, squeeze, s=80, c='#ffc107', edgecolors='k',
               linewidth=1, zorder=4, marker='s', label='Squeeze bound')
    ax.plot([0, 50], [0, 50], 'k--', alpha=0.3, label='y = x')
    
    for i, name in enumerate(diagram_names):
        ax.annotate(name, (barriers[i], bdists[i]),
                   textcoords='offset points', xytext=(8, 5), fontsize=9)
    
    corr = results['experiments']['complexity']['correlation_M_bdist']
    ax.set_title('Bottleneck Distance to Unknot vs M(D)\nr = {:.3f}'.format(corr))
    ax.set_xlabel('Exact Barrier M(D)')
    ax.set_ylabel('Distance')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    
    fig.tight_layout()
    for fmt in ['pdf', 'png']:
        fig.savefig('outputs/phase3_complexity.{}'.format(fmt), dpi=150)
    plt.close(fig)
    print('Saved phase3_complexity')

    # Figure 4: Combined results table figure
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    ax.axis('off')
    
    table_data = [
        ['Diagram', 'cr(D)', 'M(D)', 'Squeeze\nBound', 'BD to\nUnknot', 'M = cr?'],
        ['Goeritz', '11', '11', '12', '12', 'Yes'],
        ['Culprit', '10', '10', '11', '11', 'Yes'],
        ['D28', '28', '28', '28', '28', 'Yes'],
        ['Ochiai II', '45', '45', '46', '46', 'Yes'],
    ]
    
    table = ax.table(cellText=table_data[1:], colLabels=table_data[0],
                     loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 1.8)
    
    for key, cell in table.get_celld().items():
        row, col = key
        if row == 0:
            cell.set_facecolor('#e9ecef')
            cell.set_text_props(fontweight='bold')
        elif col == 5:
            cell.set_facecolor('#d4edda')
    
    ax.set_title('Phase 2+3: Exact Minimax Barriers and Persistence Analysis', 
                 fontsize=14, fontweight='bold', pad=20)
    
    fig.tight_layout()
    for fmt in ['pdf', 'png']:
        fig.savefig('outputs/phase3_results_table.{}'.format(fmt), dpi=150)
    plt.close(fig)
    print('Saved phase3_results_table')


if __name__ == '__main__':
    make_all_figures()
