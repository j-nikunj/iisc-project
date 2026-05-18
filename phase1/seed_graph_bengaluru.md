Bengaluru Seed Graph — Phase 1 (Manual, Illustrative)

Purpose: Manually curated seed graph to validate ontology, edges, and GraphRAG query patterns.

Note: Some nodes are illustrative or hypothesized. All relations should be validated with sources in later phases.

Node index (by class)
- Corridors: [[Outer Ring Road]], [[Hosur Road]], [[Old Madras Road]], [[Airport Road (Bellary Road)]], [[Sarjapur Road]], [[Whitefield Main Road]], [[Bannerghatta Road]]
- Assets: [[Silk Board Junction]], [[Hebbal Flyover]], [[KR Puram Bridge]], [[Baiyappanahalli Metro Depot]], [[Silk Board Underpass]], [[Mahadevapura Flyover]], [[KR Puram Underpass]]
- Agencies: [[BBMP]], [[DULT]], [[BMRCL]], [[Bangalore Traffic Police]]
- Operators: [[BMTC]], [[BMRCL Operations]], [[Ola Mobility]], [[Auto Rickshaw Operators - Bengaluru]]
- Policies: [[National Urban Transport Policy 2014]], [[Karnataka Electric Vehicle Policy 2021-2026]], [[Bengaluru Bus Priority Policy (Illustrative)]]
- Infrastructure Failures: [[ORR Pavement Rutting Pattern]], [[Silk Board Spillback Failure]], [[Hebbal Flyover Bearing Wear (Hypothesized)]], [[Koramangala Valley Drainage Overload]]
- Mobility Patterns: [[Peak-hour IT Corridor Commute]], [[Airport Commute Pattern]], [[Two-wheeler Dominant Last-mile]], [[Metro Feeder Transfer Pattern]]
- Transit Services: [[Namma Metro Purple Line]], [[Namma Metro Green Line]], [[BMTC 500D ORR]], [[Vayu Vajra KIA-9]], [[Metro Feeder FM-1 (Illustrative)]]
- Sensor Systems: [[Silk Board CCTV Cluster]], [[ORR ANPR Camera Network (Illustrative)]], [[Koramangala Flood Gauge (Illustrative)]]
- Maintenance Events: [[ORR Resurfacing Cycle (Illustrative)]], [[Hebbal Flyover Inspection (Illustrative)]], [[Pre-monsoon Desilting Drive (Illustrative)]], [[Silk Board Signal Retiming (Illustrative)]]
- Congestion Zones: [[Silk Board Congestion Zone]], [[Hebbal Congestion Zone]], [[KR Puram Congestion Zone]], [[Marathahalli Congestion Zone]]
- Flooding Zones: [[Silk Board Underpass Flooding Zone]], [[ORR-Bellandur Flooding Zone]], [[Whitefield Underpass Flooding Zone]]
- Stakeholders: [[IT Corridor Commuters]], [[Informal Auto Drivers]], [[Freight Operators - Bengaluru]], [[East Bengaluru Residents Associations]]
- Funding Mechanisms: [[Farebox Revenue]], [[State Budget Grant]], [[Multilateral Loan - Metro]]
- Urban Regions: [[Bengaluru Urban Region]], [[ORR IT Corridor Region]], [[Whitefield Region]], [[Hebbal Region]]

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
Summary: Primary orbital corridor linking major employment clusters and ring road junctions.
Relations:
- CONNECTS_TO -> [[Hosur Road]]
- CONNECTS_TO -> [[Old Madras Road]]
- CONNECTS_TO -> [[Sarjapur Road]]
- LOCATED_IN -> [[ORR IT Corridor Region]]
- OVERLAPS_WITH -> [[Silk Board Congestion Zone]]
- OVERLAPS_WITH -> [[Marathahalli Congestion Zone]]

---

type: Corridor
id: corridor-blr-hosur-road
title: Hosur Road
city: Bengaluru
status: active
tags: [class/corridor, city/bengaluru, region/south]
source_confidence: medium
created: 2026-05-18
---
Summary: South corridor connecting central Bengaluru to industrial and peri-urban areas.
Relations:
- CONNECTS_TO -> [[Outer Ring Road]]
- OVERLAPS_WITH -> [[Silk Board Congestion Zone]]
- LOCATED_IN -> [[Bengaluru Urban Region]]

