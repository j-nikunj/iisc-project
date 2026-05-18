import argparse
import json
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx
import yaml
from networkx.readwrite import json_graph

EDGE_TYPES = {
    "OWNS",
    "OPERATES",
    "MAINTAINS",
    "CONNECTS_TO",
    "CAUSES",
    "CORRELATES_WITH",
    "DEPENDS_ON",
    "REGULATED_BY",
    "FUNDED_BY",
    "LOCATED_IN",
    "IMPACTS",
    "MONITORS",
    "SERVES",
    "OVERLAPS_WITH",
    "CONSTRAINS",
}

SEVERITIES = {"ERROR", "WARNING", "INFO"}
DEFAULT_SEVERITY_BY_TYPE = {
    "missing_frontmatter": "ERROR",
    "frontmatter_parse_error": "ERROR",
    "missing_required_field": "ERROR",
    "missing_node_id": "ERROR",
    "duplicate_node_id": "ERROR",
    "invalid_node_class": "ERROR",
    "invalid_edge_type": "ERROR",
    "unresolved_wikilink": "WARNING",
    "duplicate_title": "WARNING",
    "duplicate_alias": "WARNING",
    "semantic_edge_violation": "ERROR",
    "cardinality_violation": "WARNING",
}

DEFAULT_REMEDIATION_BY_TYPE = {
    "missing_frontmatter": "Add a YAML frontmatter block to the node file.",
    "frontmatter_parse_error": "Fix YAML syntax in frontmatter.",
    "missing_required_field": "Populate the required frontmatter field.",
    "missing_node_id": "Add a unique id to the node frontmatter.",
    "duplicate_node_id": "Ensure node ids are unique across the repository.",
    "invalid_node_class": "Use a node_class from the allowed ontology.",
    "invalid_edge_type": "Use an edge type from the taxonomy.",
    "unresolved_wikilink": "Fix the wikilink or add the missing node.",
    "duplicate_title": "Ensure node titles are unique.",
    "duplicate_alias": "Ensure aliases are unique or remove duplicates.",
    "semantic_edge_violation": "Fix source/target classes or update compatibility rules.",
    "cardinality_violation": "Add missing relations to satisfy ontology constraints.",
}

ALLOWED_NODE_CLASSES = {
    "corridor",
    "asset",
    "agency",
    "operator",
    "policy",
    "infrastructure_failure",
    "mobility_pattern",
    "transit_service",
    "sensor_system",
    "maintenance_event",
    "congestion_zone",
    "flooding_zone",
    "stakeholder",
    "funding_mechanism",
    "urban_region",
}

REQUIRED_FIELDS = {
    "type",
    "node_class",
    "id",
    "title",
    "city",
    "status",
    "tags",
    "source_confidence",
    "created",
    "updated",
    "geo",
}

EDGE_COMPATIBILITY = {
    "OWNS": {"sources": {"agency", "stakeholder"}, "targets": {"asset", "corridor", "sensor_system"}},
    "OPERATES": {"sources": {"operator"}, "targets": {"transit_service", "asset"}},
    "MAINTAINS": {"sources": {"agency", "operator"}, "targets": {"asset", "corridor", "maintenance_event"}},
    "CONNECTS_TO": {"sources": {"corridor", "urban_region"}, "targets": {"corridor", "urban_region"}},
    "CAUSES": {
        "sources": {"infrastructure_failure", "policy", "mobility_pattern"},
        "targets": {"congestion_zone", "flooding_zone", "infrastructure_failure"},
    },
    "CORRELATES_WITH": {
        "sources": {"mobility_pattern", "congestion_zone", "flooding_zone", "infrastructure_failure"},
        "targets": {"mobility_pattern", "congestion_zone", "flooding_zone", "infrastructure_failure"},
    },
    "DEPENDS_ON": {
        "sources": {"transit_service", "operator", "maintenance_event", "mobility_pattern"},
        "targets": {"corridor", "asset", "transit_service", "funding_mechanism"},
    },
    "REGULATED_BY": {
        "sources": {"operator", "transit_service", "policy"},
        "targets": {"agency", "policy"},
    },
    "FUNDED_BY": {
        "sources": {"policy", "operator", "asset", "maintenance_event", "transit_service"},
        "targets": {"funding_mechanism"},
    },
    "LOCATED_IN": {
        "sources": {"asset", "corridor", "congestion_zone", "flooding_zone", "sensor_system", "urban_region"},
        "targets": {"urban_region"},
    },
    "IMPACTS": {
        "sources": {"policy", "infrastructure_failure", "congestion_zone", "flooding_zone", "mobility_pattern"},
        "targets": {"stakeholder", "mobility_pattern", "corridor"},
    },
    "MONITORS": {
        "sources": {"sensor_system"},
        "targets": {"asset", "corridor", "congestion_zone", "flooding_zone", "mobility_pattern"},
    },
    "SERVES": {
        "sources": {"transit_service"},
        "targets": {"urban_region", "stakeholder", "asset"},
    },
    "OVERLAPS_WITH": {
        "sources": {"corridor", "asset", "congestion_zone", "flooding_zone", "urban_region"},
        "targets": {"corridor", "asset", "congestion_zone", "flooding_zone", "urban_region"},
    },
    "CONSTRAINS": {
        "sources": {"policy", "infrastructure_failure", "maintenance_event"},
        "targets": {"transit_service", "operator", "corridor", "asset"},
    },
}

