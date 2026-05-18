Operator — Node Template

type: Operator
id: operator-{unique_id}

title:
operator_type: (public_transit|private_bus|ride_hailing|freight_carrier|paratransit)

properties:
- registration_id:
- operating_region:
- fleet_size:
- vehicle_types:
- fare_structure:
- revenue_sources:
- contract_terms: (if any)
- performance_metrics: {on_time, availability, load_factor}
- compliance_issues: []

relations:
- operates_on: [Corridor, Route]
- regulated_by: [Agency]
- receives_funding_from: [BudgetLine, PPPContract]

evidence:
- contracts: []
- operator_reports: []

notes:
- Include links to GTFS or schedule data when available.