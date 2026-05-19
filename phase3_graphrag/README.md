Phase 3 GraphRAG Infrastructure (Bengaluru)

Goal
- Add graph-aware retrieval expansion and context assembly on top of Phase 2 semantic retrieval.
- Keep ontology and Phase 2 components unchanged.

Key scripts
- graphrag_retrieval.py: vector retrieval + graph expansion + context assembly
- eval_graphrag.py: evaluation report with expected coverage
- graphrag_utils.py: shared graph traversal and context utilities
- context_quality.py: context quality report for retrieval outputs

Inputs
- Graph root: ../seed_graph/bengaluru
- Qdrant collection: configured in config.yaml

Outputs
- output/context.json
- output/context.md
- output/context_quality.json
- output/context_quality.md
- reports/graphrag_eval.json

Usage
1) GraphRAG retrieval context:
   python graphrag_retrieval.py --config config.yaml --query "multimodal bottlenecks near Silk Board"
2) Evaluation report:
   python eval_graphrag.py --config config.yaml --examples ../phase2_retrieval/queries/eval_examples.json

Notes
- Uses Qdrant query_points for qdrant-client 1.18.0.
- No changes to ontology or graph data.
