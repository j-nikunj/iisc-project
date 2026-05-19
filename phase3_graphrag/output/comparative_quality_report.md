Comparative GraphRAG Context Quality Report

Queries:
- flooding and drainage: flooding and drainage bottlenecks near Silk Board junction
- multimodal transport: multimodal transfer bottlenecks near Silk Board junction
- weak infrastructure maintenance: weak infrastructure maintenance risks on Outer Ring Road corridor
- commuter impact: commuter impact from corridor disruptions near Silk Board
- policy/governance: policy and governance constraints on corridor upgrades in Bengaluru
- public transport dependency: public transport dependency for commuters near Silk Board
- sensor/monitoring systems: sensor and monitoring systems for traffic and drainage near Silk Board

Per-category metrics:
| Category | overlap_ratio | node_class_diversity | relation_diversity | depth_avg | redundancy | vector_hits | graph_expansion |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multimodal transport | 0.00 | 11 | 5 | 1.00 | 0 | 8 | 9 |
| weak infrastructure maintenance | 0.00 | 10 | 5 | 1.00 | 0 | 8 | 8 |
| policy/governance | 0.00 | 10 | 5 | 1.00 | 0 | 8 | 13 |
| sensor/monitoring systems | 0.00 | 10 | 5 | 1.00 | 0 | 8 | 8 |
| commuter impact | 0.00 | 10 | 4 | 1.00 | 0 | 8 | 10 |
| public transport dependency | 0.00 | 10 | 4 | 1.00 | 0 | 8 | 14 |
| flooding and drainage | 0.00 | 8 | 4 | 1.00 | 0 | 8 | 6 |

Summary:
- strongest categories: multimodal transport, weak infrastructure maintenance
- weakest categories: public transport dependency, flooding and drainage
- graph expansion improves: flooding and drainage, multimodal transport, weak infrastructure maintenance, commuter impact, policy/governance, public transport dependency, sensor/monitoring systems
- graph expansion introduces noise: n/a
- semantic/graph alignment: flooding and drainage, multimodal transport
- semantic/graph divergence: public transport dependency, sensor/monitoring systems

Structural signals:
- weak semantic anchor classes: policy, transit_service
- over-generic node classes: agency, transit_service
- rare relations: n/a
- common relations: OVERLAPS_WITH(22), DEPENDS_ON(16), IMPACTS(13), MAINTAINS(10), CONSTRAINS(7)
- disconnected topology categories: n/a