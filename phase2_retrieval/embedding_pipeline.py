import argparse
import json
from pathlib import Path
from time import perf_counter
from typing import Any, Dict, List

from node_parser import load_nodes, serialize_node_text
from semantic_utils import coalesce, load_yaml_config, resolve_config_path


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
    parser.add_argument("--config", default="")
    parser.add_argument("--root", default="", help="Seed graph root")
    parser.add_argument("--output", default="", help="Output directory")
    parser.add_argument("--model", default="", help="Embedding model name")
    parser.add_argument("--batch-size", type=int, default=0)
    parser.add_argument("--normalize", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    config = load_yaml_config(args.config)
    root = coalesce(args.root, config.get("graph_root"))
    output = coalesce(args.output, config.get("output_dir"))
    root = resolve_config_path(args.config, root)
    output = resolve_config_path(args.config, output)
    embed_cfg = config.get("embedding", {})
    model_name = coalesce(args.model, embed_cfg.get("model_name"), "BAAI/bge-small-en-v1.5")
    batch_size = args.batch_size or embed_cfg.get("batch_size", 64)
    normalize = args.normalize or bool(embed_cfg.get("normalize", False))
    max_length = embed_cfg.get("max_length")

    if not root or not output:
        raise SystemExit("--root and --output are required (or provide config.yaml)")

    root = Path(root)
    output_dir = Path(output)
    output_dir.mkdir(parents=True, exist_ok=True)

    nodes = load_nodes(root)
    records = build_records(nodes)
    write_jsonl(output_dir / "serialized_nodes.jsonl", records)

    if args.dry_run:
        print(f"Serialized {len(records)} nodes (dry run).")
        return

    start = perf_counter()
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(model_name)
    if max_length:
        model.max_seq_length = int(max_length)
    texts = [row["text"] for row in records]
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=normalize,
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
