# Taxonomy authoring guide (Industry → Segment → Use case)

Taxonomy is discovered by traversing folders.

## Folder convention
```
registry/taxonomy/industries/<industry_id>/industry.yaml
registry/taxonomy/industries/<industry_id>/segments/<segment_id>/segment.yaml
registry/taxonomy/industries/<industry_id>/segments/<segment_id>/use-cases/<use_case_id>/use_case.yaml
```

## Use case config
A use case carries:
- tags (used for applicability and reporting)
- scoping questions (rendered in the UI and normalized into context)

Example:
```yaml
id: claims-approval-assistant
name: Claims Approval & Denial Assistant
tags: [llm, rag, decision_support, phi, pii]
scope_questions:
  - id: processes_phi
    prompt: "Does the system process PHI?"
    type: boolean
    default: true
  - id: jurisdictions
    prompt: "Which jurisdictions apply?"
    type: multiselect
    options: [US, EU, UK]
    default: [US]
```
