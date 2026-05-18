Asset — Node Template

type: Asset
id: asset-{unique_id}

title:
category: (bridge|road_segment|tunnel|station|signal)

properties:
- geo_id:
- location: (lat, lon)
- owner_agency:
- installation_date:
- condition_index: (0-100)
- last_maintenance_date:
- expected_life_years:
- SHM_sensors: []
- inspection_records: []
- replacement_cost_estimate:

relations:
- part_of: [Corridor, Network]
- maintained_by: [MaintenanceContract]
- funded_by: [BudgetLine]

evidence:
- inspection_reports: []
- imagery_links: []

notes:
- Store time-series condition updates in `inspection_records` with timestamps.