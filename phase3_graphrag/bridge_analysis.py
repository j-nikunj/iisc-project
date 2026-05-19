import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from graphrag_utils import build_graph, load_config, resolve_paths
from node_parser import load_nodes  # type: ignore


TOKEN_RE = re.compile(r"[a-z0-9]+")
GENERIC_CLASSES = {"agency", "corridor", "transit_service"}


def tokenize(text: str) -> List[str]:
    return TOKEN_RE.findall(text.lower())


def node_text(node) -> str:
    meta = node.meta
    title = str(meta.get("title", ""))
    tags = meta.get("tags") or []
    if isinstance(tags, list):
        tags_text = " ".join([str(tag) for tag in tags])
    else:
        tags_text = str(tags)
    summary = node.summary or ""
    return " ".join([title, tags_text, summary])


def jaccard(a: Iterable[str], b: Iterable[str]) -> float:
    set_a = set(a)
    set_b = set(b)
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def edge_type_for_pair(
    class_pair_map: Dict[Tuple[str, str], Counter],
    source_class: str,
    target_class: str,
) -> str:
    if (source_class, target_class) in class_pair_map:
        return class_pair_map[(source_class, target_class)].most_common(1)[0][0]
    if (target_class, source_class) in class_pair_map:
        return class_pair_map[(target_class, source_class)].most_common(1)[0][0]

    if source_class == "agency" and target_class in {"asset", "maintenance_event"}:
        return "MAINTAINS"
    if source_class == "maintenance_event" and target_class in {"asset", "corridor"}:
        return "DEPENDS_ON"
    if source_class == "congestion_zone" and target_class in {"asset", "corridor"}:
        return "OVERLAPS_WITH"
    if source_class == "flooding_zone" and target_class in {"asset", "corridor"}:
        return "OVERLAPS_WITH"
    if source_class == "infrastructure_failure" and target_class in {"asset", "corridor"}:
        return "IMPACTS"
    if source_class == "sensor_system" and target_class in {"asset", "corridor"}:
        return "DEPENDS_ON"
    if source_class == "mobility_pattern" and target_class in {"corridor", "transit_service"}:
        return "DEPENDS_ON"
    return "IMPACTS"


def confidence_score(
    similarity: float,
    co_occurrence: int,
    topology_gap: float,
    class_support: float,
    overlap_impact: float,
) -> float:
    co_norm = min(co_occurrence / 3.0, 1.0)
    score = (
        0.35 * similarity
        + 0.2 * co_norm
        + 0.2 * topology_gap
        + 0.15 * class_support
        + 0.1 * overlap_impact
    )
    return round(score, 3)


