from pathlib import Path
import json
import networkx as nx


OUTPUT_DIR = Path(__file__).resolve().parent / "output"

OUTPUT_DIR.mkdir(exist_ok=True)


class GraphExporter:
    def __init__(self, graph):
        self.graph = graph

    def export_graph_json(self):
        print("\nExporting graph to JSON...\n")

        graph_data = nx.node_link_data(self.graph)

        output_path = OUTPUT_DIR / "semantic_transport_graph.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(graph_data, f, indent=2)

        print(f"[DONE] JSON graph exported:")
        print(output_path)

    def export_graph_gml(self):
        print("\nExporting graph to GML...\n")

        output_path = OUTPUT_DIR / "semantic_transport_graph.gml"

        nx.write_gml(self.graph, output_path)

        print(f"[DONE] GML graph exported:")
        print(output_path)

    def inspect_node_distribution(self):
        print("\nInspecting node class distribution...\n")

        distribution = {}

        for _, data in self.graph.nodes(data=True):
            node_class = data.get("node_class", "unknown")

            distribution[node_class] = (
                distribution.get(node_class, 0) + 1
            )

        print("\nNODE CLASS DISTRIBUTION")

        for node_class, count in distribution.items():
            print(f"{node_class}: {count}")

    def inspect_relation_distribution(self):
        print("\nInspecting relation distribution...\n")

        distribution = {}

        for _, _, data in self.graph.edges(data=True):
            relation = data.get("relation", "unknown")

            distribution[relation] = (
                distribution.get(relation, 0) + 1
            )

        print("\nRELATION DISTRIBUTION")

        for relation, count in distribution.items():
            print(f"{relation}: {count}")

    def run(self):
        print("\n" + "=" * 80)
        print("GRAPH EXPORT AND INSPECTION")
        print("=" * 80)

        self.inspect_node_distribution()

        self.inspect_relation_distribution()

        self.export_graph_json()

        self.export_graph_gml()

        print("\nGraph export completed.\n")