Symptom → Proximate → Structural Cause Framework — India Transportation (with city examples)

Date: 2026-05-18

Purpose: Detailed mapping from observable symptoms to proximate causes to structural/root causes, with concrete city-level examples, metrics, graph nodes/edges to instantiate in the knowledge graph, and candidate intervention levers.

Framework template (per symptom):
- Symptom (observable metric)
- Proximate causes (direct mechanisms)
- Structural/root causes (institutional, political-economy, data, finance)
- Feedback loops (reinforcing/balancing)
- Graph nodes to create (node types)
- Graph edges to create (edge types + direction)
- Early-warning indicators / metrics
- Pilot intervention levers

1) Chronic urban traffic congestion — Example: Bengaluru
- Symptom: Peak-hour average travel speeds < 15 km/h on primary corridors; increasing delay index.
- Proximate causes: High private vehicle mode share; insufficient public transit capacity; poor last-mile connectivity; traffic signal timing inefficiencies.
- Structural/root causes: Land-use sprawl increasing trip lengths; lack of integrated transport-landuse planning; weak revenue models for bus operators; fragmented institutional responsibility between state roads, city traffic police, and municipal transport.
- Feedback loops: Congestion → perceived unreliability of buses → modal shift to private vehicles → more congestion.
- Graph nodes: `Corridor`, `BusService`, `PrivateVehicleFleet`, `TrafficSignalController`, `LandUseZone`, `CommuterSegment`.
- Graph edges: `demand_flow (CommuterSegment→Mode)`, `service_capacity(BusService→Corridor)`, `infrastructure_ownership(City→Corridor)`, `policy_influence(MunicipalBudget→BusService)`.
- Early-warning indicators: rising modal share of two-wheelers and cars; declining bus load factors; increasing bus headway variance.
- Pilot levers: performance-based bus contracts; dedicated bus lanes on targeted corridors; last-mile micro-transit integrations; corridor-level adaptive signal control.

2) High road fatalities — Example: Delhi & Pune
- Symptom: Road traffic fatality rate per 100k population > national average; hotspots persistent despite interventions.
- Proximate causes: High vehicle speeds on mixed streets; unsafe infrastructure for pedestrians; lack of enforcement of helmet/seatbelt laws; poor post-crash response.
- Structural/root causes: Institutional fragmentation between traffic enforcement and urban planners; revenue structures that deprioritize safe street design; weak data systems for crash causation analysis.
- Feedback loops: High fatalities increase political pressure for quick fixes (speed bumps, signage) rather than systemic redesign.
- Graph nodes: `CrashHotspot`, `EnforcementUnit`, `RoadSegment`, `EmergencyResponseUnit`.
- Graph edges: `causal_relation(RoadDesign→CrashRisk)`, `enforcement_coverage(EnforcementUnit→RoadSegment)`, `response_time(EmergencyResponseUnit→CrashHotspot)`.
- Early-warning indicators: clustering of minor-injury crashes; increasing vehicle speeds on urban arterials; declining EMS response times.
- Pilot levers: targeted Safe Systems redesign on hotspot segments; strengthened EMS dispatching with geo-routing; automated speed enforcement with revenue ring-fencing for safety upgrades.

3) Unreliable suburban/urban rail service — Example: Mumbai suburban rail
- Symptom: Peak passenger load factors > 300%; frequent delays and cascading cancellations.
- Proximate causes: Infrastructure capacity constraints; rolling stock shortages; signaling limitations; insufficient maintenance windows.
- Structural/root causes: Historic underinvestment in operational resilience vis-à-vis expansion; misaligned financing that funds new lines but not lifecycle O&M; governance split between central railways and local metropolitan authorities.
- Feedback loops: Overcrowding → crowding-induced delays → reduced perceived reliability → demand surge to alternative (often road) modes during disruptions.
- Graph nodes: `Station`, `TrackSegment`, `RollingStockFleet`, `SignalingSystem`, `MaintenanceDepot`.
- Graph edges: `capacity_constraint(TrackSegment→Throughput)`, `fleet_availability(RollingStockFleet→ServiceFrequency)`, `maintenance_dependency(MaintenanceDepot→RollingStockFleet)`.
- Early-warning indicators: rising unscheduled maintenance incidents; train punctuality drops; fleet age distribution skewed older.
- Pilot levers: night-time maintenance windows with temporary bus bridges; targeted procurement for high-cadence rolling stock; signaling modernization pilots with ROI tracking.

