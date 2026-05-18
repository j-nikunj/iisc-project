Root-Cause Hierarchy — India Transportation (initial draft)

Date: 2026-05-18

Purpose: Layered mapping from symptoms → proximate causes → structural/root causes, with feedback loops and validation checks.

Symptoms (observable):
- Chronic traffic congestion in cities
- High road fatality rates
- Poor reliability of public transit
- Under-maintained bridges/roads
- Modal imbalance (private vehicles dominant)
- Inefficient freight last-mile movements

Proximate causes:
- Capacity gaps (insufficient transit frequency or fleet)
- Fragmented planning across agencies
- Underfunding of maintenance (capex bias)
- Weak enforcement (traffic rules, axle loads)
- Inadequate data & monitoring
- Poor farebox recovery and unsustainable transit business models
- Informal sector exclusion from formal planning

Structural / root causes:
- Institutional fragmentation: misaligned incentives across ministries, states, and local bodies
- Political-economy cycles: short-term electoral incentives bias capex toward visible projects
- Procurement and contracting pathologies: cost-plus, low accountability, contractor capture
- Financing architecture misalignment: lack of predictable opex funding, reliance on project loans
- Data poverty: no standardized asset registries, siloed data, poor interoperability
- Capacity constraints: technical, managerial, and maintenance workforce shortages in local bodies
- Regulatory gaps: unclear roles for paratransit, difficulty integrating informal actors
- Land-use and urban form: sprawl increases travel demand and private vehicle dependence

Feedback loops (examples):
- Visibility loop: political preference for new visible infrastructure → neglect of maintenance → asset deterioration → demand for new projects
- Revenue loop: falling transit ridership → lower fare revenue → service cuts → further ridership loss
- Enforcement loop: weak axle-load enforcement → road damage → higher maintenance costs → deferred maintenance

Validation & metrics:
- Use asset condition indices, fatalities per VKT, on-time performance, farebox recovery ratios, maintenance backlog estimates
- Triangulate with data sources: satellite imagery, OSMnx road networks, traffic sensor feeds, state PWD records

Next steps:
- Map concrete examples (city- and state-level case studies) to each structural cause
- Encode causal relations as edges in `graph_schema.md` and instantiate nodes for policy levers
- Design indicators for each feedback loop to detect early-warning signals