SELF_LOOP_ALLOWED = {"CONNECTS_TO", "OVERLAPS_WITH", "CORRELATES_WITH"}

CARDINALITY_RULES = [
    {
        "name": "corridor_has_transit_dependency",
        "node_class": "corridor",
        "direction": "incoming",
        "edge_type": "DEPENDS_ON",
        "other_classes": {"transit_service"},
        "min": 1,
        "severity": "WARNING",
        "requires_any_tags": {"transit/served"},
        "message": "Corridor should be referenced by at least one Transit Service.",
        "remediation": "Add DEPENDS_ON edges from transit services using the corridor.",
    },
    {
        "name": "asset_has_maintainer",
        "node_class": "asset",
        "direction": "incoming",
        "edge_type": "MAINTAINS",
        "other_classes": {"agency", "operator"},
        "min": 1,
        "severity": "WARNING",
        "message": "Asset should have at least one maintainer.",
        "remediation": "Add MAINTAINS edges from responsible agencies or operators.",
    },
    {
        "name": "transit_service_has_operator",
        "node_class": "transit_service",
        "direction": "incoming",
        "edge_type": "OPERATES",
        "other_classes": {"operator"},
        "min": 1,
        "severity": "WARNING",
        "message": "Transit service should be operated by at least one operator.",
        "remediation": "Add OPERATES edges from the responsible operator.",
    },
    {
        "name": "congestion_zone_overlaps_corridor",
        "node_class": "congestion_zone",
        "direction": "outgoing",
        "edge_type": "OVERLAPS_WITH",
        "other_classes": {"corridor"},
        "min": 1,
        "severity": "WARNING",
        "message": "Congestion zone should overlap at least one corridor.",
        "remediation": "Add OVERLAPS_WITH edges to affected corridors.",
    },
    {
        "name": "policy_has_constraint",
        "node_class": "policy",
        "direction": "outgoing",
        "edge_type": "CONSTRAINS",
        "other_classes": {"corridor", "asset", "operator", "transit_service"},
        "min": 1,
        "severity": "WARNING",
        "message": "Policy should constrain at least one entity.",
        "remediation": "Add CONSTRAINS edges to affected entities.",
    },
]

RELATION_LINE_RE = re.compile(r"^\s*-\s*([A-Z_]+)\s*->\s*\[\[([^\]]+)\]\]\s*$")
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


@dataclass
class NodeRecord:
    file_path: str
    meta: Dict[str, Any]
    body: str
    parse_errors: List[str]


@dataclass
class EdgeRecord:
    source_id: str
    target_id: Optional[str]
    edge_type: str
    raw_target: str
    source_file: str
    source_section: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> Tuple[Dict[str, Any], str, List[str]]:
    errors: List[str] = []
    fm_re = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n", re.S)
    match = fm_re.match(text)
    if not match:
        errors.append("missing_frontmatter")
        return {}, text, errors
    front = match.group(1)
    body = text[match.end():]
    try:
        meta = yaml.safe_load(front) or {}
    except Exception as exc:
        errors.append(f"frontmatter_parse_error: {exc}")
        meta = {}
    return meta, body, errors


