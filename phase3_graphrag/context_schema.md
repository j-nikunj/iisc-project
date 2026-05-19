GraphRAG Context Schema (Phase 3)

Output JSON (output/context.json)
{
  "query": "...",
  "vector_hits": [
    {"node_id": "...", "title": "...", "node_class": "...", "score": 0.0}
  ],
  "graph_expansion": [
    {"node_id": "...", "title": "...", "node_class": "...", "path": ["..."]}
  ],
  "context_text": "..."
}

Context assembly rules
- Vector hits come first, ordered by similarity score.
- Graph expansion follows, ordered by BFS depth and then title.
- Node details include title, node_class, summary, relations, and optional content.
