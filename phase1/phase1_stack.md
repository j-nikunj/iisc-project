Minimal Implementation Stack — Phase 1

Goal: Validate ontology quality and graph semantics without premature complexity.

Recommended stack (Phase 1)
- Markdown files (Obsidian-compatible) as the source of truth.
- Python + NetworkX for parsing nodes and edges, validation, and traversal.
- A small YAML + wikilink parser to extract nodes and relations.
- Optional: SQLite for indexing node metadata and quick lookups.

Why NetworkX first (not Neo4j yet)
- No server dependency, fast iteration, and easy debugging.
- Excellent for small graphs (< 10k nodes) and ontology experimentation.
- Lets you rapidly test traversal logic and validation rules.
- Keeps development local-first and reversible.

When to migrate to Neo4j or another graph DB
- Graph exceeds 10k to 50k nodes or multi-user editing begins.
- Need transactional updates, concurrent writes, or remote access.
- Requirement for advanced graph query performance or visualization APIs.

Future GraphRAG integration (after Phase 1)
- Export a clean edge list and node metadata into a vector-ready format.
- Compute embeddings for summary + relations only.
- Use Graph + Vector hybrid retrieval: graph traversal narrows candidates, vector reranking surfaces best nodes.
- Introduce a vector store only after ontology validation stabilizes.

Phase 1 success criteria
- Node taxonomy consistent.
- Edge semantics valid.
- Validation rules catch errors early.
- Canonical queries are answerable via graph traversal.
