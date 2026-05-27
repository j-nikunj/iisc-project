import json
import requests
from pathlib import Path

# Define the project root and the path to the payload file
PROJECT_ROOT = Path(__file__).resolve().parent
PAYLOAD_PATH = PROJECT_ROOT / "output" / "graphrag_payload.json"
LM_STUDIO_ENDPOINT = "http://localhost:1234/v1/chat/completions"

def load_rag_payload(filepath):
    """Loads the GraphRAG JSON payload from the specified file."""
    print(f"Loading GraphRAG payload from: {filepath}")
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Payload file not found at: {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"[ERROR] Failed to decode JSON from: {filepath}")
        return None

def query_local_llm(payload):
    """Sends the GraphRAG payload to the local LLM and prints the response."""
    if not payload:
        return

    system_prompt = (
        "You are an expert transportation infrastructure analyst. Your task is to analyze "
        "GraphRAG context containing seed nodes, neighborhood context, and causal "
        "operational chains. Identify cascading failure risks and summarize the "
        "systemic vulnerabilities based strictly on the provided graph context."
    )

    # Format the payload into a clean narrative instead of a raw JSON dump
    user_content = format_payload_as_narrative(payload)

    api_payload = {
        "model": "loaded_model",  # This will use whatever model is loaded in LM Studio
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.2,
        "max_tokens": 1500,
    }

    headers = {"Content-Type": "application/json"}

    print("\nSending payload to LM Studio...")
    try:
        response = requests.post(LM_STUDIO_ENDPOINT, headers=headers, json=api_payload)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        response_data = response.json()
        
        print("\n" + "="*80)
        print("LLM REASONING RESPONSE")
        print("="*80)
        
        # Extract and print the content from the response
        if response_data.get("choices"):
            llm_response = response_data["choices"][0]["message"]["content"]
            print(llm_response)
        else:
            print("[ERROR] No response choices found in the API return object.")
            print("Full Response:", response_data)

    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Failed to connect to LM Studio at {LM_STUDIO_ENDPOINT}.")
        print("Please ensure LM Studio is running and the local server is started.")
        print(f"Details: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def format_payload_as_narrative(payload: dict) -> str:
    """Formats the GraphRAG JSON payload into a structured Markdown string."""
    narrative = ["# GraphRAG Operational Context\n"]

    # 1. Query
    narrative.append("## 1. Query")
    narrative.append(f"{payload.get('query', 'N/A')}\n")

    # 2. Seed Nodes
    narrative.append("## 2. Seed Nodes")
    seed_nodes = payload.get('seed_nodes', [])
    if not seed_nodes:
        narrative.append("- No seed nodes found.")
    else:
        for node in seed_nodes:
            narrative.append(
                f"- **{node.get('node_id', 'N/A')}** ({node.get('node_class', 'N/A')}): "
                f"{node.get('description', 'No description.')} "
                f"(Role: {node.get('semantic_role', 'N/A')}, Score: {node.get('traversal_score', 0.0)})"
            )
    narrative.append("")

    # 3. Neighborhood Context
    narrative.append("## 3. Neighborhood Context")
    neighborhood = payload.get('neighborhood_context', [])
    if not neighborhood:
        narrative.append("- No neighborhood context found.")
    else:
        for node in neighborhood:
            narrative.append(
                f"- **{node.get('node_id', 'N/A')}** ({node.get('node_class', 'N/A')}): "
                f"{node.get('description', 'No description.')} "
                f"(Source: {node.get('source_node', 'N/A')}, Score: {node.get('traversal_score', 0.0)})"
            )
    narrative.append("")

    # 4. Operational Reasoning Chains
    narrative.append("## 4. Operational Reasoning Chains")
    chains = payload.get('causal_chains', [])
    if not chains:
        narrative.append("- No operational chains were assembled.")
    else:
        for i, chain in enumerate(chains):
            path_str = " -> ".join([p.get('node_id', 'N/A') for p in chain.get('path', [])])
            narrative.append(
                f"- **Chain {i+1}** (Score: {chain.get('chain_score', 0.0)})\n"
                f"  Path: {path_str}"
            )
    
    return "\n".join(narrative)

def main():
    """Main function to run the local LLM reasoner."""
    rag_payload = load_rag_payload(PAYLOAD_PATH)
    query_local_llm(rag_payload)

if __name__ == "__main__":
    main()
