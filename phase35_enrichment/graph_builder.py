import networkx as nx


class GraphBuilder:
    def __init__(self, normalized_entities):
        self.normalized_entities = normalized_entities

        self.graph = nx.MultiDiGraph()

    def build_nodes(self):
        print("\nBuilding graph nodes...\n")

        for entity_type, entities in self.normalized_entities.items():

            for entity in entities:
                node_id = entity.get("id")

                if not node_id:
                    continue

                self.graph.add_node(
                    node_id,
                    **entity
                )

        print(f"[DONE] Added {self.graph.number_of_nodes()} nodes.")

    def build_route_stop_relations(self):
        print("\nBuilding route-stop operational relations...\n")

        stop_events = self.normalized_entities.get(
            "stop_time_event",
            []
        )

        route_trip_map = {}

        trip_patterns = self.normalized_entities.get(
            "transit_trip_pattern",
            []
        )

        for trip in trip_patterns:
            trip_id = trip.get("id")
            route_id = trip.get("route_id")

            if trip_id and route_id:
                route_trip_map[trip_id] = route_id

        relation_count = 0

        for event in stop_events:
            trip_id = event.get("trip_id")
            stop_id = event.get("stop_id")

            route_id = route_trip_map.get(trip_id)

            if not route_id or not stop_id:
                continue

            self.graph.add_edge(
                route_id,
                stop_id,
                relation="SERVES_STOP",
                semantic_role="operational_connectivity"
            )

            relation_count += 1

        print(f"[DONE] Added {relation_count} route-stop relations.")

    def build_trip_stop_relations(self):
        print("\nBuilding trip-stop temporal relations...\n")

        stop_events = self.normalized_entities.get(
            "stop_time_event",
            []
        )

        relation_count = 0

        for event in stop_events:
            trip_id = event.get("trip_id")
            stop_id = event.get("stop_id")

            if not trip_id or not stop_id:
                continue

            self.graph.add_edge(
                trip_id,
                stop_id,
                relation="VISITS_STOP",
                semantic_role="temporal_operational_transition",
                arrival_time=event.get("arrival_time"),
                departure_time=event.get("departure_time"),
                stop_sequence=event.get("stop_sequence")
            )

            relation_count += 1

        print(f"[DONE] Added {relation_count} trip-stop relations.")

    def summarize_graph(self):
        print("\n" + "=" * 80)
        print("GRAPH SUMMARY")
        print("=" * 80)

        print(f"Nodes: {self.graph.number_of_nodes()}")
        print(f"Edges: {self.graph.number_of_edges()}")

        print("\nSample Nodes:")

        sample_nodes = list(self.graph.nodes(data=True))[:3]

        for node in sample_nodes:
            print(node)

        print("\nSample Edges:")

        sample_edges = list(
            self.graph.edges(data=True)
        )[:5]

        for edge in sample_edges:
            print(edge)

    def run(self):
        print("\n" + "=" * 80)
        print("SEMANTIC GRAPH CONSTRUCTION")
        print("=" * 80)

        self.build_nodes()

        self.build_route_stop_relations()

        self.build_trip_stop_relations()

        self.summarize_graph()

        print("\nSemantic graph construction completed.\n")