4) Under-maintained bridges and pavements — Example: State PWD networks (case: Andhra Pradesh)
- Symptom: Increasing proportion of roads/bridges rated poor in asset condition surveys; frequent emergency repairs; higher unit repair costs.
- Proximate causes: Deferred maintenance; weak contractor performance bonds; lack of asset registry and condition-based maintenance scheduling.
- Structural/root causes: Fiscal cycles favor new capital spending; no dedicated O&M funding streams; procurement favoring low upfront cost over lifecycle cost.
- Feedback loops: Deferred maintenance → accelerated deterioration → higher future costs → fiscal pressure leading to more deferred maintenance.
- Graph nodes: `Asset`, `MaintenanceContract`, `BudgetLine`, `InspectionRecord`.
- Graph edges: `funding_flow(BudgetLine→MaintenanceContract)`, `condition_update(InspectionRecord→Asset)`, `contract_performance(MaintenanceContract→AssetCondition)`.
- Early-warning indicators: increasing time-gap between scheduled inspections; rising emergency repair spend proportion; mismatch between planned and executed maintenance.
- Pilot levers: condition-based maintenance pilots with SHM sensors; ring-fenced maintenance funds; procurement reform to emphasize lifecycle costing.

5) Inefficient last-mile freight movements — Example: Urban consolidation issues in Chennai
- Symptom: High empty-trip ratios for light commercial vehicles; high terminal dwell times; congestion from ad-hoc loading zones.
- Proximate causes: Lack of consolidation centers; poor loading/unloading infrastructure; regulatory hassles (permits, time-window restrictions); fragmented information on freight demand.
- Structural/root causes: Lack of integrated urban freight policy; stakeholder fragmentation between port/rail authorities and city agencies; absence of market mechanisms for consolidation.
- Feedback loops: High last-mile cost → preference for smaller, time-flexible carriers → fragmentation persists.
- Graph nodes: `FreightNode`, `ConsolidationCenter`, `Depot`, `TruckOperator`.
- Graph edges: `flow(FreightNode→Depot)`, `terminal_utilization(Depot→DwellTime)`, `policy_barrier(CityRegulation→ConsolidationCenter)`.
- Early-warning indicators: rising per-tonne last-mile costs; occupancy rates at ad-hoc loading zones; average door-to-door delivery time variance.
- Pilot levers: micro-consolidation hubs; time-window-based curb pricing; digital freight marketplaces with real-time matching.

Graph encoding guidance
- Encode each symptom, proximate cause, and structural cause as nodes with `type` tags and `evidence` metadata (datasets, reports, timestamps).
- Use `causal_relation` edges directed from causes → effects; annotate edges with confidence scores and evidence citations.
- Capture temporal edges (policy enactment, funding cycles) as timestamped relations to support temporal queries.
- Represent feedback loops as small cyclical subgraphs and compute centrality to find dominant reinforcing loops.

Validation & metrics
- Attach numeric indicators as node properties (e.g., `avg_speed_kmph`, `fatalities_per_100k`, `farebox_recovery`) for graph-filtered analytics.
- Link nodes to external data sources (MoRTH crash database, transport surveys, OSM extracts) in `provenance`.

Next steps
- Instantiate node templates for each symptom and for the `Corridor`, `Asset`, `Operator`, `Policy` entity types in the `iisc project` folder.
- Gather city-level datasets (e.g., bus schedules, crash records, fleet registries) to populate evidence fields.
- Design graph queries for detecting the listed early-warning indicators.
