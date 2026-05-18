Ontology Validation Rules — Phase 1

Goal: Detect structural problems early and enforce semantic consistency.

Node-level rules
1) Required metadata present: type, id, title, city, status, tags, source_confidence, created.
2) id uniqueness across the graph.
3) type must be in the approved class list.
4) status must be one of active/planned/illustrative/hypothesized.
5) source_confidence must be low/medium/high.

Edge-level rules
6) Edge type must be in the approved taxonomy.
7) Source and target classes must be valid for the edge type.
8) No self-loop edges except CONNECTS_TO and OVERLAPS_WITH.

Graph-level rules
9) Orphan detection: any node with zero relations is flagged, except Funding Mechanism and Policy (allowed only if tagged status/illustrative).
10) Governance cycles: OWNS/REGULATED_BY edges must not form cycles longer than 1 edge.
11) Zone containment: Congestion Zone and Flooding Zone must have LOCATED_IN -> Urban Region.
12) Asset containment: Asset must have LOCATED_IN -> Urban Region; OVERLAPS_WITH -> Corridor where applicable.
13) Transit Service must have OPERATED_BY -> Operator and DEPENDS_ON -> Corridor or Asset.
14) Sensor System must MONITOR at least one Asset, Corridor, or Zone.
15) Funding Mechanism must FUNDS at least one Policy, Asset, Operator, or Maintenance Event.
16) Infrastructure Failure must AFFECT or CAUSE at least one Asset, Corridor, or Zone.

Consistency checks
17) If node is tagged class/agency, it must have at least one OWNS, MAINTAINS, REGULATES, or FUNDS edge.
18) If node is class/operator, it must OPERATE at least one Transit Service.
19) If node is class/policy, it must REGULATE or CONSTRAIN at least one node.
20) If node is class/maintenance_event, it must DEPENDS_ON an Asset or Corridor.

Implementation notes
- Parse YAML and body relation lines into a normalized edge list.
- Validate edges using a class-to-edge compatibility map.
- Emit a report with: node_id, issue_type, suggested fix.
