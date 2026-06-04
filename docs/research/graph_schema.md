Initial Graph Schema — iisc project

Node properties:
- id
- title
- aliases
- content (markdown)
- embeddings
- metadata (source, timestamps, tags)
- geographic metadata (lat/lon, admin boundaries)
- infrastructure_category
- ontology_types
- provenance (citations, dataset links)

Edge types:
- wikilink
- backlink
- citation
- semantic_similarity
- causal_relation
- dependency_chain
- spatial_connectivity
- governance_relation

Capabilities to support:
- graph traversal, centrality, community detection
- subgraph extraction, causal-chain reasoning
- embedding-backed semantic neighborhood queries

Storage candidates: Neo4j / ArangoDB / Memgraph for graph; Qdrant/FAISS for vectors.
