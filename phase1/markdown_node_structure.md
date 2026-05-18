Markdown Node Structure — Phase 1

Goal: Standardize node files for Obsidian and graph parsing.

YAML frontmatter (required fields)
- type: one of the defined node classes
- id: unique slug, lowercase, hyphenated
- title: human-readable name
- city: Bengaluru
- status: active | planned | illustrative | hypothesized
- tags: list of lowercase tags
- source_confidence: low | medium | high
- created: YYYY-MM-DD

Optional fields
- aliases: [alt names]
- geo: {lat: , lon: }
- owner_agency: [[Agency]]
- operator: [[Operator]]
- policy_scope: national | state | city
- evidence_links: [urls]
- data_links: [urls]

Body structure
- Summary: 2-4 lines.
- Relations: list of edge statements with wikilinks.
- Notes: optional context or caveats.

Wikilink conventions
- Use [[Title]] links that match the node title.
- Use edge verbs in uppercase (OWNS, OPERATES, etc).
- Only use defined edge types.

Tagging standards
- Use class tag: class/corridor, class/asset, class/agency, etc.
- Use locality tags: city/bengaluru, region/orr, region/whitefield, region/hebbal.
- Use status tags: status/active, status/illustrative.

Embedding preparation strategy
- For embeddings, concatenate: title + summary + relations.
- Exclude raw YAML fields from embedding text.
- Store an embedding_ready flag when parsing is complete.

Example node
---
type: Corridor
id: corridor-blr-orr
title: Outer Ring Road
city: Bengaluru
status: active
tags: [class/corridor, city/bengaluru, region/orr]
source_confidence: medium
created: 2026-05-18
---
Summary: Primary orbital corridor connecting major IT employment clusters.
Relations:
- CONNECTS_TO -> [[Hosur Road]]
- CONNECTS_TO -> [[Old Madras Road]]
- OVERLAPS_WITH -> [[ORR IT Corridor Region]]
Notes: Jurisdiction overlaps multiple agencies; treat as multi-owner until validated.
