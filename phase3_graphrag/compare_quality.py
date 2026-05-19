import json
import os


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def main() -> None:
    base = "d:/iisc project/phase3_graphrag/output"
    entries = [
        (
            "flooding_drainage",
            "flooding and drainage",
            "flooding and drainage bottlenecks near Silk Board junction",
        ),
        (
            "multimodal_transport",
            "multimodal transport",
            "multimodal transfer bottlenecks near Silk Board junction",
        ),
        (
            "weak_infra_maintenance",
            "weak infrastructure maintenance",
            "weak infrastructure maintenance risks on Outer Ring Road corridor",
        ),
        (
            "commuter_impact",
            "commuter impact",
            "commuter impact from corridor disruptions near Silk Board",
        ),
        (
            "policy_governance",
            "policy/governance",
            "policy and governance constraints on corridor upgrades in Bengaluru",
        ),
        (
            "public_transport_dependency",
            "public transport dependency",
            "public transport dependency for commuters near Silk Board",
        ),
        (
            "sensor_monitoring",
            "sensor/monitoring systems",
            "sensor and monitoring systems for traffic and drainage near Silk Board",
        ),
    ]

    reports = []
    class_exp_counts: dict[str, int] = {}
    class_vec_counts: dict[str, int] = {}
    class_exp_cat_counts: dict[str, set[str]] = {}
    class_vec_cat_counts: dict[str, set[str]] = {}
    relation_counts: dict[str, int] = {}
    relation_cat_counts: dict[str, set[str]] = {}

    for slug, label, query in entries:
        data = load_json(os.path.join(base, slug, "context_quality.json"))
        breakdown = data.get("breakdown", {})
        vector_hits = breakdown.get("vector_hits", 0)
        graph_exp = breakdown.get("graph_expansion", 0)
        unique = breakdown.get("unique_nodes", 0)
        overlap = breakdown.get("overlap", 0)
        overlap_ratio = (overlap / unique) if unique else 0.0

        class_dist_all = data.get("node_class_distribution", {}).get("all", {})
        class_dist_vector = data.get("node_class_distribution", {}).get(
            "vector_hits", {}
        )
        class_dist_expanded = data.get("node_class_distribution", {}).get(
            "graph_expansion", {}
        )

        node_class_diversity = len(class_dist_all)
        relation_diversity = len(data.get("edge_type_distribution", {}))
        depth_avg = data.get("expansion_depth", {}).get("metrics", {}).get(
            "avg", 0.0
        )

        duplicates = data.get("duplicates", {})
        red_vec = sum(v - 1 for v in duplicates.get("vector_hits", {}).values())
        red_exp = sum(v - 1 for v in duplicates.get("graph_expansion", {}).values())
        redundancy = red_vec + red_exp

        expansion_only = sorted(
            set(class_dist_expanded.keys()) - set(class_dist_vector.keys())
        )
        vector_only = sorted(
            set(class_dist_vector.keys()) - set(class_dist_expanded.keys())
        )

        score = round(
            overlap_ratio * 2
            + node_class_diversity / 10
            + relation_diversity / 10
            + depth_avg / 3
            - redundancy / 20,
            4,
        )

        reports.append(
            {
                "slug": slug,
                "category": label,
                "query": query,
                "metrics": {
                    "vector_hits": vector_hits,
                    "graph_expansion": graph_exp,
                    "unique_nodes": unique,
                    "overlap": overlap,
                    "overlap_ratio": round(overlap_ratio, 4),
                    "node_class_diversity": node_class_diversity,
                    "relation_diversity": relation_diversity,
                    "expansion_depth_avg": depth_avg,
                    "redundancy_count": redundancy,
                    "composite_score": score,
                },
                "expansion_only_classes": expansion_only,
                "vector_only_classes": vector_only,
            }
        )

        for cls, count in class_dist_expanded.items():
            class_exp_counts[cls] = class_exp_counts.get(cls, 0) + count
            class_exp_cat_counts.setdefault(cls, set()).add(slug)

        for cls, count in class_dist_vector.items():
            class_vec_counts[cls] = class_vec_counts.get(cls, 0) + count
            class_vec_cat_counts.setdefault(cls, set()).add(slug)

        for rel, count in data.get("edge_type_distribution", {}).items():
            relation_counts[rel] = relation_counts.get(rel, 0) + count
            relation_cat_counts.setdefault(rel, set()).add(slug)

    reports_sorted_score = sorted(
        reports, key=lambda r: r["metrics"]["composite_score"], reverse=True
    )
    reports_sorted_overlap = sorted(
        reports, key=lambda r: r["metrics"]["overlap_ratio"], reverse=True
    )

    strongest = [r["category"] for r in reports_sorted_score[:2]]
    weakest = [r["category"] for r in reports_sorted_score[-2:]]

    align_well = [
        r["category"]
        for r in reports_sorted_overlap
        if r["metrics"]["overlap_ratio"] > 0
    ][:2]
    if not align_well:
        align_well = [r["category"] for r in reports_sorted_overlap[:2]]

    diverge = [r["category"] for r in reports_sorted_overlap[-2:]]

    expansion_improves = [
        r["category"]
        for r in reports
        if r["metrics"]["graph_expansion"] > 0 and r["expansion_only_classes"]
    ]
    expansion_noise = [
        r["category"]
        for r in reports
        if r["metrics"]["overlap_ratio"] == 0
        and r["metrics"]["relation_diversity"] <= 1
    ]

    weak_anchor_classes = sorted(
        [cls for cls in class_exp_cat_counts if cls not in class_vec_cat_counts]
    )
    generic_classes = sorted(
        [
            cls
            for cls in class_exp_cat_counts
            if len(class_exp_cat_counts[cls]) >= 3
            and len(class_vec_cat_counts.get(cls, set())) <= 1
        ]
    )
    rare_relations = sorted(
        [rel for rel in relation_cat_counts if len(relation_cat_counts[rel]) == 1]
    )
    common_relations = sorted(
        relation_counts.items(), key=lambda kv: kv[1], reverse=True
    )[:5]
    disconnected = [
        r["category"]
        for r in reports
        if r["metrics"]["overlap_ratio"] == 0
        and r["metrics"]["relation_diversity"] <= 1
        and r["metrics"]["expansion_depth_avg"] <= 1
    ]

    summary = {
        "strongest_categories": strongest,
        "weakest_categories": weakest,
        "graph_expansion_improves": expansion_improves,
        "graph_expansion_noise": expansion_noise,
        "semantic_graph_alignment": align_well,
        "semantic_graph_divergence": diverge,
        "weak_semantic_anchor_classes": weak_anchor_classes,
        "over_generic_node_classes": generic_classes,
        "rare_relations": rare_relations,
        "common_relations": common_relations,
        "disconnected_topology_categories": disconnected,
    }

    payload = {
        "queries": [
            {"slug": slug, "category": label, "query": query}
            for slug, label, query in entries
        ],
        "per_query": reports,
        "summary": summary,
    }

    json_path = os.path.join(base, "comparative_quality_report.json")
    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)

    md_lines = []
    md_lines.append("Comparative GraphRAG Context Quality Report")
    md_lines.append("")
    md_lines.append("Queries:")
    for _slug, label, query in entries:
        md_lines.append("- {}: {}".format(label, query))
    md_lines.append("")
    md_lines.append("Per-category metrics:")
    md_lines.append(
        "| Category | overlap_ratio | node_class_diversity | relation_diversity | depth_avg | redundancy | vector_hits | graph_expansion |"
    )
    md_lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for report in reports_sorted_score:
        metrics = report["metrics"]
        md_lines.append(
            "| {} | {:.2f} | {} | {} | {:.2f} | {} | {} | {} |".format(
                report["category"],
                metrics["overlap_ratio"],
                metrics["node_class_diversity"],
                metrics["relation_diversity"],
                metrics["expansion_depth_avg"],
                metrics["redundancy_count"],
                metrics["vector_hits"],
                metrics["graph_expansion"],
            )
        )

    md_lines.append("")
    md_lines.append("Summary:")
    md_lines.append(
        "- strongest categories: {}".format(
            ", ".join(strongest) if strongest else "n/a"
        )
    )
    md_lines.append(
        "- weakest categories: {}".format(
            ", ".join(weakest) if weakest else "n/a"
        )
    )
    md_lines.append(
        "- graph expansion improves: {}".format(
            ", ".join(expansion_improves) if expansion_improves else "n/a"
        )
    )
    md_lines.append(
        "- graph expansion introduces noise: {}".format(
            ", ".join(expansion_noise) if expansion_noise else "n/a"
        )
    )
    md_lines.append(
        "- semantic/graph alignment: {}".format(
            ", ".join(align_well) if align_well else "n/a"
        )
    )
    md_lines.append(
        "- semantic/graph divergence: {}".format(
            ", ".join(diverge) if diverge else "n/a"
        )
    )

    md_lines.append("")
    md_lines.append("Structural signals:")
    md_lines.append(
        "- weak semantic anchor classes: {}".format(
            ", ".join(weak_anchor_classes) if weak_anchor_classes else "n/a"
        )
    )
    md_lines.append(
        "- over-generic node classes: {}".format(
            ", ".join(generic_classes) if generic_classes else "n/a"
        )
    )
    md_lines.append(
        "- rare relations: {}".format(
            ", ".join(rare_relations) if rare_relations else "n/a"
        )
    )
    md_lines.append(
        "- common relations: {}".format(
            ", ".join(
                ["{}({})".format(rel, count) for rel, count in common_relations]
            )
            if common_relations
            else "n/a"
        )
    )
    md_lines.append(
        "- disconnected topology categories: {}".format(
            ", ".join(disconnected) if disconnected else "n/a"
        )
    )

    md_path = os.path.join(base, "comparative_quality_report.md")
    with open(md_path, "w", encoding="utf-8") as file:
        file.write("\n".join(md_lines))

    print("Wrote {} and {}".format(json_path, md_path))


if __name__ == "__main__":
    main()