---

type: Corridor
id: corridor-blr-old-madras-road
title: Old Madras Road
city: Bengaluru
status: active
tags: [class/corridor, city/bengaluru, region/east]
source_confidence: medium
created: 2026-05-18
---
Summary: East corridor linking CBD to KR Puram and Whitefield.
Relations:
- CONNECTS_TO -> [[Outer Ring Road]]
- OVERLAPS_WITH -> [[KR Puram Congestion Zone]]
- LOCATED_IN -> [[Bengaluru Urban Region]]

---

type: Corridor
id: corridor-blr-airport-road
title: Airport Road (Bellary Road)
city: Bengaluru
status: active
tags: [class/corridor, city/bengaluru, region/north]
source_confidence: medium
created: 2026-05-18
---
Summary: North corridor connecting CBD to airport and Hebbal.
Relations:
- CONNECTS_TO -> [[Hebbal Region]]
- OVERLAPS_WITH -> [[Hebbal Congestion Zone]]
- LOCATED_IN -> [[Bengaluru Urban Region]]

---

type: Corridor
id: corridor-blr-sarjapur-road
title: Sarjapur Road
city: Bengaluru
status: active
tags: [class/corridor, city/bengaluru, region/southeast]
source_confidence: medium
created: 2026-05-18
---
Summary: Southeast corridor connecting ORR to Sarjapur and peripheral growth areas.
Relations:
- CONNECTS_TO -> [[Outer Ring Road]]
- OVERLAPS_WITH -> [[Marathahalli Congestion Zone]]
- LOCATED_IN -> [[Bengaluru Urban Region]]

---

type: Corridor
id: corridor-blr-whitefield-main-road
title: Whitefield Main Road
city: Bengaluru
status: active
tags: [class/corridor, city/bengaluru, region/whitefield]
source_confidence: medium
created: 2026-05-18
---
Summary: Key corridor within Whitefield, connecting tech parks and residential clusters.
Relations:
- CONNECTS_TO -> [[Old Madras Road]]
- LOCATED_IN -> [[Whitefield Region]]
- OVERLAPS_WITH -> [[Whitefield Underpass Flooding Zone]]

---

type: Corridor
id: corridor-blr-bannerghatta-road
title: Bannerghatta Road
city: Bengaluru
status: active
tags: [class/corridor, city/bengaluru, region/south]
source_confidence: medium
created: 2026-05-18
---
Summary: South corridor connecting residential and institutional zones.
Relations:
- LOCATED_IN -> [[Bengaluru Urban Region]]
- OVERLAPS_WITH -> [[Silk Board Congestion Zone]]

---

type: Asset
id: asset-blr-silk-board-junction
title: Silk Board Junction
city: Bengaluru
status: active
tags: [class/asset, asset/junction, city/bengaluru, region/south]
source_confidence: medium
created: 2026-05-18
---
Summary: Major multi-corridor junction linking ORR, Hosur Road, and BTM areas.
Relations:
- LOCATED_IN -> [[Bengaluru Urban Region]]
- OVERLAPS_WITH -> [[Silk Board Congestion Zone]]

---

type: Asset
id: asset-blr-hebbal-flyover
title: Hebbal Flyover
city: Bengaluru
status: active
tags: [class/asset, asset/flyover, city/bengaluru, region/hebbal]
source_confidence: medium
created: 2026-05-18
---
Summary: Flyover near Hebbal junction carrying northbound traffic flows.
Relations:
- LOCATED_IN -> [[Hebbal Region]]
- OVERLAPS_WITH -> [[Hebbal Congestion Zone]]

---

type: Asset
id: asset-blr-kr-puram-bridge
title: KR Puram Bridge
city: Bengaluru
status: active
tags: [class/asset, asset/bridge, city/bengaluru, region/east]
source_confidence: medium
created: 2026-05-18
---
Summary: Bridge enabling east corridor connectivity near KR Puram.
Relations:
- LOCATED_IN -> [[Bengaluru Urban Region]]
- OVERLAPS_WITH -> [[KR Puram Congestion Zone]]

