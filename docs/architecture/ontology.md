# Bengaluru Operational Ontology

The graph does not merely map physical geography; it maps **operational states and vulnerabilities**. The ontology is defined by explicit Node Classes and directional Edge Relationships.

## Node Classes
Nodes represent discrete operational environments or chokepoints.

* `congestion_corridor`: Arterial routes defined by volume saturation (e.g., `corr-orr-marathahalli`).
* `vulnerability_zone`: Exogenous shock points where environmental factors destroy infrastructure capacity (e.g., `flood-manyata`).
* `transfer_zone`: Multi-modal friction points where humans switch transit modes (e.g., `stress-silk-board`).
* `physical_constraint`: Engineering limitations enforcing mathematical throughput caps (e.g., `bottleneck-goraguntepalya`).
* `interchange_hub`: Massive distribution nodes for transit (e.g., `metro-majestic`).

## Directed Edge Relationships
Edges dictate causality. Traffic volume flows in one direction; cascading failures frequently travel in the opposite direction.

* `FEEDS_INTO`: Represents intended, healthy volume flow (Node A outputs traffic to Node B).
* `PROPAGATES_TO`: Represents upstream travel of a failure or shockwave (Spillback).
* `IMPACTS`: A broad causal link indicating exogenous disruption (e.g., Rain $\rightarrow$ Impacts $\rightarrow$ Underpass).
* `CREATES_TRANSFER_STRESS`: Links a surface failure to a transit node (Commuters abandoning roads for the Metro).
* `DEPENDS_ON`: Hierarchical infrastructure reliance.