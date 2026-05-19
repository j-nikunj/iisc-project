import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


def run_command(args: List[str]) -> None:
    subprocess.run(args, check=True)


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
    expansion_only_ratio = (
        (unique_nodes - vector_hits) / unique_nodes if unique_nodes else 0.0
    )

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
    words_per_node = (words / unique_nodes) if unique_nodes else 0.0
    words_per_vector_hit = (words / vector_hits) if vector_hits else 0.0

    noise_amplification = expansion_ratio * (1 - bridge_ratio)
    semantic_coherence_proxy = semantic_signal_ratio * (1 + bridge_ratio)

    return {
        "vector_hits": vector_hits,
        "graph_expansion": graph_expansion,
        "unique_nodes": unique_nodes,
        "overlap": overlap,
        "overlap_ratio": round(overlap_ratio, 4),
        "bridge_node_frequency": round(bridge_ratio, 4),
        "semantic_signal_ratio": round(semantic_signal_ratio, 4),
        "semantic_coherence_proxy": round(semantic_coherence_proxy, 4),
        "node_class_diversity": node_class_diversity,
        "relation_diversity": relation_diversity,
        "expansion_depth_avg": round(depth_avg, 4),
        "context_words": words,
        "words_per_node": round(words_per_node, 2),
        "words_per_vector_hit": round(words_per_vector_hit, 2),
        "context_growth_rate": round(expansion_ratio, 4),
        "expansion_only_ratio": round(expansion_only_ratio, 4),
        "noise_amplification": round(noise_amplification, 4),
        "expansion_redundancy": redundancy,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="GraphRAG sensitivity analysis runner")
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--query", default="multimodal transfer bottlenecks near Silk Board junction")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    output_base = Path(args.output)
    output_base.mkdir(parents=True, exist_ok=True)

    experiments = [
        {"name": "k4_h1_all", "top_k": 4, "hops": 1, "edges": [], "node_classes": [], "edge_label": "all"},
        {"name": "k8_h1_all", "top_k": 8, "hops": 1, "edges": [], "node_classes": [], "edge_label": "all"},
        {"name": "k16_h1_all", "top_k": 16, "hops": 1, "edges": [], "node_classes": [], "edge_label": "all"},
        {"name": "k8_h2_all", "top_k": 8, "hops": 2, "edges": [], "node_classes": [], "edge_label": "all"},
        {"name": "k16_h2_all", "top_k": 16, "hops": 2, "edges": [], "node_classes": [], "edge_label": "all"},
        {"name": "k8_h1_operational", "top_k": 8, "hops": 1, "edges": ["IMPACTS", "DEPENDS_ON", "CONSTRAINS"], "node_classes": [], "edge_label": "operational"},
        {"name": "k8_h1_maintenance_overlap", "top_k": 8, "hops": 1, "edges": ["MAINTAINS", "OVERLAPS_WITH"], "node_classes": [], "edge_label": "maintenance_overlap"},
        {"name": "k8_h1_transit_corridor", "top_k": 8, "hops": 1, "edges": [], "node_classes": ["transit_service", "corridor"], "edge_label": "all"},
    ]

    results = []
    for exp in experiments:
        out_dir = output_base / exp["name"]
        out_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            sys.executable,
            str(base_dir / "graphrag_retrieval.py"),
            "--config",
            args.config,
            "--query",
            args.query,
            "--top-k",
            str(exp["top_k"]),
            "--hops",
            str(exp["hops"]),
            "--output",
            str(out_dir),
        ]

        for edge in exp["edges"]:
            cmd.extend(["--edge", edge])
        for node_class in exp["node_classes"]:
            cmd.extend(["--node-class", node_class])

        run_command(cmd)
        run_command(
            [
                sys.executable,
                str(base_dir / "context_quality.py"),
                "--config",
                args.config,
                "--context",
                str(out_dir / "context.json"),
                "--output-dir",
                str(out_dir),
            ]
        )

        quality = load_json(out_dir / "context_quality.json")
        metrics = compute_metrics(quality)

        results.append(
            {
                "name": exp["name"],
                "query": args.query,
                "params": {
                    "top_k": exp["top_k"],
                    "hops": exp["hops"],
                    "edges": exp["edges"],
                    "node_classes": exp["node_classes"],
                    "edge_filter": exp["edge_label"],
                },
                "metrics": metrics,
            }
        )

    baseline = next((r for r in results if r["name"] == "k8_h1_all"), None)
    baseline_metrics = baseline["metrics"] if baseline else {}

    def delta(metric: str, value: float) -> float:
        base = float(baseline_metrics.get(metric, 0.0))
        return round(value - base, 4)

    for item in results:
        metrics = item["metrics"]
        item["delta_vs_baseline"] = {
            "overlap_ratio": delta("overlap_ratio", metrics["overlap_ratio"]),
            "bridge_node_frequency": delta(
                "bridge_node_frequency", metrics["bridge_node_frequency"]
            ),
            "semantic_signal_ratio": delta(
                "semantic_signal_ratio", metrics["semantic_signal_ratio"]
            ),
            "node_class_diversity": delta(
                "node_class_diversity", metrics["node_class_diversity"]
            ),
            "relation_diversity": delta(
                "relation_diversity", metrics["relation_diversity"]
            ),
            "context_words": delta("context_words", metrics["context_words"]),
            "noise_amplification": delta(
                "noise_amplification", metrics["noise_amplification"]
            ),
        }

    best_alignment = sorted(
        results,
        key=lambda r: (
            r["metrics"]["overlap_ratio"],
            r["metrics"]["bridge_node_frequency"],
            r["metrics"]["semantic_signal_ratio"],
        ),
        reverse=True,
    )[:3]

    highest_noise = sorted(
        results,
        key=lambda r: (
            r["metrics"]["noise_amplification"],
            r["metrics"]["context_growth_rate"],
        ),
        reverse=True,
    )[:3]

    edge_groups: Dict[str, List[Dict[str, Any]]] = {}
    for item in results:
        edge_groups.setdefault(item["params"]["edge_filter"], []).append(item)

    edge_group_stats = {}
    for key, group in edge_groups.items():
        edge_group_stats[key] = {
            "avg_overlap_ratio": round(
                sum(r["metrics"]["overlap_ratio"] for r in group) / len(group), 4
            ),
            "avg_semantic_signal_ratio": round(
                sum(r["metrics"]["semantic_signal_ratio"] for r in group) / len(group), 4
            ),
            "avg_noise_amplification": round(
                sum(r["metrics"]["noise_amplification"] for r in group) / len(group), 4
            ),
            "avg_relation_diversity": round(
                sum(r["metrics"]["relation_diversity"] for r in group) / len(group), 4
            ),
        }

    multi_hop_pairs = [
        ("k8_h1_all", "k8_h2_all"),
        ("k16_h1_all", "k16_h2_all"),
    ]
    multi_hop_effects = []
    for base_name, hop_name in multi_hop_pairs:
        base_item = next((r for r in results if r["name"] == base_name), None)
        hop_item = next((r for r in results if r["name"] == hop_name), None)
        if not base_item or not hop_item:
            continue
        multi_hop_effects.append(
            {
                "pair": f"{base_name} -> {hop_name}",
                "delta_overlap_ratio": round(
                    hop_item["metrics"]["overlap_ratio"]
                    - base_item["metrics"]["overlap_ratio"],
                    4,
                ),
                "delta_semantic_signal_ratio": round(
                    hop_item["metrics"]["semantic_signal_ratio"]
                    - base_item["metrics"]["semantic_signal_ratio"],
                    4,
                ),
                "delta_relation_diversity": round(
                    hop_item["metrics"]["relation_diversity"]
                    - base_item["metrics"]["relation_diversity"],
                    4,
                ),
                "delta_noise_amplification": round(
                    hop_item["metrics"]["noise_amplification"]
                    - base_item["metrics"]["noise_amplification"],
                    4,
                ),
            }
        )

    summary = {
        "best_alignment_configs": [item["name"] for item in best_alignment],
        "highest_noise_configs": [item["name"] for item in highest_noise],
        "edge_filter_stats": edge_group_stats,
        "multi_hop_effects": multi_hop_effects,
        "baseline_config": baseline["name"] if baseline else "n/a",
    }

    payload = {
        "query": args.query,
        "experiments": results,
        "summary": summary,
    }

    report_dir = output_base
    json_path = report_dir / "sensitivity_analysis_report.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md_lines = []
    md_lines.append("GraphRAG Sensitivity Analysis Report")
    md_lines.append("")
    md_lines.append(f"Query: {args.query}")
    md_lines.append("")
    md_lines.append("Experiments:")
    md_lines.append(
        "| Name | top_k | hops | edge_filter | overlap_ratio | semantic_signal | node_class_diversity | relation_diversity | context_words | noise_amplification |"
    )
    md_lines.append(
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"
    )
    for item in results:
        m = item["metrics"]
        params = item["params"]
        md_lines.append(
            "| {} | {} | {} | {} | {:.2f} | {:.2f} | {} | {} | {} | {:.2f} |".format(
                item["name"],
                params["top_k"],
                params["hops"],
                params["edge_filter"],
                m["overlap_ratio"],
                m["semantic_signal_ratio"],
                m["node_class_diversity"],
                m["relation_diversity"],
                m["context_words"],
                m["noise_amplification"],
            )
        )

    md_lines.append("")
    md_lines.append("Key observations:")
    md_lines.append(
        "- best alignment configs: {}".format(
            ", ".join(summary["best_alignment_configs"]) or "n/a"
        )
    )
    md_lines.append(
        "- highest noise configs: {}".format(
            ", ".join(summary["highest_noise_configs"]) or "n/a"
        )
    )
    md_lines.append("- edge filter stats:")
    for key, stats in edge_group_stats.items():
        md_lines.append(
            "  - {}: overlap {:.2f}, semantic {:.2f}, noise {:.2f}, rel_div {:.2f}".format(
                key,
                stats["avg_overlap_ratio"],
                stats["avg_semantic_signal_ratio"],
                stats["avg_noise_amplification"],
                stats["avg_relation_diversity"],
            )
        )

    md_lines.append("")
    md_lines.append("Multi-hop effects:")
    for item in multi_hop_effects:
        md_lines.append(
            "- {}: overlap {:+.2f}, semantic {:+.2f}, rel_div {:+.2f}, noise {:+.2f}".format(
                item["pair"],
                item["delta_overlap_ratio"],
                item["delta_semantic_signal_ratio"],
                item["delta_relation_diversity"],
                item["delta_noise_amplification"],
            )
        )

    md_path = report_dir / "sensitivity_analysis_report.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print("Wrote {} and {}".format(json_path, md_path))


if __name__ == "__main__":
    main()
