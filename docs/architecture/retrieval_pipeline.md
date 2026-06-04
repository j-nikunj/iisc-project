# The Hybrid Retrieval Pipeline

The retrieval pipeline bridges the gap between unstructured human natural language and strict mathematical graph traversal.

## Step 1: Semantic Seed Extraction
User queries are embedded into a vector space $V \in \mathbb{R}^{384}$. We query the Qdrant database to find the subset of nodes $S$ (Seeds) that maximize cosine similarity:
$$\text{similarity}(A, B) = \frac{A \cdot B}{\|A\| \|B\|}$$
Qdrant returns the Top-K nodes (default $K=3$) that serve as the entry points into the physical graph.

## Step 2: Semantic-Aware BFS Traversal
Using the Seed subset $S$, the NetworkX engine performs a Breadth-First Search. Unlike a standard BFS which blindly extracts all adjacent nodes, our algorithm is computationally pruned based on operational relevance. 

For a given traversal depth $d(u,v) \le 3$, an edge is only traversed if the target node's `severity_score` exceeds the baseline threshold, or if the edge is explicitly typed as `PROPAGATES_TO`.

## Step 3: Subgraph Isolation
The resulting output is a highly concentrated, isolated Subgraph $G'$ containing only the causal chains relevant to the exact failure mechanism queried by the user, entirely filtering out the remaining 97,000+ nodes to preserve the LLM's attention mechanism.