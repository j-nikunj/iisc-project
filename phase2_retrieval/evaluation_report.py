import argparse
import json
from pathlib import Path
from time import perf_counter

import networkx as nx

from semantic_utils import coalesce, load_yaml_config, resolve_config_path

from node_parser import load_nodes


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
    parser = argparse.ArgumentParser(description="Generate retrieval evaluation report")
    parser.add_argument("--config", default="")
    parser.add_argument("--root", default="")
    parser.add_argument("--examples", required=True)
    parser.add_argument("--url", default="")
    parser.add_argument("--collection", default="")
    parser.add_argument("--model", default="")
    parser.add_argument("--top-k", type=int, default=0)
    parser.add_argument("--hops", type=int, default=1)
    parser.add_argument("--edge", action="append", default=[])
    parser.add_argument("--output", default="reports/eval_report.json")
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
    graph = build_graph(nodes)

    if args.dry_run:
        Path(args.output).write_text(
            json.dumps({"status": "dry_run", "node_count": len(nodes)}, indent=2),
            encoding="utf-8",
        )
        print("Dry run complete.")
        return

    from qdrant_client import QdrantClient
    from sentence_transformers import SentenceTransformer

    client = QdrantClient(url=url)
    model = SentenceTransformer(model_name)

    examples = load_examples(Path(args.examples))
    report = []
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

        vector_hits = []
        seed_ids = []
        for res in results:
            payload = res.payload or {}
            node_id = payload.get("node_id")
            seed_ids.append(node_id)
            vector_hits.append({
                "node_id": node_id,
                "title": payload.get("title"),
                "node_class": payload.get("node_class"),
                "score": res.score,
                "explanation": "vector_similarity",
            })

        expanded = graph_expand(graph, seed_ids, args.hops, edge_types)
        expanded_nodes = []
        for node_id in sorted(expanded):
            expanded_nodes.append({
                "node_id": node_id,
                "title": graph.nodes[node_id].get("title"),
                "node_class": graph.nodes[node_id].get("node_class"),
                "explanation": "graph_expansion",
            })

        expected_titles = set(example.get("expected_nodes", []))
        vector_titles = {hit["title"] for hit in vector_hits if hit.get("title")}
        expanded_titles = {node["title"] for node in expanded_nodes if node.get("title")}
        expected_hits_vector = sorted(expected_titles.intersection(vector_titles))
        expected_hits_expanded = sorted(expected_titles.intersection(expanded_titles))
        expected_count = len(expected_titles) or 1

        report.append({
            "id": example.get("id"),
            "query": query,
            "latency_ms": latency_ms,
            "vector_hits": vector_hits,
            "graph_expanded_context": expanded_nodes,
            "expected_nodes": example.get("expected_nodes", []),
            "expected_hits_vector": expected_hits_vector,
            "expected_hits_expanded": expected_hits_expanded,
            "expected_coverage_vector": len(expected_hits_vector) / expected_count,
            "expected_coverage_expanded": len(expected_hits_expanded) / expected_count,
            "notes": example.get("notes", ""),
        })

    output_path = Path(args.output)
    output_path.write_text(json.dumps({"results": report}, indent=2), encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
