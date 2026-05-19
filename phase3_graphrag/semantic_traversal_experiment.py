import json
from pathlib import Path
from typing import Any, Dict


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def compute_metrics(quality: Dict[str, Any]) -> Dict[str, Any]:
    breakdown = quality.get("breakdown", {})
    context_size = quality.get("context_size", {})
    edge_types = quality.get("edge_type_distribution", {})

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
    relation_diversity = len(edge_types)

    depth_avg = quality.get("expansion_depth", {}).get("metrics", {}).get(
        "avg", 0.0
    )

    words = context_size.get("words", 0)
    words_per_node = (words / unique_nodes) if unique_nodes else 0.0

    operational_edges = {"IMPACTS", "DEPENDS_ON", "CONSTRAINS"}
    operational_count = sum(edge_types.get(edge, 0) for edge in operational_edges)
    total_edges = sum(edge_types.values()) or 1
    operational_ratio = operational_count / total_edges

    generic_classes = {"agency", "corridor", "transit_service"}
    expansion_class_dist = quality.get("node_class_distribution", {}).get(
        "graph_expansion", {}
    )
    generic_expansion = sum(
        count for cls, count in expansion_class_dist.items() if cls in generic_classes
    )
    generic_expansion_ratio = (
        generic_expansion / graph_expansion if graph_expansion else 0.0
    )

    noise_amplification = expansion_ratio * (1 - bridge_ratio)
    semantic_coherence_proxy = semantic_signal_ratio * (1 + bridge_ratio)
    continuity_proxy = semantic_signal_ratio * (1 - generic_expansion_ratio)

    return {
        "vector_hits": vector_hits,
        "graph_expansion": graph_expansion,
        "unique_nodes": unique_nodes,
        "overlap_ratio": round(overlap_ratio, 4),
        "semantic_signal_ratio": round(semantic_signal_ratio, 4),
        "semantic_coherence_proxy": round(semantic_coherence_proxy, 4),
        "context_density": round(words_per_node, 2),
        "context_growth_rate": round(expansion_ratio, 4),
        "noise_amplification": round(noise_amplification, 4),
        "node_class_diversity": node_class_diversity,
        "relation_diversity": relation_diversity,
        "expansion_depth_avg": round(depth_avg, 4),
        "operational_edge_ratio": round(operational_ratio, 4),
        "generic_expansion_ratio": round(generic_expansion_ratio, 4),
        "continuity_proxy": round(continuity_proxy, 4),
    }


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    output_dir = base_dir / "output" / "semantic_traversal"
    baseline_root = output_dir / "baseline"
    semantic_root = output_dir / "semantic"

    queries = [
        ("flooding_drainage", "flooding and drainage"),
        ("multimodal_transport", "multimodal transport"),
        ("weak_infra_maintenance", "weak infrastructure maintenance"),
        ("commuter_impact", "commuter impact"),
        ("policy_governance", "policy/governance"),
        ("public_transport_dependency", "public transport dependency"),
        ("sensor_monitoring", "sensor/monitoring systems"),
    ]

    per_query = []
    for slug, label in queries:
        baseline_quality = load_json(baseline_root / slug / "context_quality.json")
        semantic_quality = load_json(semantic_root / slug / "context_quality.json")

        base_metrics = compute_metrics(baseline_quality)
        sem_metrics = compute_metrics(semantic_quality)

        delta = {key: round(sem_metrics[key] - base_metrics[key], 4) for key in base_metrics}

        per_query.append(
            {
                "slug": slug,
                "category": label,
                "baseline": base_metrics,
                "semantic": sem_metrics,
                "delta": delta,
            }
        )

    def average_delta(metric: str) -> float:
        return round(sum(item["delta"][metric] for item in per_query) / len(per_query), 4)

    summary = {
        "average_delta": {
            "semantic_signal_ratio": average_delta("semantic_signal_ratio"),
            "semantic_coherence_proxy": average_delta("semantic_coherence_proxy"),
            "context_density": average_delta("context_density"),
            "noise_amplification": average_delta("noise_amplification"),
            "relation_diversity": average_delta("relation_diversity"),
            "node_class_diversity": average_delta("node_class_diversity"),
            "operational_edge_ratio": average_delta("operational_edge_ratio"),
            "generic_expansion_ratio": average_delta("generic_expansion_ratio"),
            "continuity_proxy": average_delta("continuity_proxy"),
        }
    }

    sensitivity_baseline = load_json(
        output_dir / "sensitivity_baseline" / "sensitivity_analysis_report.json"
    )
    sensitivity_semantic = load_json(
        output_dir / "sensitivity_semantic" / "sensitivity_analysis_report.json"
    )

    sensitivity_summary = {
        "baseline_best_alignment": sensitivity_baseline.get("summary", {}).get(
            "best_alignment_configs"
        ),
        "semantic_best_alignment": sensitivity_semantic.get("summary", {}).get(
            "best_alignment_configs"
        ),
        "baseline_highest_noise": sensitivity_baseline.get("summary", {}).get(
            "highest_noise_configs"
        ),
        "semantic_highest_noise": sensitivity_semantic.get("summary", {}).get(
            "highest_noise_configs"
        ),
    }

    payload = {
        "per_query": per_query,
        "summary": summary,
        "sensitivity_summary": sensitivity_summary,
    }

    json_path = output_dir / "semantic_traversal_experiment.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md_lines = []
    md_lines.append("GraphRAG Semantic Traversal Experiment")
    md_lines.append("")
    md_lines.append("Average delta (semantic - baseline):")
    for key, value in summary["average_delta"].items():
        md_lines.append("- {}: {:+.4f}".format(key, value))

    md_lines.append("")
    md_lines.append("Sensitivity summary:")
    md_lines.append(
        "- baseline best alignment: {}".format(
            ", ".join(sensitivity_summary["baseline_best_alignment"] or [])
        )
    )
    md_lines.append(
        "- semantic best alignment: {}".format(
            ", ".join(sensitivity_summary["semantic_best_alignment"] or [])
        )
    )
    md_lines.append(
        "- baseline highest noise: {}".format(
            ", ".join(sensitivity_summary["baseline_highest_noise"] or [])
        )
    )
    md_lines.append(
        "- semantic highest noise: {}".format(
            ", ".join(sensitivity_summary["semantic_highest_noise"] or [])
        )
    )

    md_lines.append("")
    md_lines.append("Per-query deltas:")
    md_lines.append(
        "| Category | d_semantic_signal | d_coherence | d_density | d_noise | d_rel_div | d_operational | d_generic_ratio | d_continuity |"
    )
    md_lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for item in per_query:
        md_lines.append(
            "| {} | {:+.4f} | {:+.4f} | {:+.4f} | {:+.4f} | {:+.4f} | {:+.4f} | {:+.4f} | {:+.4f} |".format(
                item["category"],
                item["delta"]["semantic_signal_ratio"],
                item["delta"]["semantic_coherence_proxy"],
                item["delta"]["context_density"],
                item["delta"]["noise_amplification"],
                item["delta"]["relation_diversity"],
                item["delta"]["operational_edge_ratio"],
                item["delta"]["generic_expansion_ratio"],
                item["delta"]["continuity_proxy"],
            )
        )

    md_path = output_dir / "semantic_traversal_experiment.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print("Wrote {} and {}".format(json_path, md_path))


if __name__ == "__main__":
    main()
