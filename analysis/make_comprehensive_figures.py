"""Generate comprehensive comparison figures for all 5 diagrams."""
import sys
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

sys.path.insert(0, str(Path(__file__).parent.parent))
from experiments.run import DIAGRAMS, HARDNESS


PROJECT = Path(__file__).parent.parent


def load_results():
    """Load all experiment JSON files."""
    output_dir = PROJECT / 'outputs'
    results = {}

    main_file = output_dir / 'full_experiment_results.json'
    if main_file.exists():
        with open(main_file) as f:
            results['main'] = json.load(f)

    for name in ['goeritz_scaling', 'culprit_scaling', 'd28_scaling', 'ochiai_scaling']:
        fpath = output_dir / (name + '.json')
        if fpath.exists():
            with open(fpath) as f:
                results[name] = json.load(f)

    return results


def make_comparison_table(results, output_dir):
    """Generate comparison table figure."""
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.axis('off')

    main = results.get('main', {})

    headers = ['Diagram', 'cr(D)', 'm(D)', 'Bridge', 'Best', 'Mean', 'Std', 'Nodes']
    rows = []

    for name in ['Goeritz', 'Culprit', 'D28', 'OchiaiII', 'Unknot']:
        r = main.get(name, {})
        cr = r.get('initial_crossing_number', 0)
        m = r.get('known_hardness_m', '?')
        br = r.get('bridge_only', {})
        bb = '{:.0f}'.format(br['squeeze_bound']) if br else 'N/A'
        best = '{:.0f}'.format(r.get('squeeze_bound_best', 0))
        mean_val = r.get('squeeze_bound_mean', 0)
        std_val = r.get('squeeze_bound_std', 0)
        mean_str = '{:.1f}'.format(mean_val)
        std_str = '{:.1f}'.format(std_val)
        sd = r.get('seeds_data', [])
        nodes = str(sd[0]['graph_nodes']) if sd else '0'

        rows.append([name, str(cr), str(m), bb, best, mean_str, std_str, nodes])

    table_data = [headers] + rows
    table = ax.table(cellText=rows, colLabels=headers, loc='center',
                     cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)

    for key, cell in table.get_celld().items():
        if key[0] == 0:
            cell.set_facecolor('#4472C4')
            cell.set_text_props(color='white', fontweight='bold')
        elif key[0] % 2 == 0:
            cell.set_facecolor('#D9E2F3')

    plt.title('Squeeze Lemma Bounds: Hard Unknot Diagrams', fontsize=14, pad=20)
    plt.tight_layout()
    fig.savefig(str(output_dir / 'comparison_table.png'), dpi=300, bbox_inches='tight')
    fig.savefig(str(output_dir / 'comparison_table.pdf'), bbox_inches='tight')
    plt.close(fig)
    print("Saved comparison_table.png")


