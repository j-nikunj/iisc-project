import json
import requests
from pathlib import Path

# --- Configuration ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
EVAL_DIR = PROJECT_ROOT / "evaluation"
RESULTS_DIR = EVAL_DIR / "results"
EVAL_RESULTS_FILE = RESULTS_DIR / "evaluation_results.json"
BENCHMARK_QUERIES_FILE = EVAL_DIR / "benchmark_queries.json"
REPORT_FILE = RESULTS_DIR / "llm_reasoning_report.md"

LM_STUDIO_ENDPOINT = "http://localhost:1234/v1/chat/completions"

def format_trace_to_markdown(trace_data: dict) -> str:
    """Parses the trace dictionary and returns a clean, compact markdown string."""
    markdown_lines = []

    # Format neighborhood_context
    markdown_lines.append("Context Nodes:")
    context_nodes = trace_data.get("neighborhood_context", [])
    if not context_nodes:
        markdown_lines.append("- No context nodes found.")
    else:
        for node in context_nodes:
            node_id = node.get("node_id", "N/A")
            description = node.get("description", "No description.")
            markdown_lines.append(f"- [{node_id}]: {description}")

    markdown_lines.append("\nCausal Chains:")
    # Format causal_chains
    causal_chains = trace_data.get("causal_chains", [])
    if not causal_chains:
        markdown_lines.append("- No causal chains found.")
    else:
        for i, chain in enumerate(causal_chains):
            path_ids = [p.get("node_id", "N/A") for p in chain.get("path", [])]
            path_str = " -> ".join(path_ids)
            markdown_lines.append(f"- Chain {i+1}: {path_str}")

    return "\n".join(markdown_lines)

def query_local_llm(query_text: str, trace_data: dict):
    """Sends the formatted context and query to the local LLM and returns the response."""
    
    system_prompt = (
        "You are an expert Transportation Infrastructure Analyst. "
        "You will be provided with a specific user query and a structured GraphRAG context trace. "
        "Your task is to answer the query based strictly on the provided context. "
        "CRUCIAL: If the context is irrelevant to the query or does not logically contain the answer, "
        "you must explicitly refuse to answer to avoid hallucination."
    )

    # Use the new markdown serialization function
    user_content = (
        f"QUERY:\n{query_text}\n\n"
        f"GRAPHRAG CONTEXT:\n{format_trace_to_markdown(trace_data)}"
    )

    api_payload = {
        "model": "qwen/qwen2.5-coder-14b",
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

    # --- Load Evaluation Results and Benchmark Queries ---
    try:
        with open(EVAL_RESULTS_FILE, 'r') as f:
            eval_results = json.load(f)
        print(f"Loaded {len(eval_results)} evaluation results to process.")

        with open(BENCHMARK_QUERIES_FILE, 'r') as f:
            benchmark_queries = json.load(f)
        # Create a mapping from query_id to query_text
        query_map = {q["query_id"]: q["query_text"] for q in benchmark_queries}
        print("Successfully created query ID to query text map.")

    except FileNotFoundError as e:
        print(f"[ERROR] Required file not found: {e.filename}")
        return
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to decode JSON from a file: {e}")
        return


    # --- Clear/Start Report File ---
    with open(REPORT_FILE, 'w') as f:
        f.write("# LLM Reasoning Report\n\n")
    print(f"Initialized report file at: {REPORT_FILE}")

    # --- Run Batch Loop ---
    for result in eval_results:
        query_id = result["query_id"]
        
        # Fetch the query text from the map
        query_text = query_map.get(query_id, "Unknown Query: ID not found in benchmark file.")

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