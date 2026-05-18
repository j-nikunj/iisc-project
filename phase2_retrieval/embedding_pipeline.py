import argparse
import json
from pathlib import Path
from time import perf_counter
from typing import Any, Dict, List

from node_parser import load_nodes, serialize_node_text


def build_records(nodes) -> List[Dict[str, Any]]:
    records = []
    for node in nodes:
        meta = node.meta
        record = {
            "node_id": meta.get("id"),
            "title": meta.get("title"),
            "node_class": meta.get("node_class"),
            "tags": meta.get("tags") or [],
            "city": meta.get("city"),
            "graph_snapshot_version": meta.get("graph_snapshot_version"),
            "text": serialize_node_text(node),
        }
        records.append(record)
    return records


def write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build embeddings for seed graph nodes")
    parser.add_argument("--root", required=True, help="Seed graph root")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--model", default="BAAI/bge-small-en-v1.5", help="Embedding model name")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--normalize", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(args.root)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    nodes = load_nodes(root)
    records = build_records(nodes)
    write_jsonl(output_dir / "serialized_nodes.jsonl", records)

    if args.dry_run:
        print(f"Serialized {len(records)} nodes (dry run).")
        return

    start = perf_counter()
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(args.model)
    texts = [row["text"] for row in records]
    embeddings = model.encode(
        texts,
        batch_size=args.batch_size,
        normalize_embeddings=args.normalize,
        show_progress_bar=True,
    )

    embedded_rows = []
    for row, vector in zip(records, embeddings):
        embedded_rows.append({
            "node_id": row["node_id"],
            "vector": vector.tolist(),
            "payload": {
                "title": row["title"],
                "node_class": row["node_class"],
                "tags": row["tags"],
                "city": row["city"],
                "graph_snapshot_version": row["graph_snapshot_version"],
            },
        })

    write_jsonl(output_dir / "embeddings.jsonl", embedded_rows)
    elapsed = perf_counter() - start
    print(f"Embeddings written: {len(embedded_rows)} in {elapsed:.2f}s")


if __name__ == "__main__":
    main()