---

type: Asset
id: asset-blr-baiyappanahalli-depot
title: Baiyappanahalli Metro Depot
city: Bengaluru
status: active
tags: [class/asset, asset/depot, city/bengaluru, region/east]
source_confidence: medium
created: 2026-05-18
---
Summary: Metro depot supporting rolling stock operations for east corridor services.
Relations:
- LOCATED_IN -> [[Bengaluru Urban Region]]

---

type: Asset
id: asset-blr-silk-board-underpass
title: Silk Board Underpass
city: Bengaluru
status: active
tags: [class/asset, asset/underpass, city/bengaluru, region/south]
source_confidence: medium
created: 2026-05-18
---
Summary: Underpass near Silk Board junction.
Relations:
- LOCATED_IN -> [[Bengaluru Urban Region]]
- OVERLAPS_WITH -> [[Silk Board Underpass Flooding Zone]]

---

type: Asset
id: asset-blr-mahadevapura-flyover
title: Mahadevapura Flyover
city: Bengaluru
status: active
tags: [class/asset, asset/flyover, city/bengaluru, region/orr]
source_confidence: medium
created: 2026-05-18
---
Summary: Flyover on the ORR corridor near Mahadevapura.
Relations:
- LOCATED_IN -> [[ORR IT Corridor Region]]
- OVERLAPS_WITH -> [[Marathahalli Congestion Zone]]

---

type: Asset
id: asset-blr-kr-puram-underpass
title: KR Puram Underpass
city: Bengaluru
status: active
tags: [class/asset, asset/underpass, city/bengaluru, region/east]
source_confidence: medium
created: 2026-05-18
---
Summary: Underpass facilitating traffic flows near KR Puram.
Relations:
- LOCATED_IN -> [[Bengaluru Urban Region]]
- OVERLAPS_WITH -> [[KR Puram Congestion Zone]]

---

type: Agency
id: agency-bbmp
title: BBMP
city: Bengaluru
status: active
tags: [class/agency, city/bengaluru, governance/municipal]
source_confidence: medium
created: 2026-05-18
---
Summary: Municipal corporation responsible for urban services and infrastructure.
Relations:
- OWNS -> [[Silk Board Underpass]]
- MAINTAINS -> [[Silk Board Underpass]]
- MAINTAINS -> [[Mahadevapura Flyover]]
- MAINTAINS -> [[Pre-monsoon Desilting Drive (Illustrative)]]

---

type: Agency
id: agency-dult
title: DULT
city: Bengaluru
status: active
tags: [class/agency, city/bengaluru, governance/state]
source_confidence: medium
created: 2026-05-18
---
Summary: Urban transport directorate coordinating policy and planning.
Notes: Inbound relations via REGULATED_BY from operators.

---

type: Agency
id: agency-bmrcl
title: BMRCL
city: Bengaluru
status: active
tags: [class/agency, city/bengaluru, governance/state]
source_confidence: medium
created: 2026-05-18
---
Summary: Metro rail implementing agency for Bengaluru.
Relations:
- OWNS -> [[Baiyappanahalli Metro Depot]]


---

type: Agency
id: agency-btp
title: Bangalore Traffic Police
city: Bengaluru
status: active
tags: [class/agency, city/bengaluru, governance/traffic]
source_confidence: medium
created: 2026-05-18
---
Summary: Traffic enforcement and signal management agency.
Relations:
- MAINTAINS -> [[Silk Board Signal Retiming (Illustrative)]]

---

type: Operator
id: operator-bmtc
title: BMTC
city: Bengaluru
status: active
tags: [class/operator, operator/public, city/bengaluru]
source_confidence: high
created: 2026-05-18
---
Summary: Public bus operator for Bengaluru.
Relations:
- OPERATES -> [[BMTC 500D ORR]]
- OPERATES -> [[Vayu Vajra KIA-9]]
- REGULATED_BY -> [[DULT]]
- REGULATED_BY -> [[National Urban Transport Policy 2014]]

