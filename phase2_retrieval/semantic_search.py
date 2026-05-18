import argparse
from typing import Any, List


def build_filter(node_classes: List[str], tags: List[str], snapshot: str) -> Any:
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Semantic similarity search")
    parser.add_argument("--url", default="http://localhost:6333")
    parser.add_argument("--collection", required=True)
    parser.add_argument("--model", default="BAAI/bge-small-en-v1.5")
    parser.add_argument("--query", required=True)
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--node-class", action="append", default=[])
    parser.add_argument("--tag", action="append", default=[])
    parser.add_argument("--snapshot", default="")
    args = parser.parse_args()

    from qdrant_client import QdrantClient
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(args.model)
    query_vec = model.encode(args.query, normalize_embeddings=True)

    client = QdrantClient(url=args.url)
    q_filter = build_filter(args.node_class, args.tag, args.snapshot)

    results = client.search(
        collection_name=args.collection,
        query_vector=query_vec.tolist(),
        limit=args.top_k,
        query_filter=q_filter,
        with_payload=True,
    )

    for res in results:
        payload = res.payload or {}
        print(f"{res.score:.4f} | {payload.get('title')} | {payload.get('node_id')}")


if __name__ == "__main__":
    main()
