GraphRAG Sensitivity Analysis Report

Query: multimodal transfer bottlenecks near Silk Board junction

Experiments:
| Name | top_k | hops | edge_filter | overlap_ratio | semantic_signal | node_class_diversity | relation_diversity | context_words | noise_amplification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| k4_h1_all | 4 | 1 | all | 0.00 | 0.31 | 8 | 5 | 163 | 2.25 |
| k8_h1_all | 8 | 1 | all | 0.00 | 0.47 | 11 | 5 | 221 | 1.12 |
| k16_h1_all | 16 | 1 | all | 0.00 | 0.52 | 12 | 5 | 397 | 0.94 |
| k8_h2_all | 8 | 2 | all | 0.00 | 0.25 | 13 | 6 | 410 | 3.00 |
| k16_h2_all | 16 | 2 | all | 0.00 | 0.39 | 13 | 6 | 525 | 1.56 |
| k8_h1_operational | 8 | 1 | operational | 0.00 | 0.73 | 8 | 3 | 159 | 0.38 |
| k8_h1_maintenance_overlap | 8 | 1 | maintenance_overlap | 0.00 | 0.57 | 9 | 2 | 186 | 0.75 |
| k8_h1_transit_corridor | 8 | 1 | all | 0.00 | 0.28 | 9 | 4 | 393 | 2.62 |

Key observations:
- best alignment configs: k8_h1_operational, k8_h1_maintenance_overlap, k16_h1_all
- highest noise configs: k8_h2_all, k8_h1_transit_corridor, k4_h1_all
- edge filter stats:
  - all: overlap 0.00, semantic 0.37, noise 1.92, rel_div 5.17
  - operational: overlap 0.00, semantic 0.73, noise 0.38, rel_div 3.00
  - maintenance_overlap: overlap 0.00, semantic 0.57, noise 0.75, rel_div 2.00

Multi-hop effects:
- k8_h1_all -> k8_h2_all: overlap +0.00, semantic -0.22, rel_div +1.00, noise +1.88
- k16_h1_all -> k16_h2_all: overlap +0.00, semantic -0.13, rel_div +1.00, noise +0.62

Architectural interpretation:
- Overlap remains weak because vector hits and expansion nodes rarely intersect; this indicates the graph adjacency around retrieved nodes is not semantically anchored in the embedding space.
- The dominant edge set (OVERLAPS_WITH/MAINTAINS/DEPENDS_ON/IMPACTS/CONSTRAINS) expands into generic governance/service nodes more often than query-specific semantic neighborhoods.
- Multi-hop traversal increases breadth without improving overlap, suggesting expansion strategy and bridge relations are the primary constraints rather than top-k alone.
- Node-class filters can sharpen semantic signal but also reduce overlap if graph-side classes lack semantic anchors in the vector index.