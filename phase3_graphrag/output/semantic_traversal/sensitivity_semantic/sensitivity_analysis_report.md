GraphRAG Sensitivity Analysis Report

Query: multimodal transfer bottlenecks near Silk Board junction

Experiments:
| Name | top_k | hops | edge_filter | overlap_ratio | semantic_signal | node_class_diversity | relation_diversity | context_words | noise_amplification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| k4_h1_all | 4 | 1 | all | 0.00 | 0.27 | 11 | 8 | 193 | 2.75 |
| k8_h1_all | 8 | 1 | all | 0.00 | 0.44 | 11 | 6 | 232 | 1.25 |
| k16_h1_all | 16 | 1 | all | 0.00 | 0.50 | 12 | 6 | 410 | 1.00 |
| k8_h2_all | 8 | 2 | all | 0.00 | 0.22 | 13 | 7 | 456 | 3.50 |
| k16_h2_all | 16 | 2 | all | 0.00 | 0.36 | 13 | 9 | 545 | 1.81 |
| k8_h1_operational | 8 | 1 | operational | 0.00 | 0.73 | 8 | 3 | 159 | 0.38 |
| k8_h1_maintenance_overlap | 8 | 1 | maintenance_overlap | 0.00 | 0.57 | 9 | 2 | 186 | 0.75 |
| k8_h1_transit_corridor | 8 | 1 | all | 0.00 | 0.29 | 9 | 5 | 382 | 2.50 |

Key observations:
- best alignment configs: k8_h1_operational, k8_h1_maintenance_overlap, k16_h1_all
- highest noise configs: k8_h2_all, k4_h1_all, k8_h1_transit_corridor
- edge filter stats:
  - all: overlap 0.00, semantic 0.35, noise 2.14, rel_div 6.83
  - operational: overlap 0.00, semantic 0.73, noise 0.38, rel_div 3.00
  - maintenance_overlap: overlap 0.00, semantic 0.57, noise 0.75, rel_div 2.00

Multi-hop effects:
- k8_h1_all -> k8_h2_all: overlap +0.00, semantic -0.22, rel_div +1.00, noise +2.25
- k16_h1_all -> k16_h2_all: overlap +0.00, semantic -0.14, rel_div +3.00, noise +0.81