---

type: Operator
id: operator-bmrcl-ops
title: BMRCL Operations
city: Bengaluru
status: active
tags: [class/operator, operator/public, city/bengaluru]
source_confidence: high
created: 2026-05-18
---
Summary: Metro operations unit responsible for service delivery.
Relations:
- OPERATES -> [[Namma Metro Purple Line]]
- OPERATES -> [[Namma Metro Green Line]]
- REGULATED_BY -> [[BMRCL]]
- REGULATED_BY -> [[National Urban Transport Policy 2014]]

---

type: Operator
id: operator-ola
title: Ola Mobility
city: Bengaluru
status: active
tags: [class/operator, operator/private, city/bengaluru]
aliases: [Ola]
source_confidence: medium
created: 2026-05-18
---
Summary: Ride-hailing operator with high demand at peak hours.
Relations:
- REGULATED_BY -> [[DULT]]
- REGULATED_BY -> [[Bangalore Traffic Police]]
- REGULATED_BY -> [[Karnataka Electric Vehicle Policy 2021-2026]]

---

type: Operator
id: operator-auto-union
title: Auto Rickshaw Operators - Bengaluru
city: Bengaluru
status: active
tags: [class/operator, operator/informal, city/bengaluru]
source_confidence: medium
created: 2026-05-18
---
Summary: Informal paratransit operators serving last-mile connectivity.
Relations:
- REGULATED_BY -> [[Bangalore Traffic Police]]

---

type: Policy
id: policy-nutp-2014
title: National Urban Transport Policy 2014
city: Bengaluru
status: active
tags: [class/policy, scope/national]
source_confidence: high
created: 2026-05-18
---
Summary: National policy framework guiding urban transport planning.
Relations:
- CONSTRAINS -> [[BMTC 500D ORR]]

---

type: Policy
id: policy-karnataka-ev-2021
title: Karnataka Electric Vehicle Policy 2021-2026
city: Bengaluru
status: active
tags: [class/policy, scope/state]
aliases: [Karnataka EV Policy]
source_confidence: medium
created: 2026-05-18
---
Summary: State policy shaping EV adoption and incentives.
Relations:
- CONSTRAINS -> [[Ola Mobility]]

---

type: Policy
id: policy-blr-bus-priority
title: Bengaluru Bus Priority Policy (Illustrative)
city: Bengaluru
status: illustrative
tags: [class/policy, scope/city, status/illustrative]
source_confidence: low
created: 2026-05-18
---
Summary: Illustrative policy for prioritizing bus lanes and signal priority.
Relations:
- CONSTRAINS -> [[Outer Ring Road]]
- CONSTRAINS -> [[BMTC 500D ORR]]

---

type: Infrastructure Failure
id: failure-orr-pavement-rutting
title: ORR Pavement Rutting Pattern
city: Bengaluru
status: hypothesized
tags: [class/failure, failure/pavement, region/orr]
source_confidence: low
created: 2026-05-18
---
Summary: Hypothesized pavement rutting due to heavy loads and maintenance delays.
Relations:
- CAUSES -> [[Marathahalli Congestion Zone]]
- CONSTRAINS -> [[BMTC 500D ORR]]

---

type: Infrastructure Failure
id: failure-silk-board-spillback
title: Silk Board Spillback Failure
city: Bengaluru
status: hypothesized
tags: [class/failure, failure/capacity, region/south]
source_confidence: low
created: 2026-05-18
---
Summary: Recurrent queue spillbacks causing network-wide delays.
Relations:
- CAUSES -> [[Silk Board Congestion Zone]]
- IMPACTS -> [[IT Corridor Commuters]]

---

type: Infrastructure Failure
id: failure-hebbal-bearing-wear
title: Hebbal Flyover Bearing Wear (Hypothesized)
city: Bengaluru
status: hypothesized
tags: [class/failure, failure/structural, region/hebbal]
source_confidence: low
created: 2026-05-18
---
Summary: Illustrative structural wear risk for lifecycle monitoring tests.
Relations:
- CAUSES -> [[Hebbal Congestion Zone]]
- CONSTRAINS -> [[Airport Road (Bellary Road)]]

