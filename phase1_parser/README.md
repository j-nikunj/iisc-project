Phase 1 Parser — Bengaluru Seed Graph

Goal
- Parse the Obsidian-native node repository into a NetworkX MultiDiGraph.
- Validate ontology rules and output machine-readable artifacts.

Inputs
- Node repository: ../seed_graph/bengaluru

Outputs (default)
- output/graph.json
- output/nodes.json
- output/edges.json
- output/validation_report.json
- output/metrics.json
- reports/summary_report.md

Usage
- Install dependencies from requirements.txt
- Run the parser:
  python parser.py --root ../seed_graph/bengaluru --output output --reports reports

Notes
- No databases, embeddings, or external services are used in Phase 1.
- Edit the edge and node class lists inside parser.py if the ontology changes.
