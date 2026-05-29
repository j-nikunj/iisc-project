#  Bengaluru Operational Transport Intelligence (BOTI)

[![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Framework](https://img.shields.io/badge/Framework-GraphRAG-green)](https://www.microsoft.com/en-us/research/project/graphrag/)

A sophisticated, multi-phase GraphRAG system designed to perform deep operational analysis on Bengaluru's complex transportation network. BOTI moves beyond simple document retrieval by constructing and reasoning over causal chains within a large-scale, interconnected knowledge graph.

## Overview

Traditional RAG systems excel at retrieving factual snippets but often fail to capture the complex, cascading relationships inherent in real-world operational networks. When a transportation analyst asks, "What are the downstream effects of flooding at Silk Board junction?", they need more than a document; they need a reasoned chain of causality.

BOTI addresses this by implementing a **Hybrid GraphRAG architecture**. It leverages a semantic vector search to identify initial "seed nodes" within our graph and then performs a propagation-aware traversal to discover and assemble causal operational chains. These chains are then passed to a local Large Language Model (LLM) for high-level analysis, providing actionable insights into the intricate dynamics of urban mobility.

## Core Architecture

The system follows a precise, multi-stage pipeline to transform a natural language query into a reasoned, graph-grounded answer.

**Query -> Semantic Search -> Graph Traversal -> Causal Chain Construction -> LLM Reasoning**

1.  **Semantic Seed Node Retrieval (Vector Search)**
    *   A user's query (e.g., "Analyze congestion patterns on Outer Ring Road") is embedded using a `SentenceTransformers` model (`all-MiniLM-L6-v2`).
    *   This embedding is used to query a **Qdrant** vector database, which identifies the most semantically relevant entities in the graph to act as "seed nodes" (e.g., `CORRIDOR_OUTER_RING_ROAD`, `CHOKEPOINT_MARATHAHALLI_BRIDGE`).

2.  **Propagation-Aware Graph Traversal**
    *   Starting from the seed nodes, we perform a breadth-first search (BFS) on our **NetworkX** `MultiDiGraph` (containing over 4.2 million edges).
    *   This traversal is enhanced with a custom **"Semantic-Aware Pruning"** algorithm. It intelligently preserves high-value, distant nodes (like critical infrastructure or policy documents) that a naive traversal might discard, ensuring that crucial context is not lost.

3.  **Causal Chain Assembly**
    *   The context-rich neighborhood of nodes gathered during traversal is analyzed to reconstruct the most probable causal chains.
    *   The system traces paths from effect back to cause, assembling end-to-end operational narratives (e.g., `EVENT_HEAVY_RAINFALL` -> `ASSET_DRAINAGE_FAILURE_INDRANAGAR` -> `STATE_FLOODING_INDRANAGAR_100FT_ROAD` -> `IMPACT_GRIDLOCK_EGL_FLYOVER`).

4.  **LLM-Powered Reasoning**
    *   The assembled causal chains, now in a compact and token-efficient format, are passed to a locally hosted LLM (`qwen/qwen2.5-coder-14b` via LM Studio).
    *   The LLM's role is not to find information but to *reason* over the provided graph evidence, answering the user's initial query based *strictly* on the operational chains.

## Key Technical Achievements

This project is not just a theoretical framework but a highly optimized and robust implementation with measurable wins.

1.  **🚀 4,400x Latency Optimization**
    *   Initial queries suffered from a ~160,000ms latency due to redundant loading of the massive 4.2 million edge graph from disk for every request.
    *   By implementing an intelligent in-memory caching strategy, we **reduced the average query latency to just 35ms**—a 99.98% reduction that makes interactive analysis feasible.

2.  **🧠 "Epistemic Humility" & Hallucination Rejection**
    *   A core goal was to build a system that is not only accurate but also aware of its own knowledge boundaries. We developed an automated evaluation harness to test this.
    *   When presented with adversarial queries containing "hallucination traps" (e.g., "Analyze shipping delays at the non-existent Bengaluru seaport"), the system correctly identifies that no supporting evidence exists in the graph.
    *   The LLM, guided by this lack of evidence, **explicitly refuses to answer**, demonstrating true "epistemic humility" and preventing the generation of plausible but false information.

3.  **🎯 Semantic-Aware Pruning**
    *   Standard graph traversal often fails to capture critical but distant nodes. Our custom pruning logic dynamically adjusts its scoring thresholds based on node class, ensuring that vital entities like `Policy` or `Infrastructure` nodes are preserved in the final context, leading to more comprehensive and accurate causal chains.

## Tech Stack

*   **Vector Database**: Qdrant (local Docker instance)
*   **Graph Engine**: NetworkX
*   **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2`
*   **Local LLM Inference**: LM Studio
*   **Reasoning Model**: `qwen/qwen2.5-coder-14b`
*   **Core Language**: Python

## Next Steps & Future Roadmap

*   **[ ] Interactive Frontend**: Develop a Streamlit or Flask-based user interface to allow non-technical stakeholders to interact with the system, visualize the generated causal chains, and explore the graph.
*   **[ ] Temporal Dynamics**: Integrate temporal data (e.g., GTFS real-time feeds) to enable analysis of time-sensitive operational events and model their evolution.
*   **[ ] Advanced Graph Algorithms**: Explore the use of more advanced algorithms like PageRank or community detection to identify systemic risks and influential nodes within the transportation network.
*   **[ ] Multi-Modal Integration**: Enhance the knowledge graph by incorporating multi-modal data, such as images of infrastructure damage or traffic camera feeds, to provide richer, more detailed context.