---

type: Infrastructure Failure
id: failure-koramangala-drainage-overload
title: Koramangala Valley Drainage Overload
city: Bengaluru
status: hypothesized
tags: [class/failure, failure/drainage, region/south]
source_confidence: low
created: 2026-05-18
---
Summary: Overloaded drainage catchment contributing to local flooding.
Relations:
- CAUSES -> [[ORR-Bellandur Flooding Zone]]
- CORRELATES_WITH -> [[Silk Board Underpass Flooding Zone]]

---

type: Mobility Pattern
id: pattern-peak-hour-it-commute
title: Peak-hour IT Corridor Commute
city: Bengaluru
status: active
tags: [class/pattern, pattern/commute, region/orr]
source_confidence: medium
created: 2026-05-18
---
Summary: Concentrated morning and evening commute toward ORR employment clusters.
Relations:
- CORRELATES_WITH -> [[Silk Board Congestion Zone]]
- CORRELATES_WITH -> [[Marathahalli Congestion Zone]]
- DEPENDS_ON -> [[BMTC 500D ORR]]

---

type: Mobility Pattern
id: pattern-airport-commute
title: Airport Commute Pattern
city: Bengaluru
status: active
tags: [class/pattern, pattern/commute, region/north]
source_confidence: medium
created: 2026-05-18
---
Summary: Airport access travel from CBD and ORR areas to KIA.
Relations:
- DEPENDS_ON -> [[Airport Road (Bellary Road)]]
- CORRELATES_WITH -> [[Hebbal Congestion Zone]]
- DEPENDS_ON -> [[Vayu Vajra KIA-9]]

---

type: Mobility Pattern
id: pattern-two-wheeler-last-mile
title: Two-wheeler Dominant Last-mile
city: Bengaluru
status: active
tags: [class/pattern, pattern/lastmile, city/bengaluru]
source_confidence: medium
created: 2026-05-18
---
Summary: High two-wheeler usage for last-mile connectivity across zones.
Relations:
- CORRELATES_WITH -> [[Marathahalli Congestion Zone]]

---

type: Mobility Pattern
id: pattern-metro-feeder-transfer
title: Metro Feeder Transfer Pattern
city: Bengaluru
status: active
tags: [class/pattern, pattern/transfer, city/bengaluru]
source_confidence: medium
created: 2026-05-18
---
Summary: Transfers between metro stations and feeder buses or autos.
Relations:
- DEPENDS_ON -> [[Namma Metro Purple Line]]
- DEPENDS_ON -> [[Metro Feeder FM-1 (Illustrative)]]

---

type: Transit Service
id: service-metro-purple-line
title: Namma Metro Purple Line
city: Bengaluru
status: active
tags: [class/transit_service, mode/metro, city/bengaluru]
source_confidence: high
created: 2026-05-18
---
Summary: East-west metro service connecting Baiyappanahalli to central corridors.
Relations:
- DEPENDS_ON -> [[Baiyappanahalli Metro Depot]]
- SERVES -> [[Bengaluru Urban Region]]
- FUNDED_BY -> [[Multilateral Loan - Metro]]

---

type: Transit Service
id: service-metro-green-line
title: Namma Metro Green Line
city: Bengaluru
status: active
tags: [class/transit_service, mode/metro, city/bengaluru]
source_confidence: high
created: 2026-05-18
---
Summary: North-south metro service connecting key urban zones.
Relations:
- SERVES -> [[Bengaluru Urban Region]]
- FUNDED_BY -> [[Multilateral Loan - Metro]]

---

type: Transit Service
id: service-bmtc-500d
title: BMTC 500D ORR
city: Bengaluru
status: active
tags: [class/transit_service, mode/bus, region/orr]
source_confidence: medium
created: 2026-05-18
---
Summary: Bus service operating along the ORR corridor.
Relations:
- DEPENDS_ON -> [[Outer Ring Road]]
- SERVES -> [[ORR IT Corridor Region]]

---

