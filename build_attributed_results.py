"""Build comprehensive attributed results with seed-level detail, 
bridge comparators, and plane-vs-S2 analysis."""

import sys
import json
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from experiments.run import DIAGRAMS, HARDNESS, compute_cn_distribution, compute_component_cn_distribution, load_path_words
from core.gauss import crossing_number
from core.env import KnotEnv
from tda.graph import StateGraph
from tda.persistence import squeeze_bound, compute_persistence, summary
from bridge.inject import inject_path


def compute_bridge_bound(diagram_name, word, bridge_file):
    """Compute bridge-only Squeeze Lemma bound."""
    initial_cn = crossing_number(word)
    bg = StateGraph()
    bg.add_state(word)
    
    with open(bridge_file) as f:
        bdata = json.load(f)
    
    path_variants = bdata.get('paths', {})
    variant_name = list(path_variants.keys())[0]
    path_words = [s['word'] for s in path_variants[variant_name]['states']]
    inject_path(bg, path_words)
    
    bn, be, bf = bg.get_graph()
    bb = squeeze_bound(bn, be, bf, unknot_filtration=0,
                        initial_filtration=initial_cn)
    cn_dist = compute_cn_distribution(bg)
    
    return {
        "squeeze_bound": float(bb),
        "num_nodes": bg.num_nodes(),
        "num_edges": bg.num_edges(),
        "cn_distribution": cn_dist,
        "path_variant": variant_name,
        "barrier_along_path": path_variants[variant_name]['barrier'],
        "num_steps": path_variants[variant_name]['num_steps'],
    }


