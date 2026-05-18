Corridor — Node Template

type: Corridor
id: corridor-{unique_id}

title: 
aliases:

properties:
- geo_id: 
- name:
- city:
- length_m:
- lanes:
- functional_class: (arterial/collector/local)
- typical_speed_kmph:
- peak_hour_volume_pcuh:
- modal_share: {car: %, bus: two_wheeler: %, walking: %}
- owner_agency:
- maintenance_schedule:
- sensors: (list of sensor IDs)
- last_inspection_date:

relations:
- connects_to: [Corridor]
- serves: [Station, Depot, BusStop]
- policy_influence: [Policy]
- demand_flow_from: [CommuterSegment]

evidence:
- source_documents: []
- data_links: []

notes:
- Use `corridor-{city}-{shortname}` as id convention.