def add_issue(
    issues: List[Dict[str, Any]],
    issue_type: str,
    severity: str,
    remediation: str,
    **details: Any,
) -> None:
    issues.append(
        {
            "type": issue_type,
            "severity": severity,
            "remediation": remediation,
            **details,
        }
    )


def normalize_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str):
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            try:
                parsed = yaml.safe_load(value)
                if isinstance(parsed, list):
                    return [str(v).strip() for v in parsed if str(v).strip()]
            except Exception:
                pass
        return [v.strip() for v in value.split(",") if v.strip()]
    return [str(value).strip()]


def extract_relations(body: str) -> List[Tuple[str, str]]:
    relations: List[Tuple[str, str]] = []
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
                relations.append((match.group(1), match.group(2)))
    return relations


def extract_relationships_from_meta(meta: Dict[str, Any]) -> List[Tuple[str, str]]:
    rels: List[Tuple[str, str]] = []
    candidates = meta.get("relationships") or meta.get("relations")
    if not candidates:
        return rels
    if isinstance(candidates, list):
        for item in candidates:
            if isinstance(item, dict):
                edge_type = str(item.get("type", "")).strip()
                target = str(item.get("target", "")).strip()
                if edge_type and target:
                    rels.append((edge_type, target))
            elif isinstance(item, str):
                match = RELATION_LINE_RE.match(f"- {item}")
                if match:
                    rels.append((match.group(1), match.group(2)))
    return rels


def extract_wikilinks(body: str) -> List[str]:
    return [m.group(1).strip() for m in WIKILINK_RE.finditer(body)]


def normalize_title_key(title: str) -> str:
    return title.strip()


def build_title_index(nodes: List[NodeRecord]) -> Tuple[Dict[str, str], Dict[str, str], List[Dict[str, Any]]]:
    title_to_id: Dict[str, str] = {}
    alias_to_id: Dict[str, str] = {}
    issues: List[Dict[str, Any]] = []

    for node in nodes:
        if node.parse_errors:
            for err in node.parse_errors:
                issues.append({"type": err, "file": node.file_path})
        meta = node.meta
        node_id = str(meta.get("id", "")).strip()
        title = str(meta.get("title", "")).strip()
        if title:
            key = normalize_title_key(title)
            if key in title_to_id and title_to_id[key] != node_id:
                issues.append({"type": "duplicate_title", "title": title, "node_id": node_id})
            title_to_id[key] = node_id

        aliases = normalize_list(meta.get("aliases"))
        for alias in aliases:
            alias_key = normalize_title_key(alias)
            if alias_key in alias_to_id and alias_to_id[alias_key] != node_id:
                issues.append({"type": "duplicate_alias", "alias": alias, "node_id": node_id})
            alias_to_id[alias_key] = node_id

        file_stem = Path(node.file_path).stem
        if file_stem and file_stem not in title_to_id:
            title_to_id[file_stem] = node_id

    return title_to_id, alias_to_id, issues