def make_scaling_figure(results, output_dir):
    """Generate scaling plot: bound vs exploration steps."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    plot_data = {
        'Goeritz': ('goeritz_scaling', 11),
        'Culprit': ('culprit_scaling', 10),
        'D28': ('d28_scaling', 28),
        'OchiaiII': ('ochiai_scaling', 45),
    }

    for idx, (name, (key, initial_cn)) in enumerate(plot_data.items()):
        ax = axes[idx // 2][idx % 2]
        data = results.get(key, {}).get('scaling', {})

        if not data:
            ax.text(0.5, 0.5, 'No data', ha='center', va='center',
                    transform=ax.transAxes)
            ax.set_title(name)
            continue

        steps = sorted([int(k) for k in data.keys()])
        bests = [data[str(s)]['best'] for s in steps]
        means = [data[str(s)]['mean'] for s in steps]
        stds = [data[str(s)]['std'] for s in steps]

        ax.errorbar(steps, means, yerr=stds, fmt='o-', capsize=5,
                    label='Mean +/- std', color='#4472C4')
        ax.plot(steps, bests, 's--', color='#ED7D31', label='Best')

        if name == 'Goeritz':
            ax.axhline(y=11, color='green', linestyle=':', label='Bridge-only (11)')

        m_val = HARDNESS.get(name, {}).get('m', 0)
        if m_val > 0:
            ax.axhline(y=initial_cn + m_val, color='red', linestyle='--',
                       label='cr(D)+m(D)={}+{}'.format(initial_cn, m_val))

        ax.axhline(y=initial_cn, color='gray', linestyle='-', alpha=0.3,
                   label='cr(D)={}'.format(initial_cn))

        ax.set_xlabel('Exploration Steps')
        ax.set_ylabel('Squeeze Lemma Bound')
        ax.set_title('{} (cr={}, m={})'.format(name, initial_cn, m_val))
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    plt.suptitle('Squeeze Lemma Bound vs. Exploration Steps\n(Temperature-biased random walk, 3 seeds)',
                 fontsize=14)
    plt.tight_layout()
    fig.savefig(str(output_dir / 'scaling_figure.png'), dpi=300, bbox_inches='tight')
    fig.savefig(str(output_dir / 'scaling_figure.pdf'), bbox_inches='tight')
    plt.close(fig)
    print("Saved scaling_figure.png")


def make_persistence_grid(results, output_dir):
    """Generate grid of persistence diagrams for all diagrams."""
    main = results.get('main', {})
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes_flat = axes.flatten()

    diagram_names = ['Goeritz', 'Culprit', 'D28', 'OchiaiII', 'Unknot']

    for idx, name in enumerate(diagram_names):
        ax = axes_flat[idx]
        r = main.get(name, {})
        sd = r.get('seeds_data', [])

        if not sd:
            if name == 'Unknot':
                ax.text(0.5, 0.5, 'Trivial unknot\n(0 features)', ha='center',
                        va='center', transform=ax.transAxes, fontsize=12)
                ax.set_title('Unknot (control)')
            else:
                ax.text(0.5, 0.5, 'No data', ha='center', va='center',
                        transform=ax.transAxes)
                ax.set_title(name)
            continue

        pairs = sd[0].get('persistence_pairs', [])
        if not pairs:
            ax.text(0.5, 0.5, 'No features', ha='center', va='center',
                    transform=ax.transAxes)
            ax.set_title(name)
            continue

        births = [p[0] for p in pairs]
        deaths = [p[1] for p in pairs]
        all_vals = births + deaths
        min_val = min(all_vals)
        max_val = max(all_vals)

        ax.scatter(births, deaths, alpha=0.7, s=30, edgecolors='k', linewidth=0.5)
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', alpha=0.5)
        ax.set_xlabel('Birth (cn)')
        ax.set_ylabel('Death (cn)')
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)

        bound = sd[0].get('squeeze_bound', 0)
        cr = r.get('initial_crossing_number', 0)
        m = r.get('known_hardness_m', 0)
        nfeat = len(pairs)
        ax.set_title('{}: cr={}, m={}, B={}, n={}'.format(
            name, cr, m, int(bound), nfeat), fontsize=10)

    # Hide extra subplot
    axes_flat[5].axis('off')

    plt.suptitle('Persistence Diagrams: Hard Unknot Diagrams (seed=0)', fontsize=14)
    plt.tight_layout()
    fig.savefig(str(output_dir / 'persistence_grid.png'), dpi=300, bbox_inches='tight')
    fig.savefig(str(output_dir / 'persistence_grid.pdf'), bbox_inches='tight')
    plt.close(fig)
    print("Saved persistence_grid.png")


def make_cn_distribution_figure(results, output_dir):
    """Generate crossing number distribution figure."""
    main = results.get('main', {})
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes_flat = axes.flatten()

    diagram_names = ['Goeritz', 'Culprit', 'D28', 'OchiaiII', 'Unknot']

    for idx, name in enumerate(diagram_names):
        ax = axes_flat[idx]
        r = main.get(name, {})
        sd = r.get('seeds_data', [])

        if not sd:
            if name == 'Unknot':
                ax.bar([0], [1], alpha=0.7, edgecolor='k')
                ax.set_xlabel('Crossing Number')
                ax.set_ylabel('States')
                ax.set_title('Unknot (control)')
            continue

        comp_dist = sd[0].get('cn_distribution_component', {})
        full_dist = sd[0].get('cn_distribution_full', {})

        if comp_dist:
            cns = sorted([int(k) for k in comp_dist.keys()])
            counts = [comp_dist[str(cn)] for cn in cns]
            ax.bar(cns, counts, alpha=0.7, edgecolor='k', color='#4472C4',
                   label='Component')
        elif full_dist:
            cns = sorted([int(k) for k in full_dist.keys()])
            counts = [full_dist[str(cn)] for cn in cns]
            ax.bar(cns, counts, alpha=0.7, edgecolor='k', color='#ED7D31',
                   label='Full graph')

        ax.set_xlabel('Crossing Number')
        ax.set_ylabel('Number of States')
        ax.grid(True, alpha=0.3)
        cr = r.get('initial_crossing_number', 0)
        m = r.get('known_hardness_m', 0)
        ax.set_title('{}: cr={}, m={}'.format(name, cr, m), fontsize=10)

    axes_flat[5].axis('off')

    plt.suptitle('Crossing Number Distribution in Connected Component', fontsize=14)
    plt.tight_layout()
    fig.savefig(str(output_dir / 'cn_distribution.png'), dpi=300, bbox_inches='tight')
    fig.savefig(str(output_dir / 'cn_distribution.pdf'), bbox_inches='tight')
    plt.close(fig)
    print("Saved cn_distribution.png")


def make_bridge_comparison_figure(results, output_dir):
    """Generate bridge vs exploration comparison for Goeritz."""
    main = results.get('main', {})
    goeritz = main.get('Goeritz', {})

    if not goeritz:
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Left: Bridge path cn profile
    bridge = goeritz.get('bridge_only', {})
    if bridge:
        bridge_dist = bridge.get('cn_distribution', {})
        if bridge_dist:
            cns = sorted([int(k) for k in bridge_dist.keys()])
            counts = [bridge_dist[str(cn)] for cn in cns]
            ax1.bar(cns, counts, alpha=0.7, edgecolor='k', color='#70AD47',
                    label='Bridge path')
            ax1.set_xlabel('Crossing Number')
            ax1.set_ylabel('Number of States')
            ax1.set_title('Bridge-Only Subgraph (Goeritz)')
            ax1.legend()
            ax1.grid(True, alpha=0.3)

    # Right: Exploration cn profile
    sd = goeritz.get('seeds_data', [])
    if sd:
        comp_dist = sd[0].get('cn_distribution_component', {})
        if comp_dist:
            cns = sorted([int(k) for k in comp_dist.keys()])
            counts = [comp_dist[str(cn)] for cn in cns]
            ax2.bar(cns, counts, alpha=0.7, edgecolor='k', color='#4472C4',
                    label='Exploration')
            ax2.set_xlabel('Crossing Number')
            ax2.set_ylabel('Number of States')
            ax2.set_title('Exploration Subgraph (Goeritz, seed=0)')
            ax2.legend()
            ax2.grid(True, alpha=0.3)

    plt.suptitle('Bridge Comparator: Lower Envelope vs. Exploration\n(Goeritz: Bridge=11, Exploration=12)',
                 fontsize=13)
    plt.tight_layout()
    fig.savefig(str(output_dir / 'bridge_comparison.png'), dpi=300, bbox_inches='tight')
    fig.savefig(str(output_dir / 'bridge_comparison.pdf'), bbox_inches='tight')
    plt.close(fig)
    print("Saved bridge_comparison.png")


def main():
    output_dir = PROJECT / 'outputs'
    output_dir.mkdir(exist_ok=True)

    results = load_results()
    print("Loaded results for: {}".format(list(results.keys())))

    make_comparison_table(results, output_dir)
    make_scaling_figure(results, output_dir)
    make_persistence_grid(results, output_dir)
    make_cn_distribution_figure(results, output_dir)
    make_bridge_comparison_figure(results, output_dir)

    # Save comprehensive JSON data dump
    json_data = {
        "title": "Comprehensive Experiment Results: Hard Unknot Diagrams",
        "diagrams": list(DIAGRAMS.keys()),
        "gauss_codes": {name: str(word) for name, word in DIAGRAMS.items()},
        "hardness": HARDNESS,
        "results": results.get('main', {}),
        "scaling": {
            "Goeritz": results.get('goeritz_scaling', {}).get('scaling', {}),
            "Culprit": results.get('culprit_scaling', {}).get('scaling', {}),
            "D28": results.get('d28_scaling', {}).get('scaling', {}),
            "OchiaiII": results.get('ochiai_scaling', {}).get('scaling', {}),
        },
        "method": "Temperature-biased random walk on Reidemeister move state graph",
        "squeeze_lemma_definition": "Maximum crossing number in the connected component containing the unknot (cn=0)",
        "move_set": "Full R1+R2+R3 (plane, not S2)",
    }

    with open(output_dir / 'comprehensive_data.json', 'w') as f:
        json.dump(json_data, f, indent=2)
    print("Saved comprehensive_data.json")


if __name__ == '__main__':
    main()
