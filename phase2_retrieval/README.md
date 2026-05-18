Phase 2 Retrieval Infrastructure (Bengaluru)

Goal
- Build a lightweight hybrid retrieval layer over the frozen seed graph.
- Combine vector similarity with graph traversal and metadata filters.

Scope
- No ontology changes.
- No GraphRAG, agents, or databases beyond local Qdrant.

Files
- node_parser.py: parse node files and relations
- embedding_pipeline.py: serialize nodes and generate embeddings
- qdrant_index.py: create and populate Qdrant collection
- semantic_search.py: vector similarity search
- hybrid_retrieval.py: vector + graph expansion
- metrics_report.py: retrieval evaluation and metrics
- queries/: templates and evaluation examples

Usage (typical)
1) Serialize nodes and generate embeddings:
   python embedding_pipeline.py --config config.yaml --output output
2) Build Qdrant index:
   python qdrant_index.py --config config.yaml --embeddings output/embeddings.jsonl
3) Semantic search:
   python semantic_search.py --config config.yaml --query "flooding-prone congestion corridors"
4) Hybrid retrieval:
   python hybrid_retrieval.py --config config.yaml --query "corridors dependent on BMTC" --hops 1
5) Metrics and evaluation:
   python metrics_report.py --config config.yaml --examples queries/eval_examples.json

Notes
- Qdrant must be running locally at the URL in config.yaml.
- Use --dry-run in embedding_pipeline.py to validate parsing without model download.
