import argparse
import json
from pathlib import Path
from time import perf_counter

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from graphrag_utils import build_filter, build_graph, coalesce, graph_expand_with_paths, load_config, resolve_paths
from node_parser import load_nodes  # type: ignore


def load_examples(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="GraphRAG evaluation report")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--root", default="")
    parser.add_argument("--url", default="")
    parser.add_argument("--collection", default="")
    parser.add_argument("--model", default="")
    parser.add_argument("--examples", required=True)
    parser.add_argument("--top-k", type=int, default=0)
    parser.add_argument("--hops", type=int, default=1)
    parser.add_argument("--edge", action="append", default=[])
    parser.add_argument("--snapshot", default="")
    parser.add_argument("--output", default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    config = load_config(args.config)
    qdrant_cfg = config.get("qdrant", {})
    retrieval_cfg = config.get("retrieval", {})

    root = coalesce(args.root, config.get("graph_root"))
    _root, _output, reports = resolve_paths(args.config, root, None, config.get("reports_dir"))
    root = _root
    url = coalesce(args.url, qdrant_cfg.get("url"), "http://localhost:6333")
    collection = coalesce(args.collection, qdrant_cfg.get("collection"))
    model_name = coalesce(args.model, config.get("embedding", {}).get("model_name"), "BAAI/bge-small-en-v1.5")
    top_k = args.top_k or retrieval_cfg.get("top_k", 8)
    edge_types = set(args.edge or retrieval_cfg.get("edge_types", []))
    snapshot = args.snapshot or ""

    if not root or not collection:
        raise SystemExit("--root and --collection are required (or provide config.yaml)")

    nodes = load_nodes(Path(root))
    graph, _title_index = build_graph(nodes)

    if args.dry_run:
        print(f"Dry run OK. Nodes loaded: {len(nodes)}")
        return

    model = SentenceTransformer(model_name)
    client = QdrantClient(url=url)
    q_filter = build_filter([], [], snapshot)

    report = []
    examples = load_examples(Path(args.examples))
    for example in examples:
        query = example["query"]
        start = perf_counter()
        query_vec = model.encode(query, normalize_embeddings=True)
        results = client.query_points(
            collection_name=collection,
            query=query_vec.tolist(),
            limit=top_k,
            query_filter=q_filter,
            with_payload=True,
        )
        latency_ms = (perf_counter() - start) * 1000.0
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

        expanded_ids, _paths = graph_expand_with_paths(graph, seed_ids, args.hops, edge_types)
        expanded_titles = {graph.nodes[node_id].get("title") for node_id in expanded_ids}

        expected_titles = set(example.get("expected_nodes", []))
        vector_titles = {hit["title"] for hit in vector_hits if hit.get("title")}
        expected_hits_vector = sorted(expected_titles.intersection(vector_titles))
        expected_hits_expanded = sorted(expected_titles.intersection(expanded_titles))
        expected_count = len(expected_titles) or 1

        report.append({
            "id": example.get("id"),
            "query": query,
            "latency_ms": latency_ms,
            "vector_hits": vector_hits,
            "expected_hits_vector": expected_hits_vector,
            "expected_hits_expanded": expected_hits_expanded,
            "expected_coverage_vector": len(expected_hits_vector) / expected_count,
            "expected_coverage_expanded": len(expected_hits_expanded) / expected_count,
            "notes": example.get("notes", ""),
        })

    reports_dir = Path(reports or Path(args.output).parent)
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = Path(args.output) if args.output else reports_dir / "graphrag_eval.json"
    output_path.write_text(json.dumps({"results": report}, indent=2), encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
