Systems Map — India Transportation & Mobility (initial draft)

Date: 2026-05-18

Purpose: a high-level, graph-native systems map capturing nodes, interdependencies, flows, and feedback loops for India's transportation ecosystem.

Primary node groups:
- Modes: Road, Rail (passenger, freight), Metro/Transit, Intermediate Public Transport (IPT: autorickshaw, tempos), Two-wheelers, Non-motorized (walking, cycling), Aviation, Inland waterways, Coastal shipping
- Infrastructure: Roads (national/state/urban), Bridges, Tunnels, Rail tracks/stations, Terminals, Bus depots, Metro depots, Traffic management centers
- Governance: Central ministries (MoRTH, MoHUA, MoR), State transport departments, Municipal corporations, Urban local bodies, Transit agencies, Railways, Ports, Airports
- Operators: Public transit agencies, Private bus operators, Ride-hailing platforms, Freight operators, Logistics firms
- Users: Commuters (formal/informal), Shippers, Pedestrians, Cyclists, Vulnerable road users
- Markets & Economics: Fare regimes, Fuel & energy markets, Financing bodies (PFI, multilateral lenders), PPP structures
- Data & Sensing: Traffic sensors, ANPR/CCTV, Telecom traces, Farebox systems, ITS, Road condition sensors, SHM sensors
- Maintenance & Assets: Routine maintenance crews, Asset registries, Contractor networks, Procurement systems
- Institutions & Policy: Land-use planning authorities, Licensing & regulation bodies, Courts, Political actors
- Informal Systems: Paratransit networks, Informal freight aggregators, Last-mile delivery micro-actors
- External drivers: Urbanization, Vehicle manufacturing & supply chains, Fuel prices, Climate shocks, Demographic shifts

Key flows & relations (edges):
- Demand flows: users → modes (modal choice influenced by cost, availability, speed)
- Physical dependency: infrastructure → modes (e.g., bridges enable road/rail connectivity)
- Governance overlays: institutions → infrastructure & operators (planning, procurement, regulation)
- Financial flows: markets → infrastructure & operators (capex, opex, subsidies)
- Data flows: sensors & systems → operators & governance (monitoring, enforcement, planning)
- Feedback loops: poor maintenance → degraded service → reduced ridership → lower revenues → further underinvestment

High-leverage subgraphs to model first:
1. Urban bus ecosystem: municipal planning → bus operator incentives → route economics → commuter behavior
2. Road safety & SHM: traffic management → sensor network → accident hotspots → infrastructure maintenance
3. Freight corridors: port/rail/road interfaces → last-mile logistics → trucker incentives → freight modal split

Graph modeling notes:
- Represent each node as markdown note with metadata (geo, tags, provenance, embeddings).
- Use edge types for causal_relation, dependency_chain, governance_relation, spatial_connectivity.
- Capture temporal attributes (policy enactment dates, funding cycles, maintenance histories).

Next actions:
- Convert each primary node group into node templates (file scaffolds).
- Populate the urban bus subgraph with actors, revenue models, constraints.
- Start encoding causal feedback loops as explicit edges in `graph_schema.md`.

References / sources to gather: urban mobility plans, NITI Aayog reports, MoRTH datasets, state transport policies, academic literature on paratransit and informal logistics.
