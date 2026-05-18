Bengaluru Node Classes — Phase 1

Objective: Define the core node classes for a Bengaluru transportation intelligence seed graph.

For each class: purpose, required metadata, optional metadata, relationship constraints, inheritance possibilities.

1) Corridor
- Purpose: Linear transport artery for movement and network dependency analysis.
- Required metadata: id, title, city, status, functional_class, owner_agency, tags, source_confidence.
- Optional metadata: length_m, lanes, typical_speed_kmph, modal_share, sensors, last_inspection_date.
- Relationship constraints: CONNECTS_TO Corridors; LOCATED_IN Urban Region; SERVES Transit Service; MONITORED_BY Sensor System; AFFECTED_BY Infrastructure Failure.
- Inheritance: Corridor -> Arterial, Collector, Local; Corridor -> FreightCorridor, TransitPriorityCorridor.

2) Asset
- Purpose: Physical infrastructure unit (bridge, station, signal, underpass).
- Required metadata: id, title, category, owner_agency, status, tags, source_confidence.
- Optional metadata: installation_date, condition_index, last_maintenance_date, expected_life_years, geo.
- Relationship constraints: LOCATED_IN Urban Region; OVERLAPS_WITH Corridor (where applicable); target of MAINTAINS and MONITORS; AFFECTED_BY Infrastructure Failure.
- Inheritance: Asset -> Bridge, RoadSegment, Station, Signal, Depot.

3) Agency
- Purpose: Governance or planning body with regulatory or ownership roles.
- Required metadata: id, title, jurisdiction, status, tags, source_confidence.
- Optional metadata: mandate, budget_programs, contact_url.
- Relationship constraints: OWNS Asset/Corridor; MAINTAINS Asset/Corridor; FUNDS Policies or Maintenance Events; target of REGULATED_BY edges from Operator/Transit Service.
- Inheritance: Agency -> Municipal, State, National, Regulator.

4) Operator
- Purpose: Entity that runs services (bus, metro, ride-hailing, paratransit).
- Required metadata: id, title, operator_type, operating_region, status, tags, source_confidence.
- Optional metadata: fleet_size, vehicle_types, fare_structure, performance_metrics.
- Relationship constraints: OPERATES Transit Service; DEPENDS_ON Corridor/Asset; REGULATED_BY Agency/Policy; FUNDED_BY Funding Mechanism.
- Inheritance: Operator -> PublicOperator, PrivateOperator, InformalOperator.

5) Policy
- Purpose: Policy or regulatory instrument affecting mobility or infrastructure.
- Required metadata: id, title, scope, issuing_agency, effective_date, status, tags, source_confidence.
- Optional metadata: summary, budget_implications, enforcement_mechanisms, sunset_clause.
- Relationship constraints: CONSTRAINS Corridor/Asset/Transit Service/Operator; FUNDED_BY Funding Mechanism; target of REGULATED_BY edges from Operator/Transit Service.
- Inheritance: Policy -> NationalPolicy, StatePolicy, CityPolicy.

6) Infrastructure Failure
- Purpose: Observed or hypothesized infrastructure failure pattern.
- Required metadata: id, title, failure_type, status, tags, source_confidence.
- Optional metadata: severity, onset_date, evidence_links.
- Relationship constraints: CAUSES Congestion Zone or Mobility Pattern; AFFECTS Corridor/Asset; CORRELATES_WITH Flooding Zone.
- Inheritance: Failure -> StructuralFailure, DrainageFailure, CapacityFailure.

7) Mobility Pattern
- Purpose: Recurrent movement behavior (commute, transfer, modal choice).
- Required metadata: id, title, pattern_type, status, tags, source_confidence.
- Optional metadata: peak_periods, modal_share, typical_od_pairs.
- Relationship constraints: DEPENDS_ON Transit Service/Corridor; CORRELATES_WITH Congestion Zone; IMPACTS Stakeholder.
- Inheritance: Pattern -> CommutePattern, FreightPattern, LastMilePattern.

8) Transit Service
- Purpose: Specific service line or route (metro line, bus route, airport bus).
- Required metadata: id, title, service_type, operator, status, tags, source_confidence.
- Optional metadata: headway, capacity, service_hours, fare_range.
- Relationship constraints: OPERATED_BY Operator; SERVES Urban Region/Stakeholder; DEPENDS_ON Corridor/Asset; REGULATED_BY Agency/Policy.
- Inheritance: TransitService -> MetroLine, BusRoute, FeederService, AirportService.

9) Sensor System
- Purpose: Monitoring system for traffic, safety, or flooding.
- Required metadata: id, title, sensor_type, owner_agency, status, tags, source_confidence.
- Optional metadata: coverage_area, data_frequency, data_access.
- Relationship constraints: MONITORS Corridor/Asset/Zone; DEPENDS_ON Funding Mechanism.
- Inheritance: SensorSystem -> CCTV, ANPR, FloodGauge, PavementSurvey.

10) Maintenance Event
- Purpose: Planned or executed maintenance activity.
- Required metadata: id, title, event_type, status, tags, source_confidence.
- Optional metadata: schedule_window, budget, contractor.
- Relationship constraints: DEPENDS_ON Asset/Corridor; FUNDED_BY Funding Mechanism; CONSTRAINS Transit Service or Corridor during event.
- Inheritance: MaintenanceEvent -> Inspection, Resurfacing, Desilting, SignalRetiming.

11) Congestion Zone
- Purpose: Spatial zone of recurring congestion.
- Required metadata: id, title, severity_level, status, tags, source_confidence.
- Optional metadata: peak_periods, average_speed_kmph.
- Relationship constraints: LOCATED_IN Urban Region; OVERLAPS_WITH Corridor; CAUSED_BY Failure/Pattern; IMPACTS Stakeholder.
- Inheritance: Zone -> CongestionZone (subclass of UrbanRegion zone).

12) Flooding Zone
- Purpose: Spatial zone of recurring flooding or waterlogging.
- Required metadata: id, title, severity_level, status, tags, source_confidence.
- Optional metadata: drainage_catchment, flood_frequency.
- Relationship constraints: LOCATED_IN Urban Region; OVERLAPS_WITH Corridor/Asset; CORRELATES_WITH Infrastructure Failure.
- Inheritance: Zone -> FloodingZone (subclass of UrbanRegion zone).

13) Stakeholder
- Purpose: Human or organizational group impacted by mobility system.
- Required metadata: id, title, stakeholder_type, status, tags, source_confidence.
- Optional metadata: population_size, influence_level.
- Relationship constraints: IMPACTED_BY Policy/Failure/Congestion; SERVED_BY Transit Service.
- Inheritance: Stakeholder -> CommuterGroup, OperatorGroup, ResidentGroup.

14) Funding Mechanism
- Purpose: Funding source or mechanism for projects or operations.
- Required metadata: id, title, mechanism_type, status, tags, source_confidence.
- Optional metadata: typical_amount_range, funding_cycle.
- Relationship constraints: FUNDS Policy/Operator/Asset/Maintenance Event.
- Inheritance: FundingMechanism -> Farebox, Tax, Loan, PPPAnnuity, Grant.

15) Urban Region
- Purpose: Spatial administrative or functional region.
- Required metadata: id, title, region_type, status, tags, source_confidence.
- Optional metadata: population, area_km2, boundary_geojson.
- Relationship constraints: target of LOCATED_IN edges from Corridor/Asset/Zone; CONNECTS_TO other regions; SERVED_BY Transit Service.
- Inheritance: UrbanRegion -> CityRegion, CorridorRegion, WardCluster.