def main():
    output_dir = Path(__file__).parent / 'outputs'
    output_dir.mkdir(exist_ok=True)

    # Load existing experiment results
    with open(output_dir / 'full_experiment_results.json') as f:
        main_results = json.load(f)

    # Load scaling results
    scaling = {}
    for name, fname in [('Goeritz', 'goeritz_scaling'), ('Culprit', 'culprit_scaling'),
                         ('D28', 'd28_scaling'), ('OchiaiII', 'ochiai_scaling')]:
        fpath = output_dir / (fname + '.json')
        if fpath.exists():
            with open(fpath) as f:
                scaling[name] = json.load(f).get('scaling', {})

    # Build comprehensive attributed results
    attributed = {
        "title": "Squeeze Lemma Upper Bounds on Unknotting Barriers: Attributed Results",
        "method": "Temperature-biased random walk on Reidemeister-move state graph",
        "move_set": "Full {R1, R2, R3} in the plane (NOT S2)",
        "squeeze_lemma_definition": "Maximum crossing number in the connected component of the state graph containing the unknot (cn=0)",
        "note_plane_vs_s2": "In the plane, R1_up can insert a kink at any arc position. In S2, there is an additional R1_through_infinity move (dragging the outermost arc over the point at infinity). Our implementation uses plane moves only. This means some diagrams have LOWER barriers in the plane than in S2.",
        "source": "Gauss codes from Burton et al., 'Hard Diagrams of the Unknot' (Appendix A)",
        "diagrams": {},
    }

    for name in ['Goeritz', 'Culprit', 'D28', 'OchiaiII', 'Unknot']:
        word = DIAGRAMS[name]
        initial_cn = crossing_number(word)
        h = HARDNESS.get(name, {})
        r = main_results.get(name, {})
        sd = r.get('seeds_data', [])

        diag = {
            "initial_crossing_number": initial_cn,
            "known_hardness_m_S2": h.get('m', None),
            "reference": h.get('ref', ''),
            "gauss_code_length": len(word),
            "squeeze_bound_exploration": {},
            "bridge_only": None,
            "seed_variability": {},
            "scaling": scaling.get(name, {}),
            "plane_vs_s2": None,
        }

        # Exploration bounds with per-seed attribution
        if sd:
            bounds = [s['squeeze_bound'] for s in sd]
            best = min(bounds)
            diag["squeeze_bound_exploration"] = {
                "best_over_seeds": float(best),
                "mean": float(np.mean(bounds)),
                "std": float(np.std(bounds)),
                "seeds_finding_best": int(sum(1 for b in bounds if b == best)),
                "total_seeds": len(bounds),
                "per_seed": {
                    str(s['seed']): {
                        "bound": s['squeeze_bound'],
                        "graph_nodes": s['graph_nodes'],
                        "graph_edges": s['graph_edges'],
                        "max_cn_seen": s['max_cn_seen'],
                        "resets": s['resets'],
                        "explore_steps": r.get('explore_steps', 50000),
                        "temperature": r.get('temperature', 0.5),
                    }
                    for s in sd
                },
            }

        # Seed variability analysis
        if sd and scaling.get(name):
            step_keys = sorted(scaling[name].keys(), key=int)
            variability = {}
            for sk in step_keys:
                step_bounds = scaling[name][sk]['bounds']
                step_best = min(step_bounds)
                variability[sk] = {
                    "best": step_best,
                    "seeds_finding_best": int(sum(1 for b in step_bounds if b == step_best)),
                    "total_seeds": len(step_bounds),
                    "per_seed_bounds": step_bounds,
                }
            diag["seed_variability"] = variability

        # Bridge comparator
        bridge_files = {
            'Goeritz': 'bridge/paths.json',
            'Culprit': 'bridge/culprit_paths.json',
            'D28': 'bridge/d28_paths.json',
        }
        if name in bridge_files:
            bf = Path(__file__).parent / bridge_files[name]
            if bf.exists():
                diag["bridge_only"] = compute_bridge_bound(name, word, str(bf))
                diag["bridge_only"]["note"] = "Lower envelope from known monotonic unknotting path (subgraph only)"

        # Plane vs S2 analysis
        if name in ['Goeritz', 'Culprit', 'D28']:
            m_s2 = h.get('m', 0)
            bridge_b = diag.get("bridge_only", {})
            m_plane = None
            if bridge_b:
                m_plane = bridge_b.get("barrier_along_path", None) - initial_cn
            elif sd:
                best_bound = min(s['squeeze_bound'] for s in sd)
                m_plane = best_bound - initial_cn

            diag["plane_vs_s2"] = {
                "m_S2": m_s2,
                "m_plane_empirical": m_plane,
                "discrepancy": (m_plane is not None and m_plane < m_s2),
                "explanation": "Plane R1_up at inner arc positions creates nesting that enables R2_down, which is cheaper than S2 R1_through_infinity" if (m_plane is not None and m_plane < m_s2) else None,
            }

        attributed["diagrams"][name] = diag

    # Save
    with open(output_dir / 'attributed_results.json', 'w') as f:
        json.dump(attributed, f, indent=2)

    # Print summary
    print("=" * 100)
    print("COMPREHENSIVE ATTRIBUTED RESULTS")
    print("=" * 100)
    fmt = "{:<12} {:<5} {:<5} {:<8} {:<8} {:<8} {:<15} {:<8} {:<8}"
    print(fmt.format("Diagram", "cr", "m(S2)", "Bridge", "Best", "Mean", "Seeds@Best", "m(plane)", "Discr."))
    print("-" * 100)

    for name in ['Goeritz', 'Culprit', 'D28', 'OchiaiII', 'Unknot']:
        d = attributed["diagrams"][name]
        cr = d["initial_crossing_number"]
        m_s2 = d["known_hardness_m_S2"]
        br = d.get("bridge_only", {})
        bridge_b = br.get("squeeze_bound", "N/A") if br else "N/A"
        expl = d.get("squeeze_bound_exploration", {})
        best = expl.get("best_over_seeds", "N/A")
        mean = expl.get("mean", "N/A")
        seeds_best = "{}/{}".format(
            expl.get("seeds_finding_best", 0),
            expl.get("total_seeds", 0))
        pvs = d.get("plane_vs_s2", {}) or {}
        m_plane = pvs.get("m_plane_empirical", "N/A")
        discr = "YES" if pvs.get("discrepancy") else "no"

        if isinstance(mean, float):
            mean = "{:.1f}".format(mean)
        if isinstance(best, float):
            best = "{:.0f}".format(best)
        if isinstance(bridge_b, float):
            bridge_b = "{:.0f}".format(bridge_b)
        if isinstance(m_plane, (int, float)) and m_plane is not None:
            m_plane = str(m_plane)

        print(fmt.format(name, cr, str(m_s2), str(bridge_b), str(best),
                         str(mean), seeds_best, str(m_plane), discr))

    print("=" * 100)
    print("\nSaved to outputs/attributed_results.json")


if __name__ == '__main__':
    main()
