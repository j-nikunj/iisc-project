Bengaluru Seed Graph — Obsidian Node Repository

Purpose
- File-based, graph-native repository for Phase 1 Bengaluru transportation seed graph.
- Optimized for Obsidian traversal, parser extraction, and future GraphRAG indexing.

Folder layout
- corridors/
- assets/
- agencies/
- operators/
- policies/
- congestion_zones/
- flooding_zones/
- infrastructure_failures/
- transit_services/
- stakeholders/
- urban_regions/
- sensor_systems/
- maintenance_events/
- mobility_patterns/
- funding_mechanisms/

Parser-oriented conventions
1) File naming
- File name MUST equal the node title (case preserved), plus .md.
- Avoid forbidden characters for Windows filenames.

2) Node ID conventions
- `id` is stable, lowercase, hyphenated, and unique (e.g., corridor-blr-orr).
- `node_class` uses snake_case (e.g., infrastructure_failure).

3) Edge declaration syntax
- Use `Relations:` section with list items in the form:
  - EDGE_TYPE -> [[Target Node Title]]
- Edge types must match the Phase 1 taxonomy.

4) Wikilink normalization
- Wikilinks must match the target node title exactly.
- Aliases are declared in `aliases` frontmatter only.

5) Metadata serialization
- YAML frontmatter is required for every node.
- Required fields: type, node_class, id, title, city, status, tags, source_confidence, created, updated.
- `geo` field must exist (null or {lat, lon}).

6) Summary and Notes
- `Summary:` is required in the body.
- `Notes:` optional, used for caveats and provenance hints.

Parser readiness
- A future parser can traverse folders, parse frontmatter, extract Relations, and build a NetworkX graph.
- Ontology validation rules should be applied after parsing.