def shortest_path_gap(graph, source: str, target: str) -> float:
    try:
        length = len(
            __import__("networkx").shortest_path(graph.to_undirected(), source, target)
        ) - 1
    except Exception:
        return 1.0
    if length <= 1:
        return 0.2
    if length == 2:
        return 0.5
    return 1.0


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    config = load_config(str(base_dir / "config.yaml"))
    root, output, _reports = resolve_paths(
        str(base_dir / "config.yaml"),
        config.get("graph_root"),
        config.get("output_dir"),
        None,
    )

    nodes = load_nodes(Path(root))
    graph, _title_index = build_graph(nodes)
    node_map = {node.meta.get("id"): node for node in nodes}

    class_pair_map: Dict[Tuple[str, str], Counter] = defaultdict(Counter)
    for source, target, data in graph.edges(data=True):
        source_class = graph.nodes[source].get("node_class")
        target_class = graph.nodes[target].get("node_class")
        if source_class and target_class:
            class_pair_map[(source_class, target_class)][data.get("edge_type")] += 1

    context_paths = list(Path(output).rglob("context.json"))
    contexts = []
    for path in context_paths:
        try:
            contexts.append((path, json.loads(path.read_text(encoding="utf-8"))))
        except Exception:
            continue

    vector_counts = Counter()
    expansion_counts = Counter()
    co_occurrence = Counter()
    vector_by_context = {}
    expansion_by_context = {}

    for path, ctx in contexts:
        vector_ids = [
            item.get("node_id")
            for item in ctx.get("vector_hits", [])
            if item.get("node_id")
        ]
        expansion_ids = [
            item.get("node_id")
            for item in ctx.get("graph_expansion", [])
            if item.get("node_id")
        ]

        vector_by_context[path] = vector_ids
        expansion_by_context[path] = expansion_ids

        vector_counts.update(vector_ids)
        expansion_counts.update(expansion_ids)

        for v in vector_ids:
            for e in expansion_ids:
                co_occurrence[(v, e)] += 1

    expansion_heavy = [
        node_id
        for node_id, count in expansion_counts.items()
        if count >= 2 and vector_counts.get(node_id, 0) == 0
    ]
    vector_heavy = [
        node_id
        for node_id, count in vector_counts.items()
        if count >= 2
    ]

    low_degree_vectors = []
    for node_id in vector_heavy:
        if node_id not in graph:
            continue
        degree = graph.degree(node_id)
        if degree <= 1:
            low_degree_vectors.append(node_id)

    def build_candidate(
        source_id: str,
        target_id: str,
        co_count: int,
        category: str,
    ) -> Dict[str, Any]:
        if graph.has_edge(source_id, target_id) or graph.has_edge(target_id, source_id):
            return {}

        source_node = node_map.get(source_id)
        target_node = node_map.get(target_id)
        if not source_node or not target_node:
            return {}
        source_class = graph.nodes[source_id].get("node_class") or ""
        target_class = graph.nodes[target_id].get("node_class") or ""

        source_tokens = tokenize(node_text(source_node))
        target_tokens = tokenize(node_text(target_node))
        similarity = jaccard(source_tokens, target_tokens)

        topology_gap = shortest_path_gap(graph, source_id, target_id)
        class_support = 1.0 if (source_class, target_class) in class_pair_map else 0.5
        overlap_impact = 1.0 if source_id in vector_heavy and target_id in expansion_heavy else 0.7

        edge_type = edge_type_for_pair(class_pair_map, source_class, target_class)
        confidence = confidence_score(similarity, co_count, topology_gap, class_support, overlap_impact)

        rationale = "Shared semantic signals (tokens/tags/summary) and repeated co-occurrence across retrievals suggest a missing connective edge."
        expected = "Anchors expansion nodes to vector-retrieved semantics, increasing coherence and reducing generic expansion drift."

        return {
            "source_node": {
                "id": source_id,
                "title": source_node.meta.get("title"),
                "node_class": source_class,
            },
            "target_node": {
                "id": target_id,
                "title": target_node.meta.get("title"),
                "node_class": target_class,
            },
            "suggested_edge_type": edge_type,
            "semantic_similarity": round(similarity, 4),
            "co_occurrence": co_count,
            "semantic_rationale": rationale,
            "expected_effect": expected,
            "confidence": confidence,
            "category": category,
        }

    candidates: Dict[str, List[Dict[str, Any]]] = {
        "high_confidence_structural_gaps": [],
        "possible_semantic_cross_links": [],
        "generic_hub_reductions": [],
        "optional_enrichment": [],
    }

    seen_pairs = set()

    for v in low_degree_vectors:
        for u in vector_heavy:
            if v == u or (v, u) in seen_pairs or (u, v) in seen_pairs:
                continue
            if v not in graph or u not in graph:
                continue
            sim = jaccard(tokenize(node_text(node_map[v])), tokenize(node_text(node_map[u])))
            if sim < 0.35:
                continue
            gap = shortest_path_gap(graph, v, u)
            if gap < 0.5:
                continue
            candidate = build_candidate(v, u, 1, "high_confidence_structural_gaps")
            if candidate:
                candidates["high_confidence_structural_gaps"].append(candidate)
                seen_pairs.add((v, u))

    for (v, e), count in co_occurrence.most_common(200):
        if v not in graph or e not in graph:
            continue
        if (v, e) in seen_pairs or (e, v) in seen_pairs:
            continue
        if count < 2:
            continue
        if e in expansion_heavy:
            category = "generic_hub_reductions" if graph.nodes[e].get("node_class") in GENERIC_CLASSES else "possible_semantic_cross_links"
        else:
            category = "possible_semantic_cross_links"
        candidate = build_candidate(v, e, count, category)
        if candidate:
            candidates[category].append(candidate)
            seen_pairs.add((v, e))

    for v in vector_heavy:
        for e in expansion_heavy:
            if (v, e) in seen_pairs or (e, v) in seen_pairs:
                continue
            if v not in graph or e not in graph:
                continue
            if graph.nodes[e].get("node_class") not in GENERIC_CLASSES:
                continue
            sim = jaccard(tokenize(node_text(node_map[v])), tokenize(node_text(node_map[e])))
            if sim < 0.2:
                continue
            candidate = build_candidate(v, e, 1, "generic_hub_reductions")
            if candidate:
                candidates["generic_hub_reductions"].append(candidate)
                seen_pairs.add((v, e))

    for v in vector_heavy:
        for u in vector_heavy:
            if v == u or (v, u) in seen_pairs or (u, v) in seen_pairs:
                continue
            if v not in graph or u not in graph:
                continue
            sim = jaccard(tokenize(node_text(node_map[v])), tokenize(node_text(node_map[u])))
            if sim < 0.25:
                continue
            gap = shortest_path_gap(graph, v, u)
            if gap < 0.5:
                continue
            candidate = build_candidate(v, u, 1, "optional_enrichment")
            if candidate:
                candidates["optional_enrichment"].append(candidate)
                seen_pairs.add((v, u))

    for key in candidates:
        candidates[key] = sorted(candidates[key], key=lambda item: item["confidence"], reverse=True)[:25]

    summary = {
        "context_files_analyzed": len(contexts),
        "vector_nodes": len(vector_counts),
        "expansion_nodes": len(expansion_counts),
        "expansion_heavy_nodes": len(expansion_heavy),
        "vector_heavy_nodes": len(vector_heavy),
        "low_degree_vector_nodes": len(low_degree_vectors),
        "generic_classes": sorted(list(GENERIC_CLASSES)),
        "overlap_note": "Graph expansion excludes vector hits by design in assemble_context; overlap=0 does not imply missing adjacency.",
    }

    payload = {
        "summary": summary,
        "candidates": candidates,
    }

    output_dir = Path(output)
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "candidate_bridge_relations.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md_lines = []
    md_lines.append("GraphRAG Candidate Bridge Relations")
    md_lines.append("")
    md_lines.append("Summary:")
    md_lines.append(f"- contexts analyzed: {summary['context_files_analyzed']}")
    md_lines.append(f"- vector nodes: {summary['vector_nodes']}")
    md_lines.append(f"- expansion nodes: {summary['expansion_nodes']}")
    md_lines.append(f"- expansion-heavy nodes: {summary['expansion_heavy_nodes']}")
    md_lines.append(f"- vector-heavy nodes: {summary['vector_heavy_nodes']}")
    md_lines.append(f"- low-degree vector nodes: {summary['low_degree_vector_nodes']}")
    md_lines.append(f"- generic classes: {', '.join(summary['generic_classes'])}")
    md_lines.append("")
    md_lines.append(f"Note: {summary['overlap_note']}")

    for section, items in candidates.items():
        md_lines.append("")
        md_lines.append(section.replace("_", " ").title())
        if not items:
            md_lines.append("- none")
            continue
        for item in items:
            source = item["source_node"]
            target = item["target_node"]
            md_lines.append(
                "- {} ({}) -> {} ({}), edge: {}, confidence: {:.2f}".format(
                    source.get("title"),
                    source.get("node_class"),
                    target.get("title"),
                    target.get("node_class"),
                    item.get("suggested_edge_type"),
                    item.get("confidence"),
                )
            )
            md_lines.append(
                "  - rationale: {}".format(item.get("semantic_rationale"))
            )
            md_lines.append(
                "  - expected: {}".format(item.get("expected_effect"))
            )

    md_path = output_dir / "candidate_bridge_relations.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print("Wrote {} and {}".format(json_path, md_path))


if __name__ == "__main__":
    main()
