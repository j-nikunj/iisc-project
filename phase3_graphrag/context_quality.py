import argparse
import json
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List

from graphrag_utils import build_graph, load_config, resolve_paths
from node_parser import load_nodes  # type: ignore


def load_context(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def compute_depth_metrics(depths: List[int]) -> Dict[str, Any]:
    if not depths:
        return {"min": 0, "max": 0, "avg": 0.0}
    return {
        "min": min(depths),
        "max": max(depths),
        "avg": float(mean(depths)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="GraphRAG context quality report")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--context", default="")
    parser.add_argument("--output-dir", default="")
    args = parser.parse_args()

    config = load_config(args.config)
    root = config.get("graph_root")
    output = config.get("output_dir")
    root, output, _reports = resolve_paths(args.config, root, output, None)

    context_path = Path(args.context) if args.context else Path(output) / "context.json"
    output_dir = Path(args.output_dir) if args.output_dir else Path(output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Context quality metrics explain how noisy or sparse the retrieved context is.
    # This is critical because noisy context degrades LLM reasoning and reduces answer focus.
    context = load_context(context_path)

    nodes = load_nodes(Path(root))
    graph, _title_index = build_graph(nodes)

    vector_hits = context.get("vector_hits", [])
    graph_expansion = context.get("graph_expansion", [])

    vector_ids = [hit.get("node_id") for hit in vector_hits if hit.get("node_id")]
    expansion_ids = [item.get("node_id") for item in graph_expansion if item.get("node_id")]

    # Duplicate detection flags redundant nodes that bloat context without adding signal.
    vector_dupes = {k: v for k, v in Counter(vector_ids).items() if v > 1}
    expansion_dupes = {k: v for k, v in Counter(expansion_ids).items() if v > 1}

    unique_ids = set(vector_ids).union(expansion_ids)
    overlap = set(vector_ids).intersection(expansion_ids)

    # Node-class distribution indicates whether retrieval is skewed or balanced.
    def class_counts(ids: List[str]) -> Dict[str, int]:
        return dict(Counter([graph.nodes[node_id].get("node_class") for node_id in ids if node_id in graph.nodes]))

    class_dist_all = class_counts(list(unique_ids))
    class_dist_vector = class_counts(vector_ids)
    class_dist_expanded = class_counts(expansion_ids)

    # Edge-type distribution and top traversed relations show which semantics drive expansion.
    edge_types = []
    depths = []
    for item in graph_expansion:
        path = item.get("path", [])
        depths.append(len(path))
        for step in path:
            edge = step.get("edge")
            if edge:
                edge_types.append(edge)
    edge_type_dist = dict(Counter(edge_types))
    top_relations = Counter(edge_types).most_common(5)

    depth_metrics = compute_depth_metrics(depths)
    depth_hist = dict(Counter(depths))

    context_text = context.get("context_text", "")
    context_stats = {
        "chars": len(context_text),
        "words": len(context_text.split()),
        "lines": len(context_text.splitlines()),
    }

    breakdown = {
        "vector_hits": len(vector_ids),
        "graph_expansion": len(expansion_ids),
        "unique_nodes": len(unique_ids),
        "overlap": len(overlap),
    }

    report = {
        "query": context.get("query"),
        "breakdown": breakdown,
        "node_class_distribution": {
            "all": class_dist_all,
            "vector_hits": class_dist_vector,
            "graph_expansion": class_dist_expanded,
        },
        "edge_type_distribution": edge_type_dist,
        "top_traversed_relations": top_relations,
        "expansion_depth": {
            "metrics": depth_metrics,
            "histogram": depth_hist,
        },
        "duplicates": {
            "vector_hits": vector_dupes,
            "graph_expansion": expansion_dupes,
        },
        "context_size": context_stats,
    }

    (output_dir / "context_quality.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    md_lines = [
        "GraphRAG Context Quality Report",
        "",
        f"Query: {report.get('query')}",
        "",
        "Breakdown:",
        f"- vector_hits: {breakdown['vector_hits']}",
        f"- graph_expansion: {breakdown['graph_expansion']}",
        f"- unique_nodes: {breakdown['unique_nodes']}",
        f"- overlap: {breakdown['overlap']}",
        "",
        "Node-class distribution (all):",
    ]
    for key, val in class_dist_all.items():
        md_lines.append(f"- {key}: {val}")

    md_lines += [
        "",
        "Edge-type distribution:",
    ]
    for key, val in edge_type_dist.items():
        md_lines.append(f"- {key}: {val}")

    md_lines += [
        "",
        "Top traversed relations:",
    ]
    for rel, count in top_relations:
        md_lines.append(f"- {rel}: {count}")

    md_lines += [
        "",
        "Expansion depth metrics:",
        f"- min: {depth_metrics['min']}",
        f"- max: {depth_metrics['max']}",
        f"- avg: {depth_metrics['avg']:.2f}",
        "",
        "Context size:",
        f"- chars: {context_stats['chars']}",
        f"- words: {context_stats['words']}",
        f"- lines: {context_stats['lines']}",
    ]

    (output_dir / "context_quality.md").write_text("\n".join(md_lines), encoding="utf-8")
    print(f"Wrote {output_dir / 'context_quality.json'} and context_quality.md")


if __name__ == "__main__":
    main()
