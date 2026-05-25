class OperationalSemanticEnrichment:
    def __init__(self, graph):
        self.graph = graph

    def inject_flooding_zones(self):
        flooding_nodes = [
            {
                "id": "flood-zone-orr-bellandur",
                "name": "ORR Bellandur Flooding Zone",
                "node_class": "flooding_zone",
                "semantic_role": (
                    "mobility_disruption_region"
                ),
                "description": (
                    "Flood-prone operational corridor "
                    "causing multimodal slowdown "
                    "and accessibility degradation."
                )
            },
            {
                "id": "flood-zone-koramangala",
                "name": (
                    "Koramangala Drainage Stress Region"
                ),
                "node_class": "flooding_zone",
                "semantic_role": (
                    "mobility_disruption_region"
                ),
                "description": (
                    "Urban flooding region linked "
                    "to operational mobility stress."
                )
            }
        ]

        for node in flooding_nodes:
            self.graph.add_node(
                node["id"],
                **node
            )

    def inject_congestion_corridors(self):
        congestion_nodes = [
            {
                "id": "congestion-silk-board",
                "name": (
                    "Silk Board Congestion Corridor"
                ),
                "node_class": (
                    "congestion_corridor"
                ),
                "semantic_role": (
                    "traffic_stress_region"
                ),
                "description": (
                    "Persistent multimodal "
                    "traffic congestion corridor "
                    "with spillback propagation."
                )
            },
            {
                "id": "congestion-marathahalli",
                "name": (
                    "Marathahalli Operational "
                    "Bottleneck"
                ),
                "node_class": (
                    "congestion_corridor"
                ),
                "semantic_role": (
                    "traffic_stress_region"
                ),
                "description": (
                    "Operational corridor with "
                    "high transfer delay and "
                    "mobility slowdown."
                )
            }
        ]

        for node in congestion_nodes:
            self.graph.add_node(
                node["id"],
                **node
            )

    def inject_spillback_failures(self):
        spillback_nodes = [
            {
                "id": "spillback-silk-board",
                "name": (
                    "Silk Board Spillback Failure"
                ),
                "node_class": (
                    "spillback_failure_zone"
                ),
                "semantic_role": (
                    "congestion_propagation_region"
                ),
                "description": (
                    "Traffic spillback region "
                    "causing upstream operational "
                    "congestion propagation."
                )
            }
        ]

        for node in spillback_nodes:
            self.graph.add_node(
                node["id"],
                **node
            )

    def connect_semantic_relations(self):
        semantic_edges = [
            (
                "flood-zone-orr-bellandur",
                "congestion-silk-board",
                "OVERLAPS_WITH"
            ),
            (
                "spillback-silk-board",
                "congestion-silk-board",
                "PROPAGATES_TO"
            ),
            (
                "flood-zone-koramangala",
                "congestion-marathahalli",
                "IMPACTS"
            ),
            (
                "congestion-silk-board",
                "spillback-silk-board",
                "CREATES_TRANSFER_STRESS"
            )
        ]

        for source, target, relation in (
            semantic_edges
        ):
            self.graph.add_edge(
                source,
                target,
                relation=relation,
                semantic_role=(
                    "operational_semantic_bridge"
                )
            )

    def summarize_enrichment(self):
        print("\n" + "=" * 80)
        print("OPERATIONAL SEMANTIC ENRICHMENT")
        print("=" * 80)

        print(
            f"Nodes after enrichment: "
            f"{self.graph.number_of_nodes()}"
        )

        print(
            f"Edges after enrichment: "
            f"{self.graph.number_of_edges()}"
        )

        print("\nEnrichment completed.\n")

    def run(self):
        self.inject_flooding_zones()

        self.inject_congestion_corridors()

        self.inject_spillback_failures()

        self.connect_semantic_relations()

        self.summarize_enrichment()