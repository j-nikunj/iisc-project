from pathlib import Path
import json


OUTPUT_DIR = Path(__file__).resolve().parent / "output"

OUTPUT_DIR.mkdir(exist_ok=True)


class SemanticSerializer:
    def __init__(self, graph):
        self.graph = graph

        self.semantic_documents = []

    def serialize_node(self, node_id, data):
        node_class = data.get("node_class", "unknown")

        semantic_role = data.get(
            "semantic_role",
            "operational_entity"
        )

        text_parts = [
            f"Node ID: {node_id}",
            f"Node class: {node_class}",
            f"Semantic role: {semantic_role}"
        ]

        for key, value in data.items():

            if key in [
                "node_class",
                "semantic_role"
            ]:
                continue

            if value is None:
                continue

            if value == "":
                continue

            text_parts.append(f"{key}: {value}")

        connected_relations = []

        for _, target, edge_data in self.graph.out_edges(
            node_id,
            data=True
        ):
            relation = edge_data.get("relation")

            if relation:
                connected_relations.append(
                    f"{relation} -> {target}"
                )

        if connected_relations:
            text_parts.append(
                "Operational relations: "
                + "; ".join(connected_relations[:10])
            )

        semantic_text = ". ".join(text_parts)

        return {
            "id": node_id,
            "node_class": node_class,
            "semantic_text": semantic_text
        }

    def serialize_graph(self):
        print("\nSerializing semantic graph context...\n")

        for node_id, data in self.graph.nodes(data=True):

            document = self.serialize_node(
                node_id,
                data
            )

            self.semantic_documents.append(document)

        print(
            f"[DONE] Serialized "
            f"{len(self.semantic_documents)} semantic documents."
        )

    def export_semantic_documents(self):
        print("\nExporting semantic documents...\n")

        output_path = (
            OUTPUT_DIR
            / "semantic_documents.json"
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                self.semantic_documents,
                f,
                indent=2,
                ensure_ascii=False
            )

        print(f"[DONE] Semantic documents exported:")
        print(output_path)

    def inspect_samples(self):
        print("\nSAMPLE SEMANTIC DOCUMENTS\n")

        for document in self.semantic_documents[:3]:
            print("=" * 80)
            print(document["semantic_text"])

    def run(self):
        print("\n" + "=" * 80)
        print("SEMANTIC SERIALIZATION")
        print("=" * 80)

        self.serialize_graph()

        self.inspect_samples()

        self.export_semantic_documents()

        print("\nSemantic serialization completed.\n")