GraphRAG Bridge Insertion Experiment

Bridges inserted:
- cctv_to_underpass_flooding: sensor-silk-board-cctv -> zone-silk-board-underpass-flooding (MONITORS)
- spillback_to_underpass_flooding: failure-silk-board-spillback -> zone-silk-board-underpass-flooding (CAUSES)
- peak_hour_to_hebbal_congestion: pattern-peak-hour-it-commute -> zone-hebbal-congestion (CORRELATES_WITH)
- two_wheeler_to_hebbal_congestion: pattern-two-wheeler-last-mile -> zone-hebbal-congestion (CORRELATES_WITH)

Average delta (experiment - baseline):
- semantic_signal_ratio: -0.0033
- semantic_coherence_proxy: -0.0033
- relation_diversity: +0.1429
- node_class_diversity: +0.0000
- context_growth_rate: +0.0179
- noise_amplification: +0.0179
- generic_expansion_change: +0.0000

Bridge usage counts (paths):
- cctv_to_underpass_flooding: 1
- spillback_to_underpass_flooding: 1
- peak_hour_to_hebbal_congestion: 3
- two_wheeler_to_hebbal_congestion: 0

Sensitivity summary:
- baseline best alignment: k8_h1_operational, k8_h1_maintenance_overlap, k16_h1_all
- experiment best alignment: k8_h1_operational, k8_h1_maintenance_overlap, k16_h1_all
- baseline highest noise: k8_h2_all, k4_h1_all, k8_h1_transit_corridor
- experiment highest noise: k8_h2_all, k4_h1_all, k8_h1_transit_corridor

Per-query deltas:
| Category | d_semantic_signal | d_noise | d_rel_div | d_node_div | d_context_growth | d_generic_expansion | bridge_hits |
| --- | --- | --- | --- | --- | --- | --- | --- |
| flooding and drainage | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | cctv_to_underpass_flooding(1) |
| multimodal transport | -0.0233 | +0.1250 | +0.0000 | +0.0000 | +0.1250 | +0.0000 | peak_hour_to_hebbal_congestion(1) |
| weak infrastructure maintenance | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | n/a |
| commuter impact | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | peak_hour_to_hebbal_congestion(1) |
| policy/governance | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | n/a |
| public transport dependency | +0.0000 | +0.0000 | +1.0000 | +0.0000 | +0.0000 | +0.0000 | spillback_to_underpass_flooding(1), peak_hour_to_hebbal_congestion(1) |
| sensor/monitoring systems | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | n/a |