type: Transit Service
id: service-vayu-vajra-kia9
title: Vayu Vajra KIA-9
city: Bengaluru
status: active
tags: [class/transit_service, mode/airport_bus, region/north]
source_confidence: medium
created: 2026-05-18
---
Summary: Airport bus service connecting city hubs to KIA.
Relations:
- DEPENDS_ON -> [[Airport Road (Bellary Road)]]
- SERVES -> [[Bengaluru Urban Region]]

---

type: Transit Service
id: service-metro-feeder-fm1
title: Metro Feeder FM-1 (Illustrative)
city: Bengaluru
status: illustrative
tags: [class/transit_service, mode/feeder, status/illustrative]
source_confidence: low
created: 2026-05-18
---
Summary: Illustrative feeder route for metro connectivity.
Relations:
- DEPENDS_ON -> [[Whitefield Main Road]]
- SERVES -> [[Whitefield Region]]

---

type: Sensor System
id: sensor-silk-board-cctv
title: Silk Board CCTV Cluster
city: Bengaluru
status: active
tags: [class/sensor, sensor/cctv, region/south]
source_confidence: medium
created: 2026-05-18
---
Summary: CCTV cluster monitoring traffic flows at Silk Board junction.
Relations:
- MONITORS -> [[Silk Board Congestion Zone]]
- MONITORS -> [[Silk Board Junction]]

---

type: Sensor System
id: sensor-orr-anpr
title: ORR ANPR Camera Network (Illustrative)
city: Bengaluru
status: illustrative
tags: [class/sensor, sensor/anpr, region/orr, status/illustrative]
source_confidence: low
created: 2026-05-18
---
Summary: Illustrative ANPR network for corridor travel time monitoring.
Relations:
- MONITORS -> [[Outer Ring Road]]
- MONITORS -> [[Marathahalli Congestion Zone]]

---

type: Sensor System
id: sensor-koramangala-flood-gauge
title: Koramangala Flood Gauge (Illustrative)
city: Bengaluru
status: illustrative
tags: [class/sensor, sensor/flood, region/south, status/illustrative]
source_confidence: low
created: 2026-05-18
---
Summary: Illustrative gauge to monitor drainage levels in Koramangala valley.
Relations:
- MONITORS -> [[ORR-Bellandur Flooding Zone]]

---

type: Maintenance Event
id: maintenance-orr-resurfacing
title: ORR Resurfacing Cycle (Illustrative)
city: Bengaluru
status: illustrative
tags: [class/maintenance_event, maintenance/resurfacing, region/orr]
source_confidence: low
created: 2026-05-18
---
Summary: Illustrative resurfacing cycle for ORR segments.
Relations:
- DEPENDS_ON -> [[Outer Ring Road]]
- CONSTRAINS -> [[BMTC 500D ORR]]
- FUNDED_BY -> [[State Budget Grant]]

---

type: Maintenance Event
id: maintenance-hebbal-inspection
title: Hebbal Flyover Inspection (Illustrative)
city: Bengaluru
status: illustrative
tags: [class/maintenance_event, maintenance/inspection, region/hebbal]
source_confidence: low
created: 2026-05-18
---
Summary: Illustrative inspection for flyover structural health.
Relations:
- DEPENDS_ON -> [[Hebbal Flyover]]
- CONSTRAINS -> [[Airport Road (Bellary Road)]]

---

type: Maintenance Event
id: maintenance-desilting-pre-monsoon
title: Pre-monsoon Desilting Drive (Illustrative)
city: Bengaluru
status: illustrative
tags: [class/maintenance_event, maintenance/desilting, region/south]
source_confidence: low
created: 2026-05-18
---
Summary: Illustrative desilting operations to reduce flooding risk.
Relations:
- DEPENDS_ON -> [[Silk Board Underpass]]
- CONSTRAINS -> [[Outer Ring Road]]
- FUNDED_BY -> [[State Budget Grant]]

---

type: Maintenance Event
id: maintenance-silk-board-signal-retiming
title: Silk Board Signal Retiming (Illustrative)
city: Bengaluru
status: illustrative
tags: [class/maintenance_event, maintenance/signal, region/south]
source_confidence: low
created: 2026-05-18
---
Summary: Illustrative signal timing optimization at Silk Board.
Relations:
- DEPENDS_ON -> [[Silk Board Junction]]
- CONSTRAINS -> [[BMTC 500D ORR]]

