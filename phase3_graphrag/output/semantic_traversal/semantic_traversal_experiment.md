GraphRAG Semantic Traversal Experiment

Average delta (semantic - baseline):
- semantic_signal_ratio: +0.0000
- semantic_coherence_proxy: +0.0000
- context_density: +0.0000
- noise_amplification: +0.0000
- relation_diversity: +0.1429
- node_class_diversity: +0.0000
- operational_edge_ratio: +0.0159
- generic_expansion_ratio: +0.0000
- continuity_proxy: +0.0000

Sensitivity summary:
- baseline best alignment: k8_h1_operational, k8_h1_maintenance_overlap, k16_h1_all
- semantic best alignment: k8_h1_operational, k8_h1_maintenance_overlap, k16_h1_all
- baseline highest noise: k8_h2_all, k4_h1_all, k8_h1_transit_corridor
- semantic highest noise: k8_h2_all, k4_h1_all, k8_h1_transit_corridor

Per-query deltas:
| Category | d_semantic_signal | d_coherence | d_density | d_noise | d_rel_div | d_operational | d_generic_ratio | d_continuity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| flooding and drainage | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +1.0000 | +0.1111 | +0.0000 | +0.0000 |
| multimodal transport | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| weak infrastructure maintenance | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| commuter impact | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| policy/governance | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| public transport dependency | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| sensor/monitoring systems | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |