import json
import networkx as nx
from pathlib import Path
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models
import uuid
import os

# --- Configuration ---
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_PATH = PROJECT_ROOT / "data" / "bangalore_operational_entities.json"
OUTPUT_DIR = PROJECT_ROOT / "output"
GRAPH_PATH = OUTPUT_DIR / "semantic_transport_graph.gml"

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
QDRANT_COLLECTION = "semantic_transport_graph"
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'

def main():
    """
    Ingests curated Bengaluru operational data into the NetworkX graph
    and Qdrant vector database.
    """
    print("--- Starting Bengaluru Data Ingestion ---")

    # --- Initialize Clients ---
    print(f"Initializing embedding model: {EMBEDDING_MODEL}...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    
    print(f"Connecting to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}...")
    qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    # --- Load Existing Graph or Create New ---
    if os.path.exists(GRAPH_PATH):
        print(f"Loading existing graph from: {GRAPH_PATH}")
        graph = nx.read_gml(GRAPH_PATH)
    else:
        print("No existing graph found. Initializing a new nx.MultiDiGraph().")
        graph = nx.MultiDiGraph()
    
    initial_nodes = graph.number_of_nodes()
    initial_edges = graph.number_of_edges()
    print(f"Initial graph state: {initial_nodes} nodes, {initial_edges} edges.")

    # --- Load JSON Data ---
    print(f"Loading data from: {DATA_PATH}")
    try:
        with open(DATA_PATH, 'r') as f:
            entities = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Data file not found at {DATA_PATH}. Exiting.")
        return
    print(f"Loaded {len(entities)} operational entities from JSON.")

    # --- Ghost Node Prevention ---
    valid_node_ids = {e["node_id"] for e in entities}
    print(f"Created a set of {len(valid_node_ids)} valid node IDs for edge validation.")

    # --- Ingestion Process ---
    contexts_to_embed = []
    qdrant_payloads = []
    
    for entity in entities:
        node_id = entity["node_id"]

        # 1. Graph Ingestion: Add Node with new attributes
        graph.add_node(
            node_id,
            node_class=entity.get("node_class"),
            semantic_role=entity.get("semantic_role"),
            name=entity.get("name"),
            description=entity.get("description"),
            operational_tags=str(entity.get("operational_tags", [])),
            risk_level=entity.get("risk_level"),
            mobility_modes=str(entity.get("mobility_modes", [])),
            latitude=entity.get("latitude"),
            longitude=entity.get("longitude"),
            severity_score=entity.get("severity_score")
        )

        # 2. Graph Ingestion: Add Edges with validation
        for relation in entity.get("relations", []):
            target_id = relation["target_id"]
            if target_id in valid_node_ids:
                graph.add_edge(
                    node_id,
                    target_id,
                    relation=relation["relation_type"],
                    weight=relation.get("weight")
                )
            else:
                print(f"[WARNING] Skipping edge from '{node_id}' to ghost node '{target_id}'.")

        # 3. Vector DB Ingestion: Prepare data for batching
        tags_str = ", ".join(entity.get("operational_tags", []))
        semantic_context = (
            f"Node: {entity.get('name', '')}. "
            f"Class: {entity.get('node_class', '')}. "
            f"Role: {entity.get('semantic_role', '')}. "
            f"Description: {entity.get('description', '')}. "
            f"Tags: {tags_str}"
        )
        contexts_to_embed.append(semantic_context)
        qdrant_payloads.append(entity)

    # --- Batch Embedding Generation ---
    print(f"Generating embeddings for {len(contexts_to_embed)} contexts in a single batch...")
    embeddings = model.encode(contexts_to_embed, show_progress_bar=True)
    print("[SUCCESS] Batch embedding complete.")

    # --- Prepare Qdrant points ---
    points_to_upsert = []
    for i, payload in enumerate(qdrant_payloads):
        node_id = payload["node_id"]
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, node_id))
        points_to_upsert.append(
            models.PointStruct(
                id=point_id,
                vector=embeddings[i].tolist(),
                payload=payload
            )
        )

    # --- Upsert to Qdrant in a single batch ---
    if points_to_upsert:
        print(f"Upserting {len(points_to_upsert)} vectors into Qdrant collection '{QDRANT_COLLECTION}'...")
        qdrant_client.upsert(
            collection_name=QDRANT_COLLECTION,
            points=points_to_upsert,
            wait=True
        )
        print("[SUCCESS] Qdrant indexing complete.")

    # --- Persistence ---
    print(f"Saving updated graph to: {GRAPH_PATH}")
    nx.write_gml(graph, GRAPH_PATH)
    
    # --- Final Logging ---
    nodes_added = graph.number_of_nodes() - initial_nodes
    edges_added = graph.number_of_edges() - initial_edges
    print("\n--- Ingestion Summary ---")
    print(f"Nodes added: {nodes_added}")
    print(f"Edges added: {edges_added}")
    print(f"Final graph state: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges.")
    print("-------------------------\n")


if __name__ == "__main__":
    main()