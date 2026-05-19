import argparse
from pathlib import Path
from typing import Dict, Optional

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import numpy as np

from graphrag_utils import (
    assemble_context,
    build_filter,
    build_graph,
    coalesce,
    graph_expand_with_paths,
    graph_expand_with_paths_semantic,
    load_config,
    resolve_paths,
)

from node_parser import load_nodes, serialize_node_text  # type: ignore


def main() -> None:
    parser = argparse.ArgumentParser(description="GraphRAG retrieval context")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--root", default="")
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
    parser.add_argument("--output", default="")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--semantic-traversal", action="store_true")
    parser.add_argument("--semantic-threshold", type=float, default=None)
    parser.add_argument("--semantic-max-neighbors", type=int, default=None)
    parser.add_argument("--semantic-rerank", action="store_true")
    parser.add_argument("--semantic-no-rerank", action="store_true")
    parser.add_argument("--hub-suppression", action="store_true")
    parser.add_argument("--hub-class", action="append", default=[])
    parser.add_argument("--hub-penalty", type=float, default=None)
    parser.add_argument("--semantic-query-weight", type=float, default=None)
    parser.add_argument("--semantic-seed-weight", type=float, default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    qdrant_cfg = config.get("qdrant", {})
    retrieval_cfg = config.get("retrieval", {})
    context_cfg = config.get("context", {})

    root = coalesce(args.root, config.get("graph_root"))
    output = coalesce(args.output, config.get("output_dir"))
    root, output, _reports = resolve_paths(args.config, root, output, None)

    url = coalesce(args.url, qdrant_cfg.get("url"), "http://localhost:6333")
    collection = coalesce(args.collection, qdrant_cfg.get("collection"))
    model_name = coalesce(args.model, config.get("embedding", {}).get("model_name"), "BAAI/bge-small-en-v1.5")
    top_k = args.top_k or retrieval_cfg.get("top_k", 8)
    hops = args.hops
    edge_types = set(args.edge or retrieval_cfg.get("edge_types", []))
    snapshot = args.snapshot or ""

    semantic_enabled = bool(args.semantic_traversal or retrieval_cfg.get("semantic_traversal", False))
    semantic_threshold = args.semantic_threshold
    if semantic_threshold is None:
        semantic_threshold = float(retrieval_cfg.get("semantic_threshold", 0.0))

    semantic_max_neighbors = args.semantic_max_neighbors
    if semantic_max_neighbors is None:
        semantic_max_neighbors = int(retrieval_cfg.get("semantic_max_neighbors", 0))

    semantic_rerank = bool(retrieval_cfg.get("semantic_rerank", True))
    if args.semantic_rerank:
        semantic_rerank = True
    if args.semantic_no_rerank:
        semantic_rerank = False

    hub_suppression = bool(args.hub_suppression or retrieval_cfg.get("hub_suppression", False))
    hub_classes = set(args.hub_class or retrieval_cfg.get("hub_classes", ["agency", "corridor", "transit_service"]))
    hub_penalty = args.hub_penalty
    if hub_penalty is None:
        hub_penalty = float(retrieval_cfg.get("hub_penalty", 0.15))

    query_weight = args.semantic_query_weight
    if query_weight is None:
        query_weight = float(retrieval_cfg.get("semantic_query_weight", 0.6))

    seed_weight = args.semantic_seed_weight
    if seed_weight is None:
        seed_weight = float(retrieval_cfg.get("semantic_seed_weight", 0.4))

    max_nodes = int(context_cfg.get("max_nodes", 40))
    include_relations = bool(context_cfg.get("include_relations", True))
    include_content = bool(context_cfg.get("include_content", True))

    if not root or not output or not collection:
        raise SystemExit("--root, --output, and --collection are required (or provide config.yaml)")

    nodes = load_nodes(Path(root))
    graph, _title_index = build_graph(nodes)

    if args.dry_run:
        print(f"Dry run OK. Nodes loaded: {len(nodes)}")
        return

    model = SentenceTransformer(model_name)
    query_vec = model.encode(args.query, normalize_embeddings=True)
    client = QdrantClient(url=url)
    q_filter = build_filter(args.node_class, args.tag, snapshot)

    results = client.query_points(
        collection_name=collection,
        query=query_vec.tolist(),
        limit=top_k,
        query_filter=q_filter,
        with_payload=True,
    )
    points = results.points if hasattr(results, "points") else results

    vector_hits = []
    seed_ids = []
    for res in points:
        payload = res.payload or {}
        node_id = payload.get("node_id")
        seed_ids.append(node_id)
        vector_hits.append({
            "node_id": node_id,
            "title": payload.get("title"),
            "node_class": payload.get("node_class"),
            "score": res.score,
        })

    if semantic_enabled:
        node_by_id = {node.meta.get("id"): node for node in nodes}
        embedding_cache: Dict[str, np.ndarray] = {}

        def get_embedding(node_id: str) -> Optional[np.ndarray]:
            if node_id in embedding_cache:
                return embedding_cache[node_id]
            node = node_by_id.get(node_id)
            if not node:
                return None
            text = serialize_node_text(node)
            vec = model.encode(text, normalize_embeddings=True)
            embedding_cache[node_id] = vec
            return vec

        seed_embeddings = {seed_id: get_embedding(seed_id) for seed_id in seed_ids if seed_id}

        def score_neighbor(root_seed: str, _current: str, neighbor: str, _step: Dict[str, str]) -> float:
            neighbor_vec = get_embedding(neighbor)
            if neighbor_vec is None:
                return -1.0
            query_sim = float(np.dot(query_vec, neighbor_vec))
            seed_vec = seed_embeddings.get(root_seed)
            seed_sim = float(np.dot(seed_vec, neighbor_vec)) if seed_vec is not None else 0.0
            score = query_weight * query_sim + seed_weight * seed_sim
            if hub_suppression:
                neighbor_class = graph.nodes[neighbor].get("node_class")
                if neighbor_class in hub_classes:
                    score -= hub_penalty
            return score

        expanded_ids, paths = graph_expand_with_paths_semantic(
            graph=graph,
            seeds=seed_ids,
            hops=hops,
            edge_types=edge_types,
            score_fn=score_neighbor,
            max_neighbors_per_hop=semantic_max_neighbors,
            semantic_threshold=semantic_threshold,
            rerank=semantic_rerank,
        )
    else:
        expanded_ids, paths = graph_expand_with_paths(graph, seed_ids, hops, edge_types)
    context = assemble_context(
        query=args.query,
        graph=graph,
        vector_hits=vector_hits,
        expanded_ids=expanded_ids,
        paths=paths,
        max_nodes=max_nodes,
        include_relations=include_relations,
        include_content=include_content,
    )

    output_dir = Path(output)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "context.json").write_text(
        __import__("json").dumps(context, indent=2),
        encoding="utf-8",
    )
    (output_dir / "context.md").write_text(context["context_text"], encoding="utf-8")
    print(f"Wrote {output_dir / 'context.json'} and context.md")


if __name__ == "__main__":
    main()
