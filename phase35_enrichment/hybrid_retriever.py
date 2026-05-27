from pathlib import Path
import networkx as nx
import json

from semantic_retriever import (
    SemanticRetriever
)

from neighborhood_expander import (
    NeighborhoodExpander
)

from context_assembler import (
    ContextAssembler
)

from context_chain_builder import (
    ContextChainBuilder
)


PROJECT_ROOT = Path(__file__).resolve().parent

OUTPUT_DIR = PROJECT_ROOT / "output"

GRAPH_PATH = (
    OUTPUT_DIR
    / "semantic_transport_graph.gml"
)


class HybridGraphRetriever:
    def __init__(
        self,
        top_k=3,
        max_hops=1
    ):
        self.top_k = top_k

        self.max_hops = max_hops

        self.graph = None

        self.semantic_retriever = (
            SemanticRetriever(
                top_k=self.top_k
            )
        )

    def load_graph(self):
        print("\nLoading graph...\n")

        self.graph = nx.read_gml(
            GRAPH_PATH
        )

        print(
            f"[DONE] Graph loaded with "
            f"{self.graph.number_of_nodes()} nodes "
            f"and "
            f"{self.graph.number_of_edges()} edges."
        )

    def retrieve_seed_nodes(
        self,
        query
    ):
        print("\nRunning semantic retrieval...\n")

        results = (
            self.semantic_retriever
            .semantic_search(query)
        )

        seed_nodes = []

        for result in results:
            payload = result.payload

            node_id = payload.get(
                "node_id"
            )

            if node_id:
                seed_nodes.append(node_id)

        print(
            f"[DONE] Retrieved "
            f"{len(seed_nodes)} seed nodes."
        )

        return seed_nodes

    def expand_context(
        self,
        seed_nodes
    ):
        expander = NeighborhoodExpander(
            self.graph
        )

        full_context = {}

        for seed_node in seed_nodes:
            print(
                f"\nExpanding context for: "
                f"{seed_node}"
            )

            context = (
                expander.expand_operational_context(
                    seed_node,
                    max_hops=self.max_hops
                )
            )

            for node_info in context:
                node_id = node_info["node_id"]
                if node_id not in full_context:
                    full_context[node_id] = node_info

        assembler = ContextAssembler(
            max_context_nodes=10
        )

        assembled_context = (
            assembler.assemble_context(
                list(full_context.values())
            )
        )

        return assembled_context

    def print_final_context(
        self,
        context
    ):
        assembler = ContextAssembler()

        assembler.print_assembled_context(
            context
        )

    def run(
        self,
        query
    ):
        # Guard condition to prevent redundant graph loading
        if getattr(self, 'graph', None) is None or len(self.graph.nodes) == 0:
            self.load_graph()

        raw_seed_ids = (
            self.retrieve_seed_nodes(
                query
            )
        )

        context = self.expand_context(
            raw_seed_ids
        )

        self.print_final_context(
            context
        )

        # Normalize seed nodes to ensure they have full metadata for chain building
        seed_nodes_with_metadata = []
        for node_id in raw_seed_ids:
            if node_id in self.graph.nodes:
                node_data = self.graph.nodes[node_id]
                seed_nodes_with_metadata.append({
                    "node_id": node_id,
                    "node_class": node_data.get("node_class"),
                    "semantic_role": node_data.get("semantic_role"),
                    "description": node_data.get("description", ""),
                    "traversal_score": 1.0  # Seed nodes start with max score
                })

        chain_builder = ContextChainBuilder(self.graph)
        
        all_chains = []
        for seed_node_obj in seed_nodes_with_metadata:
            chains = chain_builder.build_chains(seed_node_obj['node_id'], context)
            all_chains.extend(chains)
        
        # Sort all chains from all seed nodes by score
        sorted_chains = sorted(all_chains, key=lambda x: x['chain_score'], reverse=True)

        self._print_operational_chains(sorted_chains)

        # Export the final payload to JSON
        output_filepath = OUTPUT_DIR / "graphrag_payload.json"
        self.export_reasoning_payload(
            query,
            seed_nodes_with_metadata,
            context,
            sorted_chains,
            output_filepath
        )

    def _print_operational_chains(self, chains):
        print("\n" + "=" * 80)
        print("OPERATIONAL REASONING CHAINS")
        print("=" * 80)

        if not chains:
            print("\nNo operational chains were assembled.")
            return

        for i, chain_info in enumerate(chains[:5]): # Print top 5 chains
            print("\n" + "-" * 80)
            print(f"Chain {i+1} | Score: {chain_info['chain_score']}\n")
            
            path_str = []
            for node_context in chain_info['path']:
                node_id = node_context.get('node_id', 'N/A')
                # Fallback to graph to get node_class if it's missing from the context dict
                node_class = node_context.get('node_class') or self.graph.nodes.get(node_id, {}).get('node_class', 'N/A')
                path_str.append(f"{node_class} ({node_id})")

            print(" → ".join(path_str))


    def export_reasoning_payload(self, query, seed_nodes, context, reasoning_chains, filepath):
        """
        Serializes the complete GraphRAG reasoning context to a JSON file.
        """
        print(f"\nExporting reasoning payload to: {filepath}")

        payload = {
            "query": query,
            "seed_nodes": seed_nodes,
            "neighborhood_context": context,
            "causal_chains": reasoning_chains
        }

        try:
            with open(filepath, 'w') as f:
                json.dump(payload, f, indent=4)
            print(f"[DONE] Successfully saved payload.")
        except (IOError, TypeError) as e:
            print(f"[ERROR] Failed to export payload: {e}")


def main():
    # This main function is now for standalone testing.
    # The primary execution is handled by the evaluation/evaluator.py script.
    print("--- Running HybridGraphRetriever in Standalone Mode ---")
    test_query = (
        "Analyze cascading flooding risks across the ORR corridor."
    )

    retriever = HybridGraphRetriever(
        top_k=3,
        max_hops=2
    )

    retriever.run(test_query)


if __name__ == "__main__":
    main()