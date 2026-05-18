import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import yaml

FRONTMATTER_RE = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n", re.S)
RELATION_LINE_RE = re.compile(r"^\s*-\s*([A-Z_]+)\s*->\s*\[\[([^\]]+)\]\]\s*$")


@dataclass
class Relation:
    edge_type: str
    target: str


@dataclass
class Node:
    file_path: str
    meta: Dict[str, Any]
    body: str
    summary: str
    relations: List[Relation]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    meta = yaml.safe_load(match.group(1)) or {}
    body = text[match.end():]
    return meta, body


def extract_summary(body: str) -> str:
    for line in body.splitlines():
        if line.strip().lower().startswith("summary:"):
            return line.split(":", 1)[1].strip()
    for line in body.splitlines():
        if line.strip():
            return line.strip()
    return ""


def extract_relations(body: str) -> List[Relation]:
    relations: List[Relation] = []
    in_rel = False
    for line in body.splitlines():
        line_strip = line.strip()
        if line_strip.lower() == "relations:":
            in_rel = True
            continue
        if in_rel:
            if not line_strip:
                in_rel = False
                continue
            if line_strip.endswith(":") and not line_strip.startswith("-"):
                in_rel = False
                continue
            match = RELATION_LINE_RE.match(line)
            if match:
                relations.append(Relation(edge_type=match.group(1), target=match.group(2)))
    return relations


def strip_relation_block(body: str) -> str:
    lines = []
    in_rel = False
    for line in body.splitlines():
        line_strip = line.strip()
        if line_strip.lower() == "relations:":
            in_rel = True
            continue
        if in_rel:
            if not line_strip:
                in_rel = False
                continue
            if line_strip.endswith(":") and not line_strip.startswith("-"):
                in_rel = False
                lines.append(line)
                continue
            if RELATION_LINE_RE.match(line):
                continue
            continue
        lines.append(line)
    content = "\n".join([line for line in lines if line.strip()])
    return content


def load_nodes(root: Path) -> List[Node]:
    nodes: List[Node] = []
    for path in root.rglob("*.md"):
        if path.name.lower() == "readme.md":
            continue
        text = read_text(path)
        meta, body = parse_frontmatter(text)
        summary = extract_summary(body)
        relations = extract_relations(body)
        nodes.append(Node(file_path=str(path), meta=meta, body=body, summary=summary, relations=relations))
    return nodes


def serialize_node_text(node: Node) -> str:
    meta = node.meta
    title = str(meta.get("title", "")).strip()
    node_class = str(meta.get("node_class", "")).strip()
    tags = meta.get("tags") or []
    tags_text = ", ".join(tags) if isinstance(tags, list) else str(tags)
    geo = meta.get("geo") or {}
    geo_text = ""
    if isinstance(geo, dict):
        lat = geo.get("lat")
        lon = geo.get("lon")
        if lat is not None or lon is not None:
            geo_text = f"Geo: lat={lat}, lon={lon}"
    rel_text = "; ".join([f"{r.edge_type} {r.target}" for r in node.relations])
    content_text = strip_relation_block(node.body)

    parts: List[str] = []
    if title:
        parts.append(f"Title: {title}")
    if node_class:
        parts.append(f"Class: {node_class}")
    if tags_text:
        parts.append(f"Tags: {tags_text}")
    if geo_text:
        parts.append(geo_text)
    if node.summary:
        parts.append(f"Summary: {node.summary}")
    if rel_text:
        parts.append(f"Relations: {rel_text}")
    if content_text:
        parts.append("Content:")
        parts.append(content_text)
    return "\n".join(parts)


def iter_relations(nodes: Iterable[Node]) -> Iterable[Tuple[str, str, str]]:
    for node in nodes:
        source_id = str(node.meta.get("id", "")).strip()
        for rel in node.relations:
            yield source_id, rel.edge_type, rel.target
