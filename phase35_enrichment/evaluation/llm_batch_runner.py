import json
import requests
from pathlib import Path

# --- Configuration ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "evaluation" / "results"
EVAL_RESULTS_FILE = RESULTS_DIR / "evaluation_results.json"
REPORT_FILE = RESULTS_DIR / "llm_reasoning_report.md"

LM_STUDIO_ENDPOINT = "http://localhost:1234/v1/chat/completions"

def format_trace_as_narrative(trace: dict) -> str:
    """Formats the GraphRAG trace object into a structured Markdown string."""
    narrative = ["# GraphRAG Operational Context\n"]

    # 1. Seed Nodes
    narrative.append("## 1. Seed Nodes")
    seed_nodes = trace.get('seed_nodes', [])
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

    # 2. Neighborhood Context
    narrative.append("## 2. Neighborhood Context")
    neighborhood = trace.get('neighborhood_context', [])
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

    # 3. Operational Reasoning Chains
    narrative.append("## 3. Operational Reasoning Chains")
    chains = trace.get('causal_chains', [])
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

def query_local_llm(query_text: str, trace_data: dict):
    """Sends the formatted context and query to the local LLM and returns the response."""
    
    system_prompt = (
        "You are an expert Transportation Infrastructure Analyst. "
        "You will be provided with a specific user query and a structured GraphRAG context trace. "
        "Your task is to answer the query based strictly on the provided context. "
        "CRUCIAL: If the context is irrelevant to the query or does not logically contain the answer, "
        "you must explicitly refuse to answer to avoid hallucination."
    )

    user_content = (
        f"QUERY:\n{query_text}\n\n"
        f"GRAPHRAG CONTEXT:\n{json.dumps(trace_data, indent=2)}"
    )

    api_payload = {
        "model": "loaded_model",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.2,
        "max_tokens": 1500,
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(LM_STUDIO_ENDPOINT, headers=headers, json=api_payload)
        response.raise_for_status()
        response_data = response.json()
        if response_data.get("choices"):
            return response_data["choices"][0]["message"]["content"]
        else:
            return "[ERROR] No response choices found."
    except requests.exceptions.RequestException as e:
        return f"[ERROR] Failed to connect to LM Studio: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def main():
    """
    Runs the LLM batch evaluation by sending each benchmark trace to the local LLM.
    """
    print("--- Starting LLM Batch Reasoning Runner ---")

    # --- Load Evaluation Results ---
    try:
        with open(EVAL_RESULTS_FILE, 'r') as f:
            eval_results = json.load(f)
        print(f"Loaded {len(eval_results)} evaluation results to process.")
    except FileNotFoundError:
        print(f"[ERROR] Evaluation results file not found at: {EVAL_RESULTS_FILE}")
        return

    # --- Clear/Start Report File ---
    with open(REPORT_FILE, 'w') as f:
        f.write("# LLM Reasoning Report\n\n")
    print(f"Initialized report file at: {REPORT_FILE}")

    # --- Run Batch Loop ---
    for result in eval_results:
        query_id = result["query_id"]
        # Correctly get query_text from the top-level of the result object
        query_text = result.get("query_text", "Query text not found in result")

        print(f"\nProcessing Query ID: {query_id}...")

        # 1. Extract the raw trace data
        trace_data = result.get("trace", {})

        # 2. Query the LLM with the query and the raw trace data
        llm_response = query_local_llm(query_text, trace_data)

        # 3. Print to console
        print(f"LLM Response for {query_id}:\n---\n{llm_response}\n---")

        # 4. Append to Markdown Report
        with open(REPORT_FILE, 'a') as f:
            f.write(f"## Query ID: {query_id}\n\n")
            f.write(f"**Query:** `{query_text}`\n\n")
            f.write("**LLM Response:**\n")
            f.write("```text\n")
            f.write(llm_response + "\n")
            f.write("```\n\n")
            f.write("---\n\n")

    print(f"\nBatch processing complete. Full report saved to: {REPORT_FILE}")

if __name__ == "__main__":
    main()