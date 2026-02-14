from __future__ import annotations

from typing import Any

def build_context(*, project_name: str, industry_id: str, segment_id: str, use_case: dict[str, Any], scope_answers: dict[str, Any]) -> dict[str, Any]:
    tags = list(dict.fromkeys(use_case.get("tags", [])))

    jurisdictions = scope_answers.get("jurisdictions") or []
    if isinstance(jurisdictions, str):
        jurisdictions = [jurisdictions]

    processes_phi = bool(scope_answers.get("processes_phi")) or ("phi" in tags)
    processes_pii = ("pii" in tags)
    processes_pci = bool(scope_answers.get("processes_pci")) or ("pci" in tags)

    uses_tools = bool(scope_answers.get("uses_tools"))
    internet_exposed = bool(scope_answers.get("internet_exposed"))
    customer_facing = bool(scope_answers.get("customer_facing"))

    model_sourcing = scope_answers.get("model_sourcing") or "unknown"

    pattern = {
        "rag": ("rag" in tags),
        "agentic": uses_tools,
        "chatbot": ("chatbot" in tags),
        "classifier": ("classifier" in tags),
        "decision_support": ("decision_support" in tags),
    }

    context = {
        "system": {
            "name": project_name,
        },
        "industry": {"id": industry_id},
        "segment": {"id": segment_id},
        "use_case": {"id": use_case.get("id")},
        "tags": tags,
        "pattern": pattern,
        "data": {"phi": processes_phi, "pii": processes_pii, "pci": processes_pci},
        "deployment": {"internet_exposed": internet_exposed, "customer_facing": customer_facing},
        "jurisdiction": {
            "list": jurisdictions,
            "eu": "EU" in jurisdictions,
            "us": "US" in jurisdictions,
            "uk": "UK" in jurisdictions,
        },
        "model": {
            "sourcing": model_sourcing,
            "fine_tuned": model_sourcing == "fine_tuned",
        },
        "scope": scope_answers,
    }
    return context
