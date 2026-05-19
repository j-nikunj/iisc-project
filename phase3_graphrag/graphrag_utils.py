from __future__ import annotations

import sys
from collections import deque
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx

BASE = Path(__file__).resolve().parent
PHASE2 = BASE.parent / "phase2_retrieval"
if str(PHASE2) not in sys.path:
    sys.path.append(str(PHASE2))

from node_parser import load_nodes  # type: ignore  # noqa: E402
from semantic_utils import coalesce, load_yaml_config, resolve_config_path  # type: ignore  # noqa: E402


def load_config(path: str) -> Dict[str, Any]:
    return load_yaml_config(path)


def resolve_paths(config_path: str, root: Optional[str], output: Optional[str], reports: Optional[str]) -> Tuple[str, str, str]:
    root_resolved = resolve_config_path(config_path, root) if root else ""
    output_resolved = resolve_config_path(config_path, output) if output else ""
    reports_resolved = resolve_config_path(config_path, reports) if reports else ""
    return root_resolved, output_resolved, reports_resolved


def build_graph(nodes) -> Tuple[nx.MultiDiGraph, Dict[str, str]]:
    graph = nx.MultiDiGraph()
    title_to_id: Dict[str, str] = {}
    for node in nodes:
        meta = node.meta
        node_id = meta.get("id")
        title = meta.get("title")
        if title and node_id:
            title_to_id[title] = node_id
        graph.add_node(node_id, **meta)
    for node in nodes:
        source_id = node.meta.get("id")
        for rel in node.relations:
            target_id = title_to_id.get(rel.target)
            if not target_id:
                continue
            graph.add_edge(source_id, target_id, edge_type=rel.edge_type)
    return graph, title_to_id


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


def graph_expand_with_paths(
    graph: nx.MultiDiGraph,
    seeds: List[str],
    hops: int,
    edge_types: Set[str],
) -> Tuple[Set[str], Dict[str, List[Dict[str, str]]]]:
    visited: Set[str] = set()
    paths: Dict[str, List[Dict[str, str]]] = {}

    queue = deque()
    for seed in seeds:
        if seed is None:
            continue
        visited.add(seed)
        paths[seed] = []
        queue.append((seed, 0))

    while queue:
        current, depth = queue.popleft()
        if depth >= hops:
            continue

        for _, target_id, data in graph.out_edges(current, data=True):
            if edge_types and data.get("edge_type") not in edge_types:
                continue
            if target_id not in visited:
                step = {"from": current, "edge": data.get("edge_type"), "to": target_id, "direction": "out"}
                paths[target_id] = paths[current] + [step]
                visited.add(target_id)
                queue.append((target_id, depth + 1))

        for source_id, _, data in graph.in_edges(current, data=True):
            if edge_types and data.get("edge_type") not in edge_types:
                continue
            if source_id not in visited:
                step = {"from": source_id, "edge": data.get("edge_type"), "to": current, "direction": "in"}
                paths[source_id] = paths[current] + [step]
                visited.add(source_id)
                queue.append((source_id, depth + 1))

    return visited, paths


def graph_expand_with_paths_semantic(
    graph: nx.MultiDiGraph,
    seeds: List[str],
    hops: int,
    edge_types: Set[str],
    score_fn,
    max_neighbors_per_hop: int,
    semantic_threshold: float,
    rerank: bool,
) -> Tuple[Set[str], Dict[str, List[Dict[str, str]]]]:
    visited: Set[str] = set()
    paths: Dict[str, List[Dict[str, str]]] = {}

    queue = deque()
    for seed in seeds:
        if seed is None:
            continue
        visited.add(seed)
        paths[seed] = []
        queue.append((seed, 0, seed))

    while queue:
        current, depth, root_seed = queue.popleft()
        if depth >= hops:
            continue

        candidates: List[Tuple[float, str, Dict[str, str]]] = []

        for _, target_id, data in graph.out_edges(current, data=True):
            if edge_types and data.get("edge_type") not in edge_types:
                continue
            if target_id in visited:
                continue
            step = {"from": current, "edge": data.get("edge_type"), "to": target_id, "direction": "out"}
            score = score_fn(root_seed, current, target_id, step)
            if semantic_threshold and score < semantic_threshold:
                continue
            candidates.append((score, target_id, step))

        for source_id, _, data in graph.in_edges(current, data=True):
            if edge_types and data.get("edge_type") not in edge_types:
                continue
            if source_id in visited:
                continue
            step = {"from": source_id, "edge": data.get("edge_type"), "to": current, "direction": "in"}
            score = score_fn(root_seed, current, source_id, step)
            if semantic_threshold and score < semantic_threshold:
                continue
            candidates.append((score, source_id, step))

        if rerank:
            candidates.sort(key=lambda item: item[0], reverse=True)

        if max_neighbors_per_hop and max_neighbors_per_hop > 0:
            candidates = candidates[:max_neighbors_per_hop]

        for _score, node_id, step in candidates:
            if node_id in visited:
                continue
            paths[node_id] = paths[current] + [step]
            visited.add(node_id)
            queue.append((node_id, depth + 1, root_seed))

    return visited, paths


def assemble_context(
    query: str,
    graph: nx.MultiDiGraph,
    vector_hits: List[Dict[str, Any]],
    expanded_ids: Set[str],
    paths: Dict[str, List[Dict[str, str]]],
    max_nodes: int,
    include_relations: bool,
    include_content: bool,
) -> Dict[str, Any]:
    vector_ids = [hit["node_id"] for hit in vector_hits if hit.get("node_id")]
    expanded_only = [node_id for node_id in expanded_ids if node_id not in vector_ids]

    graph_expansion = []
    for node_id in expanded_only:
        meta = graph.nodes[node_id]
        graph_expansion.append({
            "node_id": node_id,
            "title": meta.get("title"),
            "node_class": meta.get("node_class"),
            "path": paths.get(node_id, []),
        })

    def node_block(node_id: str) -> str:
        meta = graph.nodes[node_id]
        title = meta.get("title") or node_id
        node_class = meta.get("node_class")
        summary = meta.get("summary") or meta.get("Summary") or ""
        rels = meta.get("relations")
        parts = [f"## {title}", f"Class: {node_class}"]
        if summary:
            parts.append(f"Summary: {summary}")
        if include_relations and rels:
            parts.append(f"Relations: {rels}")
        if include_content and meta.get("content"):
            parts.append("Content:")
            parts.append(str(meta.get("content")))
        return "\n".join(parts)

    ordered_nodes = vector_ids + expanded_only
    ordered_nodes = ordered_nodes[:max_nodes]
    blocks = [node_block(node_id) for node_id in ordered_nodes if node_id in graph.nodes]

    context_text = "\n\n".join([
        f"Query: {query}",
        "Vector Hits:",
        "\n".join([f"- {hit.get('title')} ({hit.get('node_id')}): {hit.get('score'):.4f}" for hit in vector_hits]),
        "Graph Expansion:",
        "\n".join([f"- {item.get('title')} ({item.get('node_id')})" for item in graph_expansion]),
        "\n".join(blocks),
    ])

    return {
        "query": query,
        "vector_hits": vector_hits,
        "graph_expansion": graph_expansion,
        "context_text": context_text,
    }
