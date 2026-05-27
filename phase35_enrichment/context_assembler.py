class ContextAssembler:
    HIGH_PRIORITY_CLASSES = {
        "flooding_zone",
        "spillback_failure_zone",
        "congestion_corridor",
        "interchange_stress_zone",
        "infrastructure_bottleneck"
    }

    def __init__(
        self,
        max_context_nodes=10
    ):
        self.max_context_nodes = (
            max_context_nodes
        )

    def score_node(
        self,
        node
    ):
        score = 0

        node_class = node.get(
            "node_class"
        )

        semantic_role = node.get(
            "semantic_role",
            ""
        )

        if (
            node_class
            in self.HIGH_PRIORITY_CLASSES
        ):
            score += 10

        if (
            "propagation"
            in semantic_role
        ):
            score += 5

        if (
            "stress"
            in semantic_role
        ):
            score += 4

        if (
            "disruption"
            in semantic_role
        ):
            score += 4
        
        score += node.get("traversal_score", 0)

        description = node.get(
            "description",
            ""
        ).lower()

        if "flood" in description:
            score += 3

        if "congestion" in description:
            score += 3

        if "multimodal" in description:
            score += 2

        return score

    def rank_context_nodes(
        self,
        context
    ):
        scored_nodes = []

        for node in context:
            score = self.score_node(
                node
            )

            scored_nodes.append(
                (
                    score,
                    node
                )
            )

        scored_nodes.sort(
            reverse=True,
            key=lambda x: x[0]
        )

        ranked_context = [
            node
            for score, node in scored_nodes
        ]

        return ranked_context

    def prune_context(
        self,
        ranked_context
    ):
        return ranked_context[
            : self.max_context_nodes
        ]

    def assemble_context(
        self,
        context
    ):
        ranked_context = (
            self.rank_context_nodes(
                context
            )
        )

        pruned_context = (
            self.prune_context(
                ranked_context
            )
        )

        return pruned_context

    def print_assembled_context(
        self,
        context
    ):
        print("\n" + "=" * 80)

        print(
            "ASSEMBLED GRAPHRAG CONTEXT"
        )

        print("=" * 80)

        for rank, node in enumerate(
            context,
            start=1
        ):
            print("\n" + "-" * 80)

            print(f"Rank: {rank}")

            print(
                f"Node ID: "
                f"{node['node_id']}"
            )

            print(
                f"Node Class: "
                f"{node['node_class']}"
            )

            print(
                f"Semantic Role: "
                f"{node['semantic_role']}"
            )

            print(
                f"Description: "
                f"{node['description']}"
            )

            print(
                f"Priority Score: "
                f"{self.score_node(node)}"
            )