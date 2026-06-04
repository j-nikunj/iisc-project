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

# Bengaluru Transportation Intelligence GraphRAG

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python)
![NetworkX](https://img.shields.io/badge/Graph-NetworkX-lightgrey?style=flat-square)
![Qdrant](https://img.shields.io/badge/Vector_DB-Qdrant-red?style=flat-square&logo=qdrant)
![GraphRAG](https://img.shields.io/badge/Architecture-GraphRAG-8A2BE2?style=flat-square)
![LM Studio](https://img.shields.io/badge/Inference-LM_Studio-green?style=flat-square)
![Qwen](https://img.shields.io/badge/LLM-Qwen2.5_14B-orange?style=flat-square)
![Research](https://img.shields.io/badge/Status-Research_Project-success?style=flat-square)
![IISc Bangalore](https://img.shields.io/badge/Institution-IISc_Bangalore-maroon?style=flat-square)

## Overview
The Bengaluru Transportation Intelligence GraphRAG is a research-grade infrastructure project developed at the Indian Institute of Science (IISc) Bangalore. It implements a Hybrid Graph Retrieval-Augmented Generation (GraphRAG) architecture to perform complex operational reasoning over urban mobility networks. By coupling deterministic graph traversals with local Large Language Models (LLMs), the system analyzes systemic traffic cascades, infrastructure bottlenecks, and multimodal transit failures.

## Motivation
Standard RAG architectures rely on pure semantic similarity, which fails in highly interconnected domains like transportation. A semantic vector search might identify that "Silk Board" and "Traffic" are related, but it cannot structurally trace how a flooded underpass upstream systematically forces vehicle diversions that eventually paralyze Silk Board. This project solves this by anchoring the LLM's context window to strict, multi-hop operational chains extracted from a deterministic knowledge graph.

## Core Features
* **Massive-Scale Knowledge Graph:** Encodes 97,662 transportation nodes and 4,231,386 edges mapping Bengaluru's operational topology.
* **Hybrid Semantic Retrieval:** Fuses Qdrant vector similarity (for semantic entry points) with NetworkX breadth-first search (for structural context).
* **Deterministic Hallucination Resistance:** Employs traversal-aware context ranking to physically bound the LLM's reasoning, effectively neutralizing out-of-domain hallucinations.
* **In-Memory Latency Optimization:** Reduced end-to-end query retrieval latency by **~4,400x** (from ~160 seconds to ~36 milliseconds) via advanced graph caching and semantic pruning.
* **Air-Gapped Inference:** Fully local reasoning pipeline utilizing LM Studio and Qwen2.5-14B, ensuring data privacy and zero API dependency.

## System Architecture
graph TD
    %% Styling Definitions
    classDef input fill:#2b3137,stroke:#fff,stroke-width:1px,color:#fff;
    classDef processing fill:#0366d6,stroke:#fff,stroke-width:1px,color:#fff;
    classDef storage fill:#28a745,stroke:#fff,stroke-width:1px,color:#fff;
    classDef generation fill:#d73a49,stroke:#fff,stroke-width:1px,color:#fff;

    %% Layer 1: Ingestion & Storage
    subgraph Layer 1: Knowledge Construction
        A[Raw Transportation Data]:::input --> B[Ontology Mapping]:::processing
        B --> C[Graph Construction]:::processing
        C --> D[(NetworkX Knowledge Graph)]:::storage
        C --> E[Text Embedding Pipeline]:::processing
        E --> F[(Qdrant Vector DB)]:::storage
    end

    %% Layer 2: Hybrid Retrieval
    subgraph Layer 2: Semantic Hybrid Retrieval
        G[User Query]:::input --> H[Semantic Retrieval]:::processing
        F --> H
        H --> I[Seed Nodes Top-K]:::processing
        I --> J[Neighborhood Expansion]:::processing
        D --> J
    end

    %% Layer 3: Context Assembly
    subgraph Layer 3: Reasoning Pipeline
        J --> K[Context Assembly & Ranking]:::processing
        K --> L[Operational Chains Extraction]:::processing
        L --> M[GraphRAG Payload Generation]:::processing
    end

    %% Layer 4: Generation
    subgraph Layer 4: Inference
        M --> N[LM Studio / Local Qwen]:::generation
        N --> O[Final Operational Analysis]:::generation
    end

    %% Link Subgraphs structurally
    F -.->|Vector Matches| H
    D -.->|Topology Data| J

## Pipeline Deep-Dive

### 1. Retrieval Pipeline
The retrieval phase avoids naive vector chunking. Instead, it embeds the semantic properties of physical infrastructure into Qdrant. When queried, Qdrant returns a highly precise set of "Seed Nodes". 

### 2. GraphRAG Pipeline
Seed nodes are passed to the NetworkX engine, which executes a bounded Neighborhood Expansion (Breadth-First Search). This captures the immediate upstream and downstream causal topological relationships (e.g., `PROPAGATES_TO`, `FEEDS_INTO`).

### 3. Operational Reasoning Chains
The expanded neighborhood is serialized into structured Operational Chains. Instead of receiving unstructured text, the LLM receives strict causal pathways:
`[Flood Event] -> IMPACTS -> [EcoSpace Underpass] -> PROPAGATES_TO -> [ORR]`

## Performance Metrics

| Metric | Baseline (Disk-I/O Naive) | Optimized (In-Memory + Pruning) | Improvement |
| :--- | :--- | :--- | :--- |
| **Graph Size** | 97K Nodes / 4.2M Edges | 97K Nodes / 4.2M Edges | N/A |
| **Retrieval Latency** | ~160,000 ms | **~36 ms** | **~4,400x** |
| **Hallucination Rate** | High (Semantic Only) | **0%** (Graph-Bounded) | Absolute |

## Repository Structure
Please refer to the `docs/` directory for deep-dive technical documentation on the ontology, reasoning pipeline, and benchmarking methodology.

## Example Queries
* *"Trace the propagation of traffic spillback from HSR Layout to the Silk Board junction."*
* *"Analyze the downstream traffic impact if the Purple Line metro experiences a sudden signaling failure."*

## License
MIT License. See `LICENSE` for details.