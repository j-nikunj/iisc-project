import json
import time
import sys
from pathlib import Path

# --- Path Setup ---
# Add the parent directory to sys.path to allow direct import of hybrid_retriever
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from hybrid_retriever import HybridGraphRetriever

# --- Configuration ---
BENCHMARK_FILE = PROJECT_ROOT / "evaluation" / "benchmark_queries.json"
PAYLOAD_FILE = PROJECT_ROOT / "output" / "graphrag_payload.json"
RESULTS_DIR = PROJECT_ROOT / "evaluation" / "results"
RESULTS_FILE = RESULTS_DIR / "evaluation_results.json"

def main():
    """
    Runs the GraphRAG evaluation suite.
    """
    print("--- Starting GraphRAG Evaluation Framework ---")

    # --- Load Benchmark Queries ---
    try:
        with open(BENCHMARK_FILE, 'r') as f:
            benchmark_queries = json.load(f)
        print(f"Loaded {len(benchmark_queries)} benchmark queries.")
    except FileNotFoundError:
        print(f"[ERROR] Benchmark file not found at: {BENCHMARK_FILE}")
        return

    # --- Setup Results ---
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    all_results = []

    # --- Instantiate Retriever ---
    # We instantiate it once to avoid reloading the graph for each query
    # Tuned parameters for better recall
    retriever = HybridGraphRetriever(top_k=10, max_hops=3)
    retriever.load_graph()

    # --- Run Evaluation Loop ---
    for query in benchmark_queries:
        print("\n" + "="*80)
        print(f"Executing Query ID: {query['query_id']} ({query['category']})")
        print(f"Query Text: {query['query_text']}")
        print("="*80)

        # 1. Run pipeline and measure latency
        start_time = time.perf_counter()
        retriever.run(query["query_text"])
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000

        # 2. Load and parse the output payload
        try:
            with open(PAYLOAD_FILE, 'r') as f:
                payload = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[ERROR] Could not read or parse payload file: {e}")
            continue

        # 3. Extract trace data for logging
        trace_seed_nodes = payload.get("seed_nodes", [])
        trace_context = payload.get("neighborhood_context", [])
        trace_chains = payload.get("causal_chains", [])

        # 4. Extract retrieved nodes from causal chains for evaluation
        retrieved_nodes = set()
        for chain in trace_chains:
            for path_node in chain.get("path", []):
                if "node_id" in path_node:
                    retrieved_nodes.add(path_node["node_id"])

        # 5. Compare against expected nodes
        expected_nodes = set(query["expected_vulnerable_nodes"])
        matched_nodes = list(expected_nodes.intersection(retrieved_nodes))
        missing_nodes = list(expected_nodes.difference(retrieved_nodes))
        
        is_pass = len(missing_nodes) == 0

        # 6. Store and print results, including the new trace object
        result = {
            "query_id": query["query_id"],
            "category": query["category"],
            "latency_ms": round(latency_ms, 2),
            "pass": is_pass,
            "matched_nodes": matched_nodes,
            "missing_nodes": missing_nodes,
            "trace": {
                "seed_nodes": trace_seed_nodes,
                "neighborhood_context": trace_context,
                "causal_chains": trace_chains
            }
        }
        all_results.append(result)

        # Console output remains clean and summarized
        print("\n--- Evaluation Result ---")
        print(f"Query ID:      {result['query_id']}")
        print(f"Category:      {result['category']}")
        print(f"Latency:       {result['latency_ms']:.2f} ms")
        print(f"Pass:          {result['pass']}")
        print(f"Matched Nodes: {result['matched_nodes']}")
        print(f"Missing Nodes: {result['missing_nodes']}")
        print("-------------------------\n")

    # --- Persist all results ---
    with open(RESULTS_FILE, 'w') as f:
        json.dump(all_results, f, indent=4)
    
    print(f"Evaluation complete. All results, including full traces, saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    main()