---

type: Congestion Zone
id: zone-silk-board-congestion
title: Silk Board Congestion Zone
city: Bengaluru
status: active
tags: [class/zone, zone/congestion, region/south]
source_confidence: medium
created: 2026-05-18
---
Summary: Recurring congestion hotspot around Silk Board junction.
Relations:
- LOCATED_IN -> [[Bengaluru Urban Region]]
- OVERLAPS_WITH -> [[Outer Ring Road]]
- OVERLAPS_WITH -> [[Hosur Road]]
- IMPACTS -> [[IT Corridor Commuters]]

---

type: Congestion Zone
id: zone-hebbal-congestion
title: Hebbal Congestion Zone
city: Bengaluru
status: active
tags: [class/zone, zone/congestion, region/hebbal]
source_confidence: medium
created: 2026-05-18
---
Summary: Congestion hotspot near Hebbal interchange and airport corridor.
Relations:
- LOCATED_IN -> [[Hebbal Region]]
- OVERLAPS_WITH -> [[Airport Road (Bellary Road)]]
- IMPACTS -> [[IT Corridor Commuters]]

---

type: Congestion Zone
id: zone-kr-puram-congestion
title: KR Puram Congestion Zone
city: Bengaluru
status: active
tags: [class/zone, zone/congestion, region/east]
source_confidence: medium
created: 2026-05-18
---
Summary: Congestion hotspot around KR Puram interchange.
Relations:
- LOCATED_IN -> [[Bengaluru Urban Region]]
- OVERLAPS_WITH -> [[Old Madras Road]]
- IMPACTS -> [[IT Corridor Commuters]]

---

type: Congestion Zone
id: zone-marathahalli-congestion
title: Marathahalli Congestion Zone
city: Bengaluru
status: active
tags: [class/zone, zone/congestion, region/orr]
source_confidence: medium
created: 2026-05-18
---
Summary: Congestion hotspot on ORR corridor near Marathahalli.
Relations:
- LOCATED_IN -> [[ORR IT Corridor Region]]
- OVERLAPS_WITH -> [[Outer Ring Road]]
- IMPACTS -> [[IT Corridor Commuters]]

---

type: Flooding Zone
id: zone-silk-board-underpass-flooding
title: Silk Board Underpass Flooding Zone
city: Bengaluru
status: active
tags: [class/zone, zone/flooding, region/south]
source_confidence: medium
created: 2026-05-18
---
Summary: Recurrent waterlogging at Silk Board underpass during heavy rains.
Relations:
- LOCATED_IN -> [[Bengaluru Urban Region]]
- OVERLAPS_WITH -> [[Silk Board Underpass]]
- CORRELATES_WITH -> [[Koramangala Valley Drainage Overload]]

---

type: Flooding Zone
id: zone-orr-bellandur-flooding
title: ORR-Bellandur Flooding Zone
city: Bengaluru
status: active
tags: [class/zone, zone/flooding, region/orr]
source_confidence: medium
created: 2026-05-18
---
Summary: Flood-prone stretch near Bellandur on ORR corridor.
Relations:
- LOCATED_IN -> [[ORR IT Corridor Region]]
- OVERLAPS_WITH -> [[Outer Ring Road]]
- CORRELATES_WITH -> [[Koramangala Valley Drainage Overload]]

---

type: Flooding Zone
id: zone-whitefield-underpass-flooding
title: Whitefield Underpass Flooding Zone
city: Bengaluru
status: active
tags: [class/zone, zone/flooding, region/whitefield]
source_confidence: medium
created: 2026-05-18
---
Summary: Waterlogging hotspot near Whitefield underpasses.
Relations:
- LOCATED_IN -> [[Whitefield Region]]
- OVERLAPS_WITH -> [[Whitefield Main Road]]

---

type: Stakeholder
id: stakeholder-it-corridor-commuters
title: IT Corridor Commuters
city: Bengaluru
status: active
tags: [class/stakeholder, stakeholder/commuters, region/orr]
source_confidence: medium
created: 2026-05-18
---
Summary: Daily commuters to IT corridors, especially ORR and Whitefield.
Notes: Inbound relations from congestion zones and failures via IMPACTS.

---

type: Stakeholder
id: stakeholder-informal-auto-drivers
title: Informal Auto Drivers
city: Bengaluru
status: active
tags: [class/stakeholder, stakeholder/auto, city/bengaluru]
source_confidence: medium
created: 2026-05-18
---
Summary: Auto drivers providing last-mile services across city.
Notes: Inbound relations from patterns and policies via IMPACTS.

---

type: Stakeholder
id: stakeholder-freight-operators
title: Freight Operators - Bengaluru
city: Bengaluru
status: active
tags: [class/stakeholder, stakeholder/freight, city/bengaluru]
source_confidence: medium
created: 2026-05-18
---
Summary: Freight carriers and logistics fleets operating in urban corridors.
Notes: Inbound relations from congestion zones via IMPACTS.

---

type: Stakeholder
id: stakeholder-east-residents
title: East Bengaluru Residents Associations
city: Bengaluru
status: active
tags: [class/stakeholder, stakeholder/residents, region/whitefield]
source_confidence: medium
created: 2026-05-18
---
Summary: Resident groups advocating for local mobility improvements.
Notes: Inbound relations from flooding and congestion zones via IMPACTS.

---

type: Funding Mechanism
id: funding-farebox
title: Farebox Revenue
city: Bengaluru
status: active
tags: [class/funding, funding/farebox]
source_confidence: medium
created: 2026-05-18
---
Summary: Operating revenue from fares and tickets.
Notes: Inbound relations from transit services via FUNDED_BY.

---

type: Funding Mechanism
id: funding-state-budget
title: State Budget Grant
city: Bengaluru
status: active
tags: [class/funding, funding/budget]
source_confidence: medium
created: 2026-05-18
---
Summary: State-level funding allocations for transport projects.
Notes: Inbound relations from maintenance events via FUNDED_BY.

---

type: Funding Mechanism
id: funding-multilateral-metro
title: Multilateral Loan - Metro
city: Bengaluru
status: active
tags: [class/funding, funding/loan]
source_confidence: medium
created: 2026-05-18
---
Summary: Multilateral loan funding for metro expansion and operations.
Notes: Inbound relations from metro services via FUNDED_BY.

---

type: Urban Region
id: region-bengaluru-urban
title: Bengaluru Urban Region
city: Bengaluru
status: active
tags: [class/region, region/city]
source_confidence: high
created: 2026-05-18
---
Summary: City-wide urban region representing the metropolitan area.
Relations:
- CONNECTS_TO -> [[ORR IT Corridor Region]]
- CONNECTS_TO -> [[Whitefield Region]]
- CONNECTS_TO -> [[Hebbal Region]]

---

type: Urban Region
id: region-orr-it-corridor
title: ORR IT Corridor Region
city: Bengaluru
status: active
tags: [class/region, region/orr]
source_confidence: medium
created: 2026-05-18
---
Summary: Functional region around ORR employment clusters.
Relations:
- CONNECTS_TO -> [[Whitefield Region]]
- CONNECTS_TO -> [[Bengaluru Urban Region]]

---

type: Urban Region
id: region-whitefield
title: Whitefield Region
city: Bengaluru
status: active
tags: [class/region, region/whitefield]
source_confidence: medium
created: 2026-05-18
---
Summary: Eastern region with tech parks and residential growth.
Relations:
- CONNECTS_TO -> [[ORR IT Corridor Region]]
- CONNECTS_TO -> [[Bengaluru Urban Region]]

---

type: Urban Region
id: region-hebbal
title: Hebbal Region
city: Bengaluru
status: active
tags: [class/region, region/hebbal]
source_confidence: medium
created: 2026-05-18
---
Summary: Northern region centered around Hebbal interchange.
Relations:
- CONNECTS_TO -> [[Bengaluru Urban Region]]

---

Notes
- This seed graph is intended for ontology validation only.
- Replace illustrative nodes with verified data as soon as sources are curated.
