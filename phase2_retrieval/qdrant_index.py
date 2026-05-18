import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models


def iter_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Qdrant index for seed graph nodes")
    parser.add_argument("--embeddings", required=True, help="Path to embeddings.jsonl")
    parser.add_argument("--url", default="http://localhost:6333")
    parser.add_argument("--collection", required=True)
    parser.add_argument("--distance", default="Cosine")
    parser.add_argument("--recreate", action="store_true")
    args = parser.parse_args()

    embeddings_path = Path(args.embeddings)
    rows = list(iter_jsonl(embeddings_path))
    if not rows:
        raise SystemExit("No embeddings found.")

    vector_size = len(rows[0]["vector"])
    client = QdrantClient(url=args.url)

    if args.recreate:
        client.recreate_collection(
            collection_name=args.collection,
            vectors_config=qdrant_models.VectorParams(
                size=vector_size,
                distance=getattr(qdrant_models.Distance, args.distance.upper()),
            ),
        )
    else:
        if args.collection not in [c.name for c in client.get_collections().collections]:
            client.create_collection(
                collection_name=args.collection,
                vectors_config=qdrant_models.VectorParams(
                    size=vector_size,
                    distance=getattr(qdrant_models.Distance, args.distance.upper()),
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

    client.upsert(collection_name=args.collection, points=points)
    print(f"Upserted {len(points)} points into {args.collection}")


if __name__ == "__main__":
    main()
