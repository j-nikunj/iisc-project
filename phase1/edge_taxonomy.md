Edge Taxonomy — Phase 1

Objective: Define edge semantics, direction, cardinality, traversal and GraphRAG importance.

Format: Edge | Meaning | Direction | Cardinality | Traversal Importance | GraphRAG Importance | Example

OWNS | Legal or administrative ownership of an asset or corridor | Agency/Stakeholder -> Asset/Corridor/SensorSystem | 1:N | High for governance chains | High for policy impact reasoning | [[BBMP]] OWNS [[Outer Ring Road]]

OPERATES | Runs a service or asset operationally | Operator -> Transit Service/Asset | 1:N | High for service queries | High for operator constraints | [[BMTC]] OPERATES [[BMTC 500D ORR]]

MAINTAINS | Responsible for upkeep | Agency/Operator -> Asset/Corridor/Maintenance Event | 1:N | High for lifecycle analysis | High for maintenance queries | [[BBMP]] MAINTAINS [[Silk Board Underpass]]

CONNECTS_TO | Physical or functional connectivity | Corridor/Asset/Urban Region -> Corridor/Urban Region | N:N (bidirectional) | Medium for network traversal | Medium for multimodal queries | [[Outer Ring Road]] CONNECTS_TO [[Hosur Road]]

CAUSES | Direct causal influence on a symptom or zone | Failure/Policy/Pattern -> Congestion Zone/Flooding Zone/Failure | 1:N | High for causal chains | High for root cause prompts | [[ORR Drainage Overload]] CAUSES [[ORR-Bellandur Flooding Zone]]

CORRELATES_WITH | Statistical association without proven causality | Pattern/Zone/Failure <-> Pattern/Zone | N:N (bidirectional) | Medium | Medium for hypothesis generation | [[Peak-hour IT Commute]] CORRELATES_WITH [[Silk Board Congestion Zone]]

DEPENDS_ON | Operational dependency | Transit Service/Operator/Maintenance Event -> Corridor/Asset/Funding | N:N | High | High for dependency reasoning | [[Namma Metro Purple Line]] DEPENDS_ON [[Baiyappanahalli Metro Depot]]

REGULATED_BY | Subject to regulatory or policy oversight | Operator/Transit Service -> Agency/Policy | N:1 | High for governance queries | High for compliance analysis | [[BMTC]] REGULATED_BY [[DULT]]

FUNDED_BY | Financial source or mechanism | Policy/Operator/Asset/Maintenance Event -> Funding Mechanism | N:N | High for finance chains | Medium for feasibility analysis | [[Namma Metro Purple Line]] FUNDED_BY [[Multilateral Loan - Metro]]

LOCATED_IN | Spatial containment | Asset/Corridor/Zone -> Urban Region | N:1 | Medium for spatial queries | Medium for region-based retrieval | [[Silk Board Junction]] LOCATED_IN [[South Bengaluru Region]]

IMPACTS | Socioeconomic or operational impact | Policy/Failure/Zone -> Stakeholder/Pattern | N:N | High | High for stakeholder analysis | [[Silk Board Congestion Zone]] IMPACTS [[IT Corridor Commuters]]

MONITORS | Monitoring coverage by sensors | Sensor System -> Asset/Zone/Corridor/Pattern | 1:N | Medium | Medium for data availability queries | [[Silk Board CCTV Cluster]] MONITORS [[Silk Board Congestion Zone]]

SERVES | Service coverage | Transit Service -> Urban Region/Stakeholder/Asset | N:N | High for service mapping | High for multimodal integration | [[BMTC 500D ORR]] SERVES [[ORR IT Corridor Region]]

OVERLAPS_WITH | Spatial overlap of zones, corridors, or assets | Zone/Corridor/Asset <-> Zone/Corridor/Asset | N:N (bidirectional) | Medium | Low to medium | [[Silk Board Congestion Zone]] OVERLAPS_WITH [[Silk Board Underpass Flooding Zone]]

CONSTRAINS | Operational or policy constraint | Policy/Failure/Maintenance Event -> Transit Service/Operator/Corridor | N:N | Medium to high | Medium for operational reasoning | [[Storm Drain Desilting - Pre Monsoon]] CONSTRAINS [[BMTC 500D ORR]]
