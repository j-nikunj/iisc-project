import argparse
from pathlib import Path
from typing import List, Set

import networkx as nx

from node_parser import load_nodes
from semantic_utils import coalesce, load_yaml_config, resolve_config_path


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


def build_filter(node_classes: List[str], tags: List[str], snapshot: str):
    from qdrant_client.http import models as qdrant_models

    must = []
    if node_classes:
        must.append(qdrant_models.FieldCondition(key="node_class", match=qdrant_models.MatchAny(any=node_classes)))
    if tags:
        must.append(qdrant_models.FieldCondition(key="tags", match=qdrant_models.MatchAny(any=tags)))
    if snapshot:
        must.append(qdrant_models.FieldCondition(key="graph_snapshot_version", match=qdrant_models.MatchValue(value=snapshot)))
    if not must:
        return None
    return qdrant_models.Filter(must=must)


def graph_expand(graph: nx.MultiDiGraph, seeds: List[str], hops: int, edge_types: Set[str]) -> Set[str]:
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
    parser = argparse.ArgumentParser(description="Hybrid vector + graph retrieval")
    parser.add_argument("--config", default="")
    parser.add_argument("--root", default="", help="Seed graph root")
    parser.add_argument("--url", default="")
    parser.add_argument("--collection", default="")
    parser.add_argument("--model", default="")
    parser.add_argument("--query", required=True)
    parser.add_argument("--top-k", type=int, default=0)
    parser.add_argument("--hops", type=int, default=1)
    parser.add_argument("--edge", action="append", default=[])
    parser.add_argument("--node-class", action="append", default=[])
    parser.add_argument("--tag", action="append", default=[])
    parser.add_argument("--snapshot", default="")
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
    hops = args.hops
    snapshot = args.snapshot or ""
    edge_types = set(args.edge or retrieval_cfg.get("edge_types", []))

    if not root or not collection:
        raise SystemExit("--root and --collection are required (or provide config.yaml)")

    from qdrant_client import QdrantClient
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(model_name)
    query_vec = model.encode(args.query, normalize_embeddings=True)

    client = QdrantClient(url=url)
    q_filter = build_filter(args.node_class, args.tag, snapshot)
    results = client.search(
        collection_name=collection,
        query_vector=query_vec.tolist(),
        limit=top_k,
        query_filter=q_filter,
        with_payload=True,
    )

    seeds = []
    for res in results:
        payload = res.payload or {}
        node_id = payload.get("node_id")
        if node_id:
            seeds.append(node_id)

    nodes = load_nodes(Path(root))
    graph = build_graph(nodes)
    expanded = graph_expand(graph, seeds, hops, edge_types)

    print("Vector hits:")
    for res in results:
        payload = res.payload or {}
        print(f"{res.score:.4f} | {payload.get('title')} | {payload.get('node_id')}")

    print("\nGraph-expanded context:")
    for node_id in sorted(expanded):
        title = graph.nodes[node_id].get("title")
        print(f"- {title} ({node_id})")


if __name__ == "__main__":
    main()
