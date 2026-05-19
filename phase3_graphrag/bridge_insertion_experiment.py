import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def compute_metrics(quality: Dict[str, Any]) -> Dict[str, Any]:
    breakdown = quality.get("breakdown", {})
    context_size = quality.get("context_size", {})
    duplicates = quality.get("duplicates", {})

    vector_hits = breakdown.get("vector_hits", 0)
    graph_expansion = breakdown.get("graph_expansion", 0)
    unique_nodes = breakdown.get("unique_nodes", 0)
    overlap = breakdown.get("overlap", 0)

    overlap_ratio = (overlap / unique_nodes) if unique_nodes else 0.0
    bridge_ratio = (overlap / vector_hits) if vector_hits else 0.0
    semantic_signal_ratio = (vector_hits / unique_nodes) if unique_nodes else 0.0
    expansion_ratio = (graph_expansion / vector_hits) if vector_hits else 0.0

    node_class_diversity = len(
        quality.get("node_class_distribution", {}).get("all", {})
    )
    relation_diversity = len(quality.get("edge_type_distribution", {}))

    depth_avg = quality.get("expansion_depth", {}).get("metrics", {}).get(
        "avg", 0.0
    )

    redundancy = sum(v - 1 for v in duplicates.get("vector_hits", {}).values()) + sum(
        v - 1 for v in duplicates.get("graph_expansion", {}).values()
    )

    words = context_size.get("words", 0)
    noise_amplification = expansion_ratio * (1 - bridge_ratio)
    semantic_coherence_proxy = semantic_signal_ratio * (1 + bridge_ratio)

    return {
        "vector_hits": vector_hits,
        "graph_expansion": graph_expansion,
        "unique_nodes": unique_nodes,
        "overlap_ratio": round(overlap_ratio, 4),
        "bridge_node_frequency": round(bridge_ratio, 4),
        "semantic_signal_ratio": round(semantic_signal_ratio, 4),
        "semantic_coherence_proxy": round(semantic_coherence_proxy, 4),
        "node_class_diversity": node_class_diversity,
        "relation_diversity": relation_diversity,
        "expansion_depth_avg": round(depth_avg, 4),
        "context_words": words,
        "context_growth_rate": round(expansion_ratio, 4),
        "noise_amplification": round(noise_amplification, 4),
        "expansion_redundancy": redundancy,
    }


