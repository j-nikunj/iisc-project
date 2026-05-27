import networkx as nx
import uuid

class ContextChainBuilder:
    HIGH_PRIORITY_RELATIONS = {
        "PROPAGATES_TO",
        "IMPACTS",
    }

    def __init__(self, graph):
        self.graph = graph

    def build_chains(self, seed_node, expanded_context):
        """
        Builds operational reasoning chains from the expanded context.
        """
        # Sort context by traversal_score to prioritize more relevant nodes
        sorted_context = sorted(expanded_context, key=lambda x: x['traversal_score'], reverse=True)
        
        chains = []
        for target_node_info in sorted_context:
            # We only build chains towards high-priority operational nodes
            if not self._is_high_priority_node(target_node_info):
                continue

            path = self._reconstruct_path(seed_node, target_node_info['node_id'], expanded_context)

            if path:
                chain_score = sum(node['traversal_score'] for node in path)
                chains.append({
                    "chain_id": f"chain_{uuid.uuid4()}",
                    "path": path,
                    "chain_score": round(chain_score, 4),
                    "reasoning_type": "propagation_chain"
                })
        
        # Sort chains by their aggregated score
        return sorted(chains, key=lambda x: x['chain_score'], reverse=True)

    def _reconstruct_path(self, start_node, end_node, context):
        """
        Finds the shortest path from start_node to end_node using BFS,
        constrained to nodes within the provided context.
        This is a lightweight path reconstruction, not a full graph search.
        """
        context_nodes = {item['node_id'] for item in context}
        context_nodes.add(start_node)
        
        if start_node not in context_nodes or end_node not in context_nodes:
            return []

        queue = [(start_node, [start_node])]
        visited = {start_node}

        while queue:
            current_node, path = queue.pop(0)

            if current_node == end_node:
                # Path found, now map back to full context objects
                path_details = []
                context_map = {item['node_id']: item for item in context}
                context_map[start_node] = {'node_id': start_node, 'traversal_score': 1.0} # Add seed
                
                for node_id in path:
                    path_details.append(context_map[node_id])
                return path_details

            # Explore neighbors, but only those in the original context
            for neighbor in self.graph.neighbors(current_node):
                if neighbor in context_nodes and neighbor not in visited:
                    relation_priority = self._get_relation_priority(current_node, neighbor)
                    if relation_priority == "HIGH": # Prioritize propagation paths
                        visited.add(neighbor)
                        new_path = list(path)
                        new_path.append(neighbor)
                        queue.append((neighbor, new_path))
        return []

    def _is_high_priority_node(self, node_info):
        """Check if the node is an operational, high-priority target."""
        return node_info.get("node_class") in [
            "flooding_zone",
            "congestion_corridor",
            "spillback_failure_zone",
            "interchange_stress_zone",
            "infrastructure_bottleneck"
        ]

    def _get_relation_priority(self, source, target):
        """Determines the priority of the relation between two nodes."""
        edge_data = self.graph.get_edge_data(source, target)
        if not edge_data:
            return "LOW"

        for _, attributes in edge_data.items():
            relation = attributes.get("relation")
            if relation in self.HIGH_PRIORITY_RELATIONS:
                return "HIGH"
        return "LOW"
