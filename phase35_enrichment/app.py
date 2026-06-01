import streamlit as st
import json
import time
import requests
from pathlib import Path

# It's good practice to put imports of your own modules after standard libraries
# Assuming hybrid_retriever is in the same directory or the path is correctly set up
try:
    from hybrid_retriever import HybridGraphRetriever
except ImportError:
    st.error("Failed to import HybridGraphRetriever. Make sure it's in the correct path.")
    st.stop()

# --- Page Configuration ---
st.set_page_config(
    page_title="Bengaluru Transport Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Caching ---
@st.cache_resource
def load_retriever():
    """
    Instantiates and caches the HybridGraphRetriever.
    The expensive graph loading happens here, but only once.
    """
    with st.spinner("Initializing Graph Engine (first-time load)..."):
        retriever = HybridGraphRetriever() # Instantiated with defaults
    return retriever

# --- Helper Functions ---
def format_trace_for_llm(trace_data: dict) -> str:
    """Formats the trace JSON into a clean, token-efficient Markdown string for the LLM."""
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

def query_local_llm(endpoint: str, query_text: str, formatted_trace: str):
    """Sends the formatted context and query to the local LLM and returns the response."""
    system_prompt = (
        "You are an expert Transportation Infrastructure Analyst. Answer the user's query based "
        "strictly on the provided GraphRAG context. CRUCIAL: If the context is irrelevant or "
        "lacks evidence, you must explicitly refuse to answer to avoid hallucination."
    )

    user_content = (
        f"QUERY:\n{query_text}\n\n"
        f"GRAPHRAG CONTEXT:\n{formatted_trace}"
    )

    api_payload = {
        "model": "qwen/qwen2.5-coder-14b", # Assuming a powerful model is loaded
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.2,
        "max_tokens": 1500,
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(endpoint, headers=headers, json=api_payload, timeout=120)
        response.raise_for_status()
        response_data = response.json()
        if response_data.get("choices"):
            return response_data["choices"][0]["message"]["content"]
        else:
            return "Error: The LLM API returned a valid response but with no 'choices' field."
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to connect to LM Studio at {endpoint}. Is the server running? Details: {e}"
    except Exception as e:
        return f"An unexpected error occurred during the API call: {e}"


# --- UI Layout ---

# --- Sidebar ---
with st.sidebar:
    st.header("GraphRAG Parameters")
    top_k_slider = st.slider(
        "Top-K Seed Nodes",
        min_value=1,
        max_value=20,
        value=10,
        help="Number of initial nodes to retrieve from the vector search."
    )
    max_hops_slider = st.slider(
        "Max Traversal Hops",
        min_value=1,
        max_value=5,
        value=3,
        help="Maximum number of steps to expand from the seed nodes in the graph."
    )
    st.header("API Configuration")
    endpoint_input = st.text_input(
        "LM Studio Endpoint",
        value="http://localhost:1234/v1/chat/completions"
    )
    
    st.markdown("---")
    st.info("Graph Status: Loaded (Cached)")


# --- Main Panel ---
st.header("Bengaluru Operational Transport Intelligence (BOTI)")
st.markdown("A Hybrid GraphRAG system for deep analysis of Bengaluru's transportation network.")

# Load the retriever from cache
retriever = load_retriever()

user_query = st.text_area(
    "Enter your analytical query:",
    "Trace the propagation of traffic spillback from HSR Layout to the Silk Board junction.",
    height=100
)

if st.button("Analyze Query"):
    if not user_query:
        st.warning("Please enter a query.")
    else:
        graphrag_payload = None
        # --- Step 1: Run GraphRAG Pipeline ---
        with st.spinner("Executing Semantic Search & Graph Traversal..."):
            try:
                # Update retriever with current slider values before running
                retriever.top_k = top_k_slider
                retriever.max_hops = max_hops_slider
                retriever.run(user_query)
                
                # Load the generated payload
                payload_path = Path(__file__).parent / "output" / "graphrag_payload.json"
                if payload_path.exists():
                    with open(payload_path, 'r') as f:
                        graphrag_payload = json.load(f)
                else:
                    st.error("Execution finished, but the output payload 'graphrag_payload.json' was not found.")

            except Exception as e:
                st.error(f"An error occurred during the GraphRAG pipeline execution: {e}")

        if graphrag_payload:
            # --- Step 2: Query LLM for Synthesis ---
            with st.spinner("Synthesizing Operational Intelligence..."):
                formatted_trace = format_trace_for_llm(graphrag_payload)
                llm_response = query_local_llm(endpoint_input, user_query, formatted_trace)

            st.success("Analysis Complete!")
            st.markdown("### LLM-Generated Analysis")
            st.markdown(llm_response)
            
            st.markdown("---")

            # --- Step 3: Display Expandable Raw Data ---
            with st.expander("View Retrieved Context Nodes"):
                nodes = graphrag_payload.get("neighborhood_context", [])
                if not nodes:
                    st.write("No context nodes were retrieved.")
                else:
                    for node in nodes:
                        st.markdown(f"**{node.get('node_id', 'N/A')}**: {node.get('description', 'No description.')}")

            with st.expander("View Causal Reasoning Chains"):
                chains = graphrag_payload.get("causal_chains", [])
                if not chains:
                    st.write("No causal chains were assembled.")
                else:
                    for i, chain in enumerate(chains):
                        path_ids = [p.get('node_id', 'N/A') for p in chain.get('path', [])]
                        path_str = " -> ".join(path_ids)
                        st.markdown(f"**Chain {i+1}**: `{path_str}`")