def extract_bridge_hits(context: Dict[str, Any], bridges: List[Dict[str, str]]) -> Dict[str, int]:
    counts = Counter()
    for item in context.get("graph_expansion", []):
        for step in item.get("path", []):
            for bridge in bridges:
                if (
                    step.get("from") == bridge["source"]
                    and step.get("to") == bridge["target"]
                    and step.get("edge") == bridge["edge"]
                ):
                    counts[bridge["name"]] += 1
    return dict(counts)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    output_dir = base_dir / "output"
    baseline_root = output_dir / "bridge_experiment" / "baseline"
    experiment_root = output_dir / "bridge_experiment" / "experiment"

    queries = [
        ("flooding_drainage", "flooding and drainage"),
        ("multimodal_transport", "multimodal transport"),
        ("weak_infra_maintenance", "weak infrastructure maintenance"),
        ("commuter_impact", "commuter impact"),
        ("policy_governance", "policy/governance"),
        ("public_transport_dependency", "public transport dependency"),
        ("sensor_monitoring", "sensor/monitoring systems"),
    ]

    bridges = [
        {
            "name": "cctv_to_underpass_flooding",
            "source": "sensor-silk-board-cctv",
            "target": "zone-silk-board-underpass-flooding",
            "edge": "MONITORS",
        },
        {
            "name": "spillback_to_underpass_flooding",
            "source": "failure-silk-board-spillback",
            "target": "zone-silk-board-underpass-flooding",
            "edge": "CAUSES",
        },
        {
            "name": "peak_hour_to_hebbal_congestion",
            "source": "pattern-peak-hour-it-commute",
            "target": "zone-hebbal-congestion",
            "edge": "CORRELATES_WITH",
        },
        {
            "name": "two_wheeler_to_hebbal_congestion",
            "source": "pattern-two-wheeler-last-mile",
            "target": "zone-hebbal-congestion",
            "edge": "CORRELATES_WITH",
        },
    ]

    per_query = []
    generic_classes = {"agency", "corridor", "transit_service"}

    for slug, label in queries:
        baseline_quality = load_json(baseline_root / slug / "context_quality.json")
        experiment_quality = load_json(experiment_root / slug / "context_quality.json")
        baseline_context = load_json(baseline_root / slug / "context.json")
        experiment_context = load_json(experiment_root / slug / "context.json")

        base_metrics = compute_metrics(baseline_quality)
        exp_metrics = compute_metrics(experiment_quality)

        delta = {key: round(exp_metrics[key] - base_metrics[key], 4) for key in base_metrics}

        base_edge_types = baseline_quality.get("edge_type_distribution", {})
        exp_edge_types = experiment_quality.get("edge_type_distribution", {})

        base_generic = baseline_quality.get("node_class_distribution", {}).get(
            "graph_expansion", {}
        )
        exp_generic = experiment_quality.get("node_class_distribution", {}).get(
            "graph_expansion", {}
        )

        base_generic_total = sum(
            count for cls, count in base_generic.items() if cls in generic_classes
        )
        exp_generic_total = sum(
            count for cls, count in exp_generic.items() if cls in generic_classes
        )

        bridge_hits = extract_bridge_hits(experiment_context, bridges)

        per_query.append(
            {
                "slug": slug,
                "category": label,
                "baseline": base_metrics,
                "experiment": exp_metrics,
                "delta": delta,
                "edge_types_baseline": base_edge_types,
                "edge_types_experiment": exp_edge_types,
                "generic_expansion_baseline": base_generic_total,
                "generic_expansion_experiment": exp_generic_total,
                "bridge_hits": bridge_hits,
            }
        )

    def average_delta(metric: str) -> float:
        return round(sum(item["delta"][metric] for item in per_query) / len(per_query), 4)

    summary = {
        "average_delta": {
            "semantic_signal_ratio": average_delta("semantic_signal_ratio"),
            "semantic_coherence_proxy": average_delta("semantic_coherence_proxy"),
            "relation_diversity": average_delta("relation_diversity"),
            "node_class_diversity": average_delta("node_class_diversity"),
            "context_growth_rate": average_delta("context_growth_rate"),
            "noise_amplification": average_delta("noise_amplification"),
            "generic_expansion_change": round(
                sum(
                    item["generic_expansion_experiment"]
                    - item["generic_expansion_baseline"]
                    for item in per_query
                )
                / len(per_query),
                4,
            ),
        },
        "bridge_usage": Counter(
            {
                name: sum(
                    item["bridge_hits"].get(name, 0) for item in per_query
                )
                for name in [bridge["name"] for bridge in bridges]
            }
        ),
    }

    sensitivity_baseline = load_json(
        output_dir
        / "bridge_experiment"
        / "sensitivity_baseline"
        / "sensitivity_analysis_report.json"
    )
    sensitivity_experiment = load_json(
        output_dir
        / "bridge_experiment"
        / "sensitivity_experiment"
        / "sensitivity_analysis_report.json"
    )

    sensitivity_summary = {
        "baseline_best_alignment": sensitivity_baseline.get("summary", {}).get(
            "best_alignment_configs"
        ),
        "experiment_best_alignment": sensitivity_experiment.get("summary", {}).get(
            "best_alignment_configs"
        ),
        "baseline_highest_noise": sensitivity_baseline.get("summary", {}).get(
            "highest_noise_configs"
        ),
        "experiment_highest_noise": sensitivity_experiment.get("summary", {}).get(
            "highest_noise_configs"
        ),
    }

    payload = {
        "bridges": bridges,
        "per_query": per_query,
        "summary": summary,
        "sensitivity_summary": sensitivity_summary,
    }

    json_path = output_dir / "bridge_insertion_experiment.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md_lines = []
    md_lines.append("GraphRAG Bridge Insertion Experiment")
    md_lines.append("")
    md_lines.append("Bridges inserted:")
    for bridge in bridges:
        md_lines.append(
            "- {}: {} -> {} ({})".format(
                bridge["name"], bridge["source"], bridge["target"], bridge["edge"]
            )
        )

    md_lines.append("")
    md_lines.append("Average delta (experiment - baseline):")
    for key, value in summary["average_delta"].items():
        md_lines.append("- {}: {:+.4f}".format(key, value))

    md_lines.append("")
    md_lines.append("Bridge usage counts (paths):")
    for name, count in summary["bridge_usage"].items():
        md_lines.append("- {}: {}".format(name, count))

    md_lines.append("")
    md_lines.append("Sensitivity summary:")
    md_lines.append(
        "- baseline best alignment: {}".format(
            ", ".join(sensitivity_summary["baseline_best_alignment"] or [])
        )
    )
    md_lines.append(
        "- experiment best alignment: {}".format(
            ", ".join(sensitivity_summary["experiment_best_alignment"] or [])
        )
    )
    md_lines.append(
        "- baseline highest noise: {}".format(
            ", ".join(sensitivity_summary["baseline_highest_noise"] or [])
        )
    )
    md_lines.append(
        "- experiment highest noise: {}".format(
            ", ".join(sensitivity_summary["experiment_highest_noise"] or [])
        )
    )

    md_lines.append("")
    md_lines.append("Per-query deltas:")
    md_lines.append(
        "| Category | d_semantic_signal | d_noise | d_rel_div | d_node_div | d_context_growth | d_generic_expansion | bridge_hits |"
    )
    md_lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for item in per_query:
        md_lines.append(
            "| {} | {:+.4f} | {:+.4f} | {:+.4f} | {:+.4f} | {:+.4f} | {:+.4f} | {} |".format(
                item["category"],
                item["delta"]["semantic_signal_ratio"],
                item["delta"]["noise_amplification"],
                item["delta"]["relation_diversity"],
                item["delta"]["node_class_diversity"],
                item["delta"]["context_growth_rate"],
                item["generic_expansion_experiment"]
                - item["generic_expansion_baseline"],
                ", ".join(
                    [
                        "{}({})".format(k, v)
                        for k, v in item["bridge_hits"].items()
                    ]
                )
                or "n/a",
            )
        )

    md_path = output_dir / "bridge_insertion_experiment.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print("Wrote {} and {}".format(json_path, md_path))


if __name__ == "__main__":
    main()