def validate_required_fields(meta: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    for field in sorted(REQUIRED_FIELDS):
        if field not in meta or meta.get(field) in (None, ""):
            issues.append({"type": "missing_required_field", "field": field})
    return issues


def validate_node_class(meta: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    node_class = str(meta.get("node_class", "")).strip()
    if node_class and node_class not in ALLOWED_NODE_CLASSES:
        return {"type": "invalid_node_class", "node_class": node_class}
    return None


def validate_edge_type(edge_type: str) -> Optional[Dict[str, Any]]:
    if edge_type not in EDGE_TYPES:
        return {"type": "invalid_edge_type", "edge_type": edge_type}
    return None


def validate_semantic_edges(
    graph: nx.MultiDiGraph,
    edges: List[EdgeRecord],
) -> Tuple[List[Dict[str, Any]], set[Tuple[str, str, str]]]:
    issues: List[Dict[str, Any]] = []
    invalid_edge_keys: set[Tuple[str, str, str]] = set()

    for edge in edges:
        if not edge.target_id:
            continue
        source_class = graph.nodes[edge.source_id].get("node_class")
        target_class = graph.nodes[edge.target_id].get("node_class")

        compat = EDGE_COMPATIBILITY.get(edge.edge_type)
        if not compat:
            continue

        violation = False
        if not source_class or not target_class:
            add_issue(
                issues,
                "semantic_edge_violation",
                "ERROR",
                "Ensure node_class is present on both source and target nodes.",
                source_id=edge.source_id,
                target_id=edge.target_id,
                edge_type=edge.edge_type,
                reason="missing_node_class",
            )
            violation = True
        else:
            if source_class not in compat["sources"]:
                add_issue(
                    issues,
                    "semantic_edge_violation",
                    "ERROR",
                    "Change edge direction or update ontology compatibility.",
                    source_id=edge.source_id,
                    target_id=edge.target_id,
                    edge_type=edge.edge_type,
                    source_class=source_class,
                    target_class=target_class,
                    reason="invalid_source_class",
                )
                violation = True
            if target_class not in compat["targets"]:
                add_issue(
                    issues,
                    "semantic_edge_violation",
                    "ERROR",
                    "Change edge direction or update ontology compatibility.",
                    source_id=edge.source_id,
                    target_id=edge.target_id,
                    edge_type=edge.edge_type,
                    source_class=source_class,
                    target_class=target_class,
                    reason="invalid_target_class",
                )
                violation = True

        if edge.source_id == edge.target_id and edge.edge_type not in SELF_LOOP_ALLOWED:
            add_issue(
                issues,
                "semantic_edge_violation",
                "ERROR",
                "Remove self-loop or change edge type to an allowed self-loop edge.",
                source_id=edge.source_id,
                target_id=edge.target_id,
                edge_type=edge.edge_type,
                reason="disallowed_self_loop",
            )
            violation = True

        if violation:
            invalid_edge_keys.add((edge.source_id, edge.target_id, edge.edge_type))

    return issues, invalid_edge_keys


def validate_cardinality(
    graph: nx.MultiDiGraph,
    invalid_edge_keys: set[Tuple[str, str, str]],
) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []

    for rule in CARDINALITY_RULES:
        node_class = rule["node_class"]
        direction = rule["direction"]
        edge_type = rule["edge_type"]
        other_classes = rule.get("other_classes") or set()
        min_count = rule.get("min", 0)
        max_count = rule.get("max")

        for node_id, data in graph.nodes(data=True):
            if data.get("node_class") != node_class:
                continue

            required_tags = set(rule.get("requires_any_tags") or [])
            if required_tags:
                node_tags = set(normalize_list(data.get("tags")))
                if not node_tags.intersection(required_tags):
                    continue

            count = 0
            if direction == "outgoing":
                edges_iter = graph.out_edges(node_id, data=True)
                for _, target_id, edge_data in edges_iter:
                    key = (node_id, target_id, edge_data.get("edge_type"))
                    if key in invalid_edge_keys:
                        continue
                    if edge_data.get("edge_type") != edge_type:
                        continue
                    target_class = graph.nodes[target_id].get("node_class")
                    if other_classes and target_class not in other_classes:
                        continue
                    count += 1
            else:
                edges_iter = graph.in_edges(node_id, data=True)
                for source_id, _, edge_data in edges_iter:
                    key = (source_id, node_id, edge_data.get("edge_type"))
                    if key in invalid_edge_keys:
                        continue
                    if edge_data.get("edge_type") != edge_type:
                        continue
                    source_class = graph.nodes[source_id].get("node_class")
                    if other_classes and source_class not in other_classes:
                        continue
                    count += 1

            violation = False
            if min_count is not None and count < min_count:
                violation = True
                expected = f">= {min_count}"
            elif max_count is not None and count > max_count:
                violation = True
                expected = f"<= {max_count}"
            else:
                expected = None

            if violation:
                add_issue(
                    issues,
                    "cardinality_violation",
                    rule.get("severity", "WARNING"),
                    rule.get("remediation", "Review ontology and add missing relations."),
                    rule_name=rule.get("name"),
                    node_id=node_id,
                    edge_type=edge_type,
                    direction=direction,
                    expected=expected,
                    actual=count,
                    message=rule.get("message"),
                )

    return issues


def build_graph(nodes: List[NodeRecord]) -> Tuple[nx.MultiDiGraph, List[EdgeRecord], List[Dict[str, Any]]]:
    title_to_id, alias_to_id, index_issues = build_title_index(nodes)
    issues: List[Dict[str, Any]] = []
    issues.extend(index_issues)

    graph = nx.MultiDiGraph()
    edges: List[EdgeRecord] = []

    id_seen: Dict[str, str] = {}

    for node in nodes:
        meta = node.meta
        node_id = str(meta.get("id", "")).strip()
        if not node_id:
            issues.append({"type": "missing_node_id", "file": node.file_path})
            continue
        if node_id in id_seen:
            issues.append({"type": "duplicate_node_id", "node_id": node_id, "file": node.file_path})
        id_seen[node_id] = node.file_path

        node_issue = validate_node_class(meta)
        if node_issue:
            node_issue.update({"node_id": node_id})
            issues.append(node_issue)

        missing_fields = validate_required_fields(meta)
        for missing in missing_fields:
            missing.update({"node_id": node_id})
            issues.append(missing)

        tags = normalize_list(meta.get("tags"))
        meta["tags"] = tags
        aliases = normalize_list(meta.get("aliases"))
        meta["aliases"] = aliases

        graph.add_node(node_id, **meta, file_path=node.file_path)

    for node in nodes:
        meta = node.meta
        node_id = str(meta.get("id", "")).strip()
        if not node_id:
            continue
        rels = extract_relations(node.body)
        rels.extend(extract_relationships_from_meta(meta))

        for edge_type, raw_target in rels:
            edge_type = edge_type.strip()
            raw_target = raw_target.strip()
            edge_issue = validate_edge_type(edge_type)
            if edge_issue:
                edge_issue.update({"node_id": node_id, "raw_target": raw_target})
                issues.append(edge_issue)
                continue

            target_id = title_to_id.get(raw_target) or alias_to_id.get(raw_target)
            if not target_id:
                issues.append({
                    "type": "unresolved_wikilink",
                    "node_id": node_id,
                    "raw_target": raw_target,
                    "edge_type": edge_type,
                })
            edges.append(
                EdgeRecord(
                    source_id=node_id,
                    target_id=target_id,
                    edge_type=edge_type,
                    raw_target=raw_target,
                    source_file=node.file_path,
                    source_section="relations",
                )
            )
            if target_id:
                graph.add_edge(node_id, target_id, edge_type=edge_type, raw_target=raw_target)

        for link in extract_wikilinks(node.body):
            if link in title_to_id or link in alias_to_id:
                continue
            issues.append({
                "type": "unresolved_wikilink",
                "node_id": node_id,
                "raw_target": link,
                "edge_type": None,
            })

    return graph, edges, issues


def compute_metrics(graph: nx.MultiDiGraph) -> Dict[str, Any]:
    metrics: Dict[str, Any] = {}
    metrics["node_count"] = graph.number_of_nodes()
    metrics["edge_count"] = graph.number_of_edges()

    node_class_dist = Counter(nx.get_node_attributes(graph, "node_class").values())
    metrics["node_class_distribution"] = dict(node_class_dist)

    edge_types = Counter([data.get("edge_type") for _, _, data in graph.edges(data=True)])
    metrics["edge_type_distribution"] = dict(edge_types)

    undirected = graph.to_undirected()
    metrics["connected_components"] = [
        {"size": len(comp), "nodes": list(comp)}
        for comp in nx.connected_components(undirected)
    ]

    orphan_nodes = [n for n in graph.nodes if graph.degree(n) == 0]
    metrics["orphan_nodes"] = orphan_nodes

    if graph.number_of_nodes() > 0:
        degree_centrality = nx.degree_centrality(undirected)
        betweenness = nx.betweenness_centrality(undirected)
        metrics["top_degree_centrality"] = sorted(
            degree_centrality.items(), key=lambda kv: kv[1], reverse=True
        )[:10]
        metrics["top_betweenness_centrality"] = sorted(
            betweenness.items(), key=lambda kv: kv[1], reverse=True
        )[:10]
    else:
        metrics["top_degree_centrality"] = []
        metrics["top_betweenness_centrality"] = []

    return metrics


def compute_semantic_metrics(
    graph: nx.MultiDiGraph,
    issues: List[Dict[str, Any]],
    invalid_edge_keys: set[Tuple[str, str, str]],
) -> Dict[str, Any]:
    metrics: Dict[str, Any] = {}
    metrics["semantic_invalid_edge_count"] = len(invalid_edge_keys)
    metrics["cardinality_failure_count"] = sum(
        1 for issue in issues if issue.get("type") == "cardinality_violation"
    )
    metrics["unsupported_edge_pattern_count"] = sum(
        1 for issue in issues if issue.get("type") == "semantic_edge_violation"
    )
    metrics["governance_loop_count"] = len(detect_governance_cycles(graph))

    orphan_semantic = set(graph.nodes())
    for source_id, target_id, data in graph.edges(data=True):
        key = (source_id, target_id, data.get("edge_type"))
        if key in invalid_edge_keys:
            continue
        orphan_semantic.discard(source_id)
        orphan_semantic.discard(target_id)
    metrics["orphan_semantic_entities"] = sorted(orphan_semantic)

    metrics["unresolved_infrastructure_dependencies"] = sum(
        1
        for issue in issues
        if issue.get("type") == "cardinality_violation"
        and issue.get("rule_name") == "asset_has_maintainer"
    )
    return metrics


def detect_governance_cycles(graph: nx.MultiDiGraph) -> List[List[str]]:
    gov_edges = [(u, v) for u, v, data in graph.edges(data=True) if data.get("edge_type") in {"OWNS", "REGULATED_BY"}]
    gov_graph = nx.DiGraph()
    gov_graph.add_edges_from(gov_edges)
    cycles = [cycle for cycle in nx.simple_cycles(gov_graph) if len(cycle) > 1]
    return cycles


def build_reports(
    graph: nx.MultiDiGraph,
    edges: List[EdgeRecord],
    issues: List[Dict[str, Any]],
    invalid_edge_keys: set[Tuple[str, str, str]],
) -> Dict[str, Any]:
    validation = defaultdict(list)
    for issue in issues:
        issue_type = issue.get("type", "unknown")
        severity = issue.get("severity") or DEFAULT_SEVERITY_BY_TYPE.get(issue_type, "WARNING")
        if severity not in SEVERITIES:
            severity = "WARNING"
        issue["severity"] = severity
        if not issue.get("remediation"):
            issue["remediation"] = DEFAULT_REMEDIATION_BY_TYPE.get(
                issue_type, "Review node and ontology definitions."
            )
        validation[issue_type].append(issue)

    cycles = detect_governance_cycles(graph)
    if cycles:
        validation["governance_cycles"].append(
            {
                "type": "governance_cycles",
                "severity": "WARNING",
                "remediation": "Break ownership/regulation cycles in governance edges.",
                "cycles": cycles,
            }
        )

    severity_counts = Counter(
        issue.get("severity")
        for issue_list in validation.values()
        for issue in issue_list
        if issue.get("severity")
    )

    return {
        "issues": dict(validation),
        "issue_count": sum(len(v) for v in validation.values()),
        "severity_counts": dict(severity_counts),
        "semantic_invalid_edge_count": len(invalid_edge_keys),
    }


def write_outputs(
    graph: nx.MultiDiGraph,
    edges: List[EdgeRecord],
    validation: Dict[str, Any],
    metrics: Dict[str, Any],
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    nodes_out = []
    for node_id, data in graph.nodes(data=True):
        record = {"id": node_id}
        record.update(data)
        nodes_out.append(record)

    edges_out = [
        {
            "source": edge.source_id,
            "target": edge.target_id,
            "edge_type": edge.edge_type,
            "raw_target": edge.raw_target,
            "source_file": edge.source_file,
            "source_section": edge.source_section,
        }
        for edge in edges
    ]

    graph_out = json_graph.node_link_data(graph)

    def json_default(obj: Any) -> str:
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return str(obj)

    (output_dir / "nodes.json").write_text(
        json.dumps(nodes_out, indent=2, default=json_default), encoding="utf-8"
    )
    (output_dir / "edges.json").write_text(
        json.dumps(edges_out, indent=2, default=json_default), encoding="utf-8"
    )
    (output_dir / "graph.json").write_text(
        json.dumps(graph_out, indent=2, default=json_default), encoding="utf-8"
    )
    (output_dir / "validation_report.json").write_text(
        json.dumps(validation, indent=2, default=json_default), encoding="utf-8"
    )
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2, default=json_default), encoding="utf-8"
    )


def write_summary_report(
    graph: nx.MultiDiGraph,
    metrics: Dict[str, Any],
    validation: Dict[str, Any],
    report_path: Path,
) -> None:
    lines: List[str] = []
    lines.append("Bengaluru Seed Graph — Summary Report")
    lines.append("")
    lines.append(f"Nodes: {metrics.get('node_count', 0)}")
    lines.append(f"Edges: {metrics.get('edge_count', 0)}")
    lines.append("")

    lines.append("Node Class Distribution:")
    for node_class, count in metrics.get("node_class_distribution", {}).items():
        lines.append(f"- {node_class}: {count}")
    lines.append("")

    lines.append("Validation Issues:")
    issue_count = validation.get("issue_count", 0)
    lines.append(f"- Total issues: {issue_count}")
    severity_counts = validation.get("severity_counts", {})
    if severity_counts:
        lines.append(f"- Severity counts: {severity_counts}")
    for issue_type, items in validation.get("issues", {}).items():
        lines.append(f"- {issue_type}: {len(items)}")
    lines.append("")

    lines.append("Semantic Metrics:")
    lines.append(
        f"- semantic_invalid_edge_count: {metrics.get('semantic_invalid_edge_count', 0)}"
    )
    lines.append(
        f"- cardinality_failure_count: {metrics.get('cardinality_failure_count', 0)}"
    )
    lines.append(
        f"- unsupported_edge_pattern_count: {metrics.get('unsupported_edge_pattern_count', 0)}"
    )
    lines.append(
        f"- governance_loop_count: {metrics.get('governance_loop_count', 0)}"
    )
    lines.append("")

    lines.append("Top Degree Centrality:")
    for node_id, score in metrics.get("top_degree_centrality", []):
        title = graph.nodes[node_id].get("title", node_id)
        lines.append(f"- {title} ({node_id}): {score:.3f}")
    lines.append("")

    lines.append("Top Betweenness Centrality:")
    for node_id, score in metrics.get("top_betweenness_centrality", []):
        title = graph.nodes[node_id].get("title", node_id)
        lines.append(f"- {title} ({node_id}): {score:.3f}")
    lines.append("")

    lines.append("Disconnected Components:")
    for comp in metrics.get("connected_components", []):
        if comp.get("size", 0) > 1:
            lines.append(f"- size {comp['size']}: {comp['nodes']}")
    lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")


def load_nodes(root: Path) -> List[NodeRecord]:
    nodes: List[NodeRecord] = []
    for path in root.rglob("*.md"):
        if path.name.lower() == "readme.md":
            continue
        text = read_text(path)
        meta, body, errors = parse_frontmatter(text)
        nodes.append(NodeRecord(file_path=str(path), meta=meta, body=body, parse_errors=errors))
    return nodes


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse Bengaluru seed graph into NetworkX")
    parser.add_argument("--root", required=True, help="Path to seed_graph/bengaluru")
    parser.add_argument("--output", required=True, help="Output directory for JSON files")
    parser.add_argument("--reports", required=True, help="Output directory for report files")
    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists():
        raise SystemExit(f"Root path does not exist: {root}")

    nodes = load_nodes(root)
    graph, edges, issues = build_graph(nodes)
    semantic_issues, invalid_edge_keys = validate_semantic_edges(graph, edges)
    cardinality_issues = validate_cardinality(graph, invalid_edge_keys)
    issues.extend(semantic_issues)
    issues.extend(cardinality_issues)

    metrics = compute_metrics(graph)
    metrics.update(compute_semantic_metrics(graph, issues, invalid_edge_keys))
    validation = build_reports(graph, edges, issues, invalid_edge_keys)

    output_dir = Path(args.output)
    reports_dir = Path(args.reports)
    reports_dir.mkdir(parents=True, exist_ok=True)

    write_outputs(graph, edges, validation, metrics, output_dir)
    write_summary_report(graph, metrics, validation, reports_dir / "summary_report.md")


if __name__ == "__main__":
    main()
