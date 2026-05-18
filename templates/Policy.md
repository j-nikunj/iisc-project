Policy — Node Template

type: Policy
id: policy-{unique_id}

title:
scope: (national|state|city)

properties:
- effective_date:
- issuing_agency:
- summary:
- full_text_link:
- affected_entities: []
- budget_implications:
- sunset_clause:
- enforcement_mechanisms:

relations:
- influences: [Corridor, Operator, Asset]
- funded_by: [BudgetLine]
- supersedes: [Policy]

evidence:
- gazette_links: []
- policy_analysis: []

notes:
- Tag with policy domains (landuse, safety, finance, procurement).