"""Run full scaled experiment across all 5 diagrams."""
import sys
import json
import time
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from experiments.run import (
    DIAGRAMS, HARDNESS, temperature_biased_explore,
    compute_cn_distribution, compute_component_cn_distribution,
    load_path_words
)
from core.gauss import crossing_number
from core.env import KnotEnv
from tda.graph import StateGraph
from tda.persistence import compute_persistence, summary, squeeze_bound, plot_diagram
from bridge.inject import inject_path

STEP_SCALE = {
    'Unknot':    100,
    'Culprit':   50000,
    'Goeritz':   50000,
    'D28':       50000,
    'OchiaiII':  20000,
}

TEMP_SCALE = {
    'Unknot':    0.3,
    'Culprit':   0.5,
    'Goeritz':   0.3,
    'D28':       0.8,
    'OchiaiII':  0.5,
}

seeds = [0, 1, 2]
all_results = {}

for name, word in DIAGRAMS.items():
    initial_cn = crossing_number(word)
    h = HARDNESS.get(name, {})
    m_val = h.get('m', 0)
    max_cn = initial_cn + m_val + 5
    num_steps = STEP_SCALE.get(name, 50000)
    temp = TEMP_SCALE.get(name, 0.5)

    print("")
    print("=" * 60)
    print("Diagram: {} | cr={} | m={} | steps={} | T={} | max_cn={}".format(
        name, initial_cn, m_val, num_steps, temp, max_cn))
    print("=" * 60)
    t0 = time.time()

    res = {
        "diagram": name,
        "initial_crossing_number": initial_cn,
        "known_hardness_m": m_val,
        "reference": h.get('ref', ''),
        "max_crossings": max_cn,
        "temperature": temp,
        "seeds": seeds,
        "explore_steps": num_steps,
    }

    # Bridge comparator for Goeritz
    if name == 'Goeritz':
        bridge_path_file = Path(__file__).parent / 'bridge' / 'paths.json'
        if bridge_path_file.exists():
            bg = StateGraph()
            bg.add_state(word)
            pw = load_path_words(str(bridge_path_file), variant='r1up_r2down')
            inject_path(bg, pw)
            bn, be, bf = bg.get_graph()
            bb = squeeze_bound(bn, be, bf, unknot_filtration=0)
            bcn = compute_cn_distribution(bg)
            res['bridge_only'] = {
                "squeeze_bound": float(bb),
                "num_nodes": bg.num_nodes(),
                "num_edges": bg.num_edges(),
                "cn_distribution": bcn,
            }
            print("  Bridge-only: bound={}".format(bb))

    # Unknot is trivial
    if name == 'Unknot':
        res["squeeze_bound_best"] = 0.0
        res["squeeze_bound_mean"] = 0.0
        res["squeeze_bound_std"] = 0.0
        res["seeds_data"] = []
        all_results[name] = res
        print("  Trivial: bound=0")
        continue

    seed_bounds = []
    seed_data = []
    for seed in seeds:
        env = KnotEnv(max_crossings=max_cn + 10)
        graph = StateGraph()
        graph.add_state(word)

        if name == 'Goeritz':
            bridge_path_file = Path(__file__).parent / 'bridge' / 'paths.json'
            if bridge_path_file.exists():
                pw = load_path_words(str(bridge_path_file), variant='r1up_r2down')
                inject_path(graph, pw)

        resets, max_cn_seen = temperature_biased_explore(
            env, graph, num_steps, word,
            seed=seed, max_crossings=max_cn, temperature=temp
        )

        nodes, edges, filt = graph.get_graph()
        bound = squeeze_bound(nodes, edges, filt, unknot_filtration=0)
        diagram_pd = compute_persistence(nodes, edges, filt)
        pd_summ = summary(diagram_pd)
        cn_dist = compute_cn_distribution(graph)
        comp_cn_dist = compute_component_cn_distribution(graph)

        seed_bounds.append(bound)
        sd = {
            "seed": seed,
            "squeeze_bound": float(bound),
            "resets": resets,
            "max_cn_seen": max_cn_seen,
            "graph_nodes": graph.num_nodes(),
            "graph_edges": graph.num_edges(),
            "persistence_summary": {
                k: (float(v) if hasattr(v, '__float__') else v)
                for k, v in pd_summ.items()
            },
            "persistence_pairs": [[float(b), float(d)] for b, d in diagram_pd],
            "cn_distribution_full": cn_dist,
            "cn_distribution_component": comp_cn_dist,
        }
        seed_data.append(sd)

        # Save per-seed persistence diagram
        output_dir = Path(__file__).parent / 'outputs'
        output_dir.mkdir(exist_ok=True)
        pd_path = str(output_dir / "{}_seed{}_pd.png".format(name, seed))
        plot_diagram(diagram_pd, pd_path,
                     title="{} (seed={}) Persistence Diagram".format(name, seed))
        graph.save(str(output_dir / "{}_seed{}_graph.pkl".format(name, seed)))

        print("  Seed {}: bound={}, nodes={}, edges={}, max_cn={}, resets={}".format(
            seed, bound, graph.num_nodes(), graph.num_edges(), max_cn_seen, resets))

    res["seeds_data"] = seed_data
    res["squeeze_bound_best"] = float(min(seed_bounds))
    res["squeeze_bound_mean"] = float(np.mean(seed_bounds))
    res["squeeze_bound_std"] = float(np.std(seed_bounds))
    all_results[name] = res
    elapsed = time.time() - t0
    print("  Time: {:.1f}s | Best={} | Mean={:.1f}+/-{:.1f}".format(
        elapsed, res["squeeze_bound_best"],
        res["squeeze_bound_mean"], res["squeeze_bound_std"]))

# Save combined results
output_dir = Path(__file__).parent / 'outputs'
output_dir.mkdir(exist_ok=True)
with open(output_dir / 'full_experiment_results.json', 'w') as f:
    json.dump(all_results, f, indent=2)
print("\nSaved combined results to outputs/full_experiment_results.json")

# Print comparison table
print("")
print("=" * 95)
header = "{:<12} {:<7} {:<6} {:<8} {:<8} {:<10} {:<8} {:<8}".format(
    "Diagram", "cr(D)", "m(D)", "Bridge", "Best", "Mean", "Std", "Nodes")
print(header)
print("-" * 95)
for name, r in all_results.items():
    cr = r["initial_crossing_number"]
    m = r.get("known_hardness_m", "?")
    br = r.get("bridge_only", {})
    bb = str(br.get("squeeze_bound", "N/A")) if br else "N/A"
    best = str(r.get("squeeze_bound_best", "N/A"))
    mean_val = r.get("squeeze_bound_mean", 0)
    std_val = r.get("squeeze_bound_std", 0)
    nodes_val = r["seeds_data"][0]["graph_nodes"] if r.get("seeds_data") else 0
    mean_str = "{:.1f}".format(mean_val) if isinstance(mean_val, float) else str(mean_val)
    std_str = "{:.1f}".format(std_val) if isinstance(std_val, float) else str(std_val)
    row = "{:<12} {:<7} {:<6} {:<8} {:<8} {:<10} {:<8} {:<8}".format(
        name, cr, str(m), bb, best, mean_str, std_str, str(nodes_val))
    print(row)
print("=" * 95)
