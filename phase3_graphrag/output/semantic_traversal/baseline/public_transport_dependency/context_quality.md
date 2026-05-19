GraphRAG Context Quality Report

Query: public transport dependency for commuters near Silk Board

Breakdown:
- vector_hits: 8
- graph_expansion: 15
- unique_nodes: 23
- overlap: 0

Node-class distribution (all):
- agency: 1
- asset: 2
- congestion_zone: 4
- mobility_pattern: 3
- corridor: 4
- flooding_zone: 1
- stakeholder: 2
- sensor_system: 1
- maintenance_event: 2
- infrastructure_failure: 1
- transit_service: 2

Edge-type distribution:
- OVERLAPS_WITH: 4
- IMPACTS: 2
- DEPENDS_ON: 5
- CORRELATES_WITH: 2
- MAINTAINS: 1
- MONITORS: 1

Top traversed relations:
- DEPENDS_ON: 5
- OVERLAPS_WITH: 4
- IMPACTS: 2
- CORRELATES_WITH: 2
- MAINTAINS: 1

Expansion depth metrics:
- min: 1
- max: 1
- avg: 1.00

Context size:
- chars: 2538
- words: 288
- lines: 77