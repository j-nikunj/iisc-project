import argparse
import json
from collections import Counter
from pathlib import Path
from time import perf_counter

import networkx as nx

from node_parser import load_nodes
from semantic_utils import coalesce, load_yaml_config, resolve_config_path


def load_examples(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def build_graph(nodes) -> nx.MultiDiGraph:
    graph = nx.MultiDiGraph()
    title_to_id = {}
    for node in nodes:
        meta = node.meta
        node_id = meta.get("id")
        title = meta.get("title")
        title_to_id[title] = node_id
        graph.add_node(node_id, **meta)
    for node in nodes:
        source_id = node.meta.get("id")
        for rel in node.relations:
            target_id = title_to_id.get(rel.target)
            if not target_id:
                continue
            graph.add_edge(source_id, target_id, edge_type=rel.edge_type)
    return graph


def graph_expand(graph: nx.MultiDiGraph, seeds, hops: int, edge_types):
    visited = set(seeds)
    frontier = set(seeds)
    for _ in range(hops):
        next_frontier = set()
        for node_id in frontier:
            for _, target_id, data in graph.out_edges(node_id, data=True):
                if edge_types and data.get("edge_type") not in edge_types:
                    continue
                if target_id not in visited:
                    next_frontier.add(target_id)
            for source_id, _, data in graph.in_edges(node_id, data=True):
                if edge_types and data.get("edge_type") not in edge_types:
                    continue
                if source_id not in visited:
                    next_frontier.add(source_id)
        visited.update(next_frontier)
        frontier = next_frontier
    return visited


def main() -> None:
    parser = argparse.ArgumentParser(description="Retrieval metrics report")
    parser.add_argument("--config", default="")
    parser.add_argument("--root", default="")
    parser.add_argument("--examples", required=True)
    parser.add_argument("--url", default="")
    parser.add_argument("--collection", default="")
    parser.add_argument("--model", default="")
    parser.add_argument("--top-k", type=int, default=0)
    parser.add_argument("--output", default="metrics_report.json")
    parser.add_argument("--hops", type=int, default=1)
    parser.add_argument("--edge", action="append", default=[])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    config = load_yaml_config(args.config)
    qdrant_cfg = config.get("qdrant", {})
    retrieval_cfg = config.get("retrieval", {})
    root = coalesce(args.root, config.get("graph_root"))
    root = resolve_config_path(args.config, root)
    url = coalesce(args.url, qdrant_cfg.get("url"), "http://localhost:6333")
    collection = coalesce(args.collection, qdrant_cfg.get("collection"))
    model_name = coalesce(args.model, config.get("embedding", {}).get("model_name"), "BAAI/bge-small-en-v1.5")
    top_k = args.top_k or retrieval_cfg.get("top_k", 8)
    edge_types = set(args.edge or retrieval_cfg.get("edge_types", []))
    if not root or not collection:
        raise SystemExit("--root and --collection are required (or provide config.yaml)")

    nodes = load_nodes(Path(root))
    node_classes = {n.meta.get("id"): n.meta.get("node_class") for n in nodes}
    graph = build_graph(nodes)

    if args.dry_run:
        Path(args.output).write_text(
            json.dumps({"node_count": len(nodes), "status": "dry_run"}, indent=2),
            encoding="utf-8",
        )
        print("Dry run complete.")
        return

    from qdrant_client import QdrantClient
    from sentence_transformers import SentenceTransformer

    client = QdrantClient(url=url)
    model = SentenceTransformer(model_name)

    examples = load_examples(Path(args.examples))
    results_out = []
    retrieved_nodes = set()
    for example in examples:
        query = example["query"]
        start = perf_counter()
        query_vec = model.encode(query, normalize_embeddings=True)
        results = client.search(
            collection_name=collection,
            query_vector=query_vec.tolist(),
            limit=top_k,
            with_payload=True,
        )
        latency_ms = (perf_counter() - start) * 1000.0

        top_ids = [res.payload.get("node_id") for res in results if res.payload]
        class_dist = Counter(node_classes.get(node_id) for node_id in top_ids)
        retrieved_nodes.update(top_ids)

        expanded = graph_expand(graph, top_ids, args.hops, edge_types)
        expanded_class_dist = Counter(node_classes.get(node_id) for node_id in expanded)

        results_out.append({
            "id": example.get("id"),
            "query": query,
            "latency_ms": latency_ms,
            "top_k": top_k,
            "top_ids": top_ids,
            "node_class_distribution": dict(class_dist),
            "graph_expansion_size": len(expanded),
            "expanded_node_class_distribution": dict(expanded_class_dist),
            "scores": [res.score for res in results],
        })

    coverage = 0.0
    if nodes:
        coverage = len(retrieved_nodes) / len(nodes)

    output_path = Path(args.output)
    output_path.write_text(
        json.dumps({"results": results_out, "retrieval_coverage": coverage}, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
