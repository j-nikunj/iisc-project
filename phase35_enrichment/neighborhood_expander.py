import networkx as nx


class NeighborhoodExpander:
    HIGH_PRIORITY_RELATIONS = {
        "PROPAGATES_TO",
        "IMPACTS",
        "CREATES_TRANSFER_STRESS"
    }

    MEDIUM_PRIORITY_RELATIONS = {
        "OVERLAPS_WITH",
        "SERVES_STOP",
        "VISITS_STOP"
    }

    def __init__(self, graph):
        self.graph = graph

    def get_neighbors(
        self,
        seed_node,
        max_hops=1
    ):
        visited = set()

        neighborhood = []

        queue = [(seed_node, 0)]

        while queue:
            current_node, depth = queue.pop(0)

            if current_node in visited:
                continue

            visited.add(current_node)

            if depth > max_hops:
                continue

            neighborhood.append(current_node)

            for neighbor in self.graph.neighbors(
                current_node
            ):
                queue.append(
                    (neighbor, depth + 1)
                )

        return neighborhood

    def prioritize_relations(
        self,
        source,
        target
    ):
        edge_data = self.graph.get_edge_data(
            source,
            target
        )

        if not edge_data:
            return "LOW"

        for _, attributes in edge_data.items():
            relation = attributes.get(
                "relation"
            )

            if relation in (
                self.HIGH_PRIORITY_RELATIONS
            ):
                return "HIGH"

            if relation in (
                self.MEDIUM_PRIORITY_RELATIONS
            ):
                return "MEDIUM"

        return "LOW"

    def expand_operational_context(
        self,
        seed_node,
        max_hops=2,
        initial_score=1.0,
        decay_factor=0.5
    ):
        """
        Expands the operational context around a seed node using a weighted BFS.

        - Eliminates duplicate nodes.
        - Propagates a traversal score that decays with distance.
        - Applies relation-aware scoring.
        """
        visited = {}  # Use a dictionary to store the highest score for each visited node
        queue = [(seed_node, initial_score, 0)]  # (node, score, depth)
        visited[seed_node] = initial_score

        CRITICAL_CLASSES = {
            "flood_vulnerability_region",
            "infrastructure_bottleneck",
            "transfer_stress_zone",
            "congestion_corridor",
            "spillback_failure_zone"
        }

        while queue:
            current_node, current_score, depth = queue.pop(0)

            if depth >= max_hops:
                continue

            for neighbor in self.graph.neighbors(current_node):
                relation_priority = self.prioritize_relations(current_node, neighbor)
                
                # Adjust score decay based on relation priority
                if relation_priority == "HIGH":
                    priority_decay = decay_factor * 0.5  # Less decay for high-priority relations
                elif relation_priority == "MEDIUM":
                    priority_decay = decay_factor
                else:
                    priority_decay = decay_factor * 1.5  # More decay for low-priority relations

                new_score = current_score * (1.0 - priority_decay)

                # --- Semantic-Aware Pruning Logic ---
                neighbor_data = self.graph.nodes.get(neighbor, {})
                neighbor_class = neighbor_data.get("node_class")

                # Apply a much lower threshold for critical infrastructure nodes
                is_critical = neighbor_class in CRITICAL_CLASSES
                pruning_threshold = 0.01 if is_critical else 0.1

                if new_score < pruning_threshold:
                    continue
                # --- End of Pruning Logic ---

                if neighbor not in visited or new_score > visited[neighbor]:
                    visited[neighbor] = new_score
                    queue.append((neighbor, new_score, depth + 1))

        # Assemble the context from the visited nodes
        expanded_context = []
        for node, score in visited.items():
            if node == seed_node:  # Don't include the seed node in its own context
                continue
            
            node_data = self.graph.nodes[node]
            expanded_context.append(
                {
                    "node_id": node,
                    "node_class": node_data.get("node_class"),
                    "semantic_role": node_data.get("semantic_role"),
                    "description": node_data.get("description", ""),
                    "traversal_score": round(score, 4),
                    "source_node": seed_node
                }
            )

        return expanded_context

    def print_context(
        self,
        context
    ):
        print("\n" + "=" * 80)

        print(
            "GRAPH NEIGHBORHOOD CONTEXT"
        )

        print("=" * 80)

        for entry in context:
            print("\n" + "-" * 80)

            print(
                f"Node ID: "
                f"{entry['node_id']}"
            )

            print(
                f"Node Class: "
                f"{entry['node_class']}"
            )

            print(
                f"Semantic Role: "
                f"{entry['semantic_role']}"
            )

            print(
                f"Description: "
                f"{entry['description']}"
            )

    def run(
        self,
        seed_node,
        max_hops=1
    ):
        context = (
            self.expand_operational_context(
                seed_node,
                max_hops=max_hops
            )
        )

        self.print_context(context)