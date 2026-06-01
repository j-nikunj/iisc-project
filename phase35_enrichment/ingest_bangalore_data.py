import json
import networkx as nx
from pathlib import Path
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import VectorParams, Distance
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

    # Check if collection exists, create if it doesn't
    try:
        collections_response = qdrant_client.get_collections()
        collection_names = [c.name for c in collections_response.collections]
        
        if QDRANT_COLLECTION not in collection_names:
            print(f"Collection '{QDRANT_COLLECTION}' not found. Creating a new one...")
            qdrant_client.create_collection(
                collection_name=QDRANT_COLLECTION,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE) # 384 is the dimension size for all-MiniLM-L6-v2
            )
            print(f"[SUCCESS] Created collection '{QDRANT_COLLECTION}'.")
    except Exception as e:
        print(f"Warning: Failed to verify or create Qdrant collection: {e}")


    # --- Load Existing Graph or Create New ---
    if os.path.exists(GRAPH_PATH):
        print(f"Loading existing graph from: {GRAPH_PATH}")
        try:
            graph = nx.read_gml(GRAPH_PATH)
        except Exception as e:
            print(f"[WARNING] Graph file is corrupted or unreadable ({e}). Initializing a new nx.MultiDiGraph().")
            graph = nx.MultiDiGraph()
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
            data = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Data file not found at {DATA_PATH}. Exiting.")
        return
    print(f"Loaded {len(data)} operational entities from JSON.")

    # --- Ghost Node Prevention ---
    valid_node_ids = {e["node_id"] for e in data}
    print(f"Created a set of {len(valid_node_ids)} valid node IDs for edge validation.")

    # --- Process Entities (Nodes and Edges) ---
    for entity in data:
        source_id = entity.get("node_id")
        if not source_id:
            continue

        # --- NODE SANITIZATION ---
        raw_node_attrs = {
            "node_class": entity.get("node_class"),
            "semantic_role": entity.get("semantic_role"),
            "name": entity.get("name"),
            "description": entity.get("description"),
            "risk_level": entity.get("risk_level"),
            "severity_score": entity.get("severity_score"),
            "latitude": entity.get("latitude"),
            "longitude": entity.get("longitude")
        }

        # Convert lists to strings for GML compatibility
        if entity.get("mobility_modes"):
            raw_node_attrs["mobility_modes"] = ",".join(entity["mobility_modes"])
        if entity.get("operational_tags"):
            raw_node_attrs["operational_tags"] = ",".join(entity["operational_tags"])

        # Filter out all None values
        clean_node_attrs = {k: v for k, v in raw_node_attrs.items() if v is not None}
        graph.add_node(source_id, **clean_node_attrs)

        # --- EDGE SANITIZATION ---
        for rel in entity.get("relations", []):
            target_id = rel.get("target_id")
            if target_id and target_id in valid_node_ids:
                raw_edge_attrs = {
                    "relation_type": rel.get("relation_type", "connected_to"),
                    "weight": rel.get("weight", 1.0)
                }
                # Filter out None values just in case
                clean_edge_attrs = {k: v for k, v in raw_edge_attrs.items() if v is not None}
                graph.add_edge(source_id, target_id, **clean_edge_attrs)
            elif target_id:
                 print(f"[WARNING] Skipping edge from '{source_id}' to ghost node '{target_id}'.")


    # --- Batch Embedding Generation ---
    print("Preparing text for batch embedding generation...")

    # 1. Extract text strings for the embedding model
    texts_to_embed = []
    for entity in data:
        node_name = entity.get("name", entity.get("node_id", "Unknown Node"))
        description = entity.get("description", "")
        # Combine name and description for rich semantic search
        semantic_text = f"{node_name}: {description}"
        texts_to_embed.append(semantic_text)

    print(f"Generating embeddings for {len(texts_to_embed)} contexts in a single batch...")
    # 2. Encode the strings, NOT the dictionaries
    embeddings = model.encode(texts_to_embed, show_progress_bar=True)
    print("[SUCCESS] Batch embedding complete.")

    # --- Prepare Qdrant points ---
    points_to_upsert = []
    for i, payload in enumerate(data):
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