"""Run exploration scaling sweep: 10k-100k steps for each diagram."""
import sys
import json
import time
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from experiments.run import (
    DIAGRAMS, HARDNESS, temperature_biased_explore,
    compute_cn_distribution, compute_component_cn_distribution,
)
from core.gauss import crossing_number
from core.env import KnotEnv
from tda.graph import StateGraph
from tda.persistence import compute_persistence, summary, squeeze_bound

STEP_LEVELS = [10000, 25000, 50000, 100000]
SEEDS = [0, 1, 2]
TEMPERATURES = [0.1, 0.3, 0.5, 0.8, 1.0]

DIAGRAMS_TO_RUN = ['Goeritz', 'Culprit', 'D28', 'OchiaiII', 'Unknot']

all_sweep = {}

for name in DIAGRAMS_TO_RUN:
    word = DIAGRAMS[name]
    initial_cn = crossing_number(word)
    h = HARDNESS.get(name, {})
    m_val = h.get('m', 0)
    max_cn = initial_cn + m_val + 5
    temp = 0.5 if name != 'D28' else 0.8
    if name == 'Goeritz':
        temp = 0.3

    if name == 'Unknot':
        all_sweep[name] = {
            "initial_cn": 0,
            "all_steps_bound": 0.0,
        }
        print("Unknot: trivial, bound=0")
        continue

    print("\n=== {} (cr={}, m={}) ===".format(name, initial_cn, m_val))

    diagram_sweep = {"initial_cn": initial_cn, "known_m": m_val}

    for num_steps in STEP_LEVELS:
        if name == 'OchiaiII' and num_steps > 50000:
            continue  # too slow

        step_key = str(num_steps)
        bounds = []
        node_counts = []
        times = []

        for seed in SEEDS:
            env = KnotEnv(max_crossings=max_cn + 10)
            graph = StateGraph()
            graph.add_state(word)

            t0 = time.time()
            resets, max_cn_seen = temperature_biased_explore(
                env, graph, num_steps, word,
                seed=seed, max_crossings=max_cn, temperature=temp
            )
            elapsed = time.time() - t0

            nodes, edges, filt = graph.get_graph()
            bound = squeeze_bound(nodes, edges, filt, unknot_filtration=0,
                                   initial_filtration=initial_cn)

            bounds.append(float(bound))
            node_counts.append(graph.num_nodes())
            times.append(elapsed)

        diagram_sweep[step_key] = {
            "bounds": bounds,
            "best": float(min(bounds)),
            "mean": float(np.mean(bounds)),
            "std": float(np.std(bounds)),
            "mean_nodes": float(np.mean(node_counts)),
            "mean_time": float(np.mean(times)),
            "temperature": temp,
            "seeds": SEEDS,
        }
        print("  steps={}: best={}, mean={:.1f}+/-{:.1f}, nodes={:.0f}, time={:.1f}s".format(
            num_steps, min(bounds), np.mean(bounds), np.std(bounds),
            np.mean(node_counts), np.mean(times)))

    all_sweep[name] = diagram_sweep

# Also run temperature sweep for Goeritz
print("\n=== Temperature sweep: Goeritz (50k steps) ===")
temp_sweep = {}
word = DIAGRAMS['Goeritz']
goeritz_initial_cn = crossing_number(word)
max_cn = 11 + 1 + 5
for temp in TEMPERATURES:
    bounds = []
    for seed in SEEDS:
        env = KnotEnv(max_crossings=max_cn + 10)
        graph = StateGraph()
        graph.add_state(word)
        resets, max_cn_seen = temperature_biased_explore(
            env, graph, 50000, word,
            seed=seed, max_crossings=max_cn, temperature=temp
        )
        nodes, edges, filt = graph.get_graph()
        bound = squeeze_bound(nodes, edges, filt, unknot_filtration=0,
                               initial_filtration=goeritz_initial_cn)
        bounds.append(float(bound))
    temp_sweep[str(temp)] = {
        "bounds": bounds,
        "best": float(min(bounds)),
        "mean": float(np.mean(bounds)),
    }
    print("  T={}: best={}, mean={:.1f}".format(temp, min(bounds), np.mean(bounds)))

all_sweep["_temperature_sweep_Goeritz"] = temp_sweep

# Save
output_dir = Path(__file__).parent / 'outputs'
output_dir.mkdir(exist_ok=True)
with open(output_dir / 'scaling_sweep_results.json', 'w') as f:
    json.dump(all_sweep, f, indent=2)
print("\nSaved to outputs/scaling_sweep_results.json")

# Summary table
print("\n" + "=" * 100)
print("{:<12} {:<6} {:<6} {:<10} {:<10} {:<10} {:<10} {:<10}".format(
    "Diagram", "cr", "m", "10k", "25k", "50k", "100k", "Bridge"))
print("-" * 100)
for name in DIAGRAMS_TO_RUN:
    r = all_sweep.get(name, {})
    cr = r.get("initial_cn", 0)
    m = r.get("known_m", 0)
    vals = []
    for step in STEP_LEVELS:
        v = r.get(str(step), {})
        if v:
            vals.append("{:.0f}".format(v.get("best", 0)))
        else:
            vals.append("-")
    bridge = "-"
    if name == "Goeritz":
        bridge = "11"
    print("{:<12} {:<6} {:<6} {:<10} {:<10} {:<10} {:<10} {:<10}".format(
        name, cr, m, vals[0], vals[1], vals[2], vals[3], bridge))
print("=" * 100)
