import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models

from semantic_utils import coalesce, load_yaml_config


def iter_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Qdrant index for seed graph nodes")
    parser.add_argument("--config", default="")
    parser.add_argument("--embeddings", required=True, help="Path to embeddings.jsonl")
    parser.add_argument("--url", default="")
    parser.add_argument("--collection", default="")
    parser.add_argument("--distance", default="")
    parser.add_argument("--recreate", action="store_true")
    args = parser.parse_args()

    config = load_yaml_config(args.config)
    qdrant_cfg = config.get("qdrant", {})
    url = coalesce(args.url, qdrant_cfg.get("url"), "http://localhost:6333")
    collection = coalesce(args.collection, qdrant_cfg.get("collection"))
    distance = coalesce(args.distance, qdrant_cfg.get("distance"), "cosine")
    if not collection:
        raise SystemExit("--collection is required (or provide config.yaml)")

    embeddings_path = Path(args.embeddings)
    rows = list(iter_jsonl(embeddings_path))
    if not rows:
        raise SystemExit("No embeddings found.")

    vector_size = len(rows[0]["vector"])
    client = QdrantClient(url=url)

    if args.recreate:
        client.recreate_collection(
            collection_name=collection,
            vectors_config=qdrant_models.VectorParams(
                size=vector_size,
                distance=getattr(qdrant_models.Distance, str(distance).upper()),
            ),
        )
    else:
        if collection not in [c.name for c in client.get_collections().collections]:
            client.create_collection(
                collection_name=collection,
                vectors_config=qdrant_models.VectorParams(
                    size=vector_size,
                    distance=getattr(qdrant_models.Distance, str(distance).upper()),
                ),
            )

    points = []
    for idx, row in enumerate(rows):
        points.append(
            qdrant_models.PointStruct(
                id=idx,
                vector=row["vector"],
                payload={
                    "node_id": row["node_id"],
                    **row["payload"],
                },
            )
        )

    client.upsert(collection_name=collection, points=points)
    print(f"Upserted {len(points)} points into {collection}")


if __name__ == "__main__":
    main()
