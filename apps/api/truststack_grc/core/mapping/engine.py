from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from truststack_grc.core.mapping.rules import eval_rule
from truststack_grc.core.packs.models import Pack, ControlDefinition

def stable_id(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

@dataclass
class PackRef:
    domain: str
    pack_id: str
    version: str
    control_id: str
    title: str | None = None

def _uniq_list(items: list[Any]) -> list[Any]:
    seen = set()
    out = []
    for x in items:
        key = jsonable_key(x)
        if key in seen:
            continue
        seen.add(key)
        out.append(x)
    return out

def jsonable_key(x: Any) -> str:
    if isinstance(x, dict):
        return str(sorted((k, jsonable_key(v)) for k, v in x.items()))
    if isinstance(x, list):
        return str([jsonable_key(i) for i in x])
    return repr(x)

def generate_checklist(context: dict[str, Any], packs: list[Pack]) -> dict[str, Any]:
    merged: dict[str, dict[str, Any]] = {}

    for pack in packs:
        for ctrl in pack.controls:
            ok, trace = eval_rule(ctrl.applicability, context)
            if not ok:
                continue

            merge_key = ctrl.canonical_id or f"{pack.pack.domain}/{pack.pack.id}/{ctrl.id}"
            instance_id = stable_id(merge_key)

            ref = {
                "domain": pack.pack.domain,
                "pack_id": pack.pack.id,
                "version": pack.pack.version,
                "control_id": ctrl.id,
                "source": pack.pack.source.model_dump(),
                "pack_hash": pack.hash,
            }

            why_parts = []
            if ctrl.why:
                why_parts.append(ctrl.why)
            if trace.matched:
                why_parts.append("Triggered by: " + "; ".join(trace.matched))

            if merge_key not in merged:
                merged[merge_key] = {
                    "item_id": instance_id,
                    "merge_key": merge_key,
                    "canonical_id": ctrl.canonical_id,
                    "title": ctrl.title,
                    "objective": ctrl.objective,
                    "severity": ctrl.severity,
                    "category": ctrl.category,
                    "domain": pack.pack.domain,
                    "pack_refs": [ref],
                    "why_applies": "\n".join(why_parts).strip(),
                    "evidence_required": list(ctrl.evidence_required or []),
                    "test_procedures": list(ctrl.test_procedures or []),
                    "status": "not_started",
                    "owner": None,
                    "notes": None,
                    "evidence": [],
                }
            else:
                merged[merge_key]["pack_refs"].append(ref)
                merged[merge_key]["evidence_required"] = _uniq_list(merged[merge_key]["evidence_required"] + list(ctrl.evidence_required or []))
                merged[merge_key]["test_procedures"] = _uniq_list(merged[merge_key]["test_procedures"] + list(ctrl.test_procedures or []))
                # Prefer highest severity when merged
                sev_rank = {"low": 0, "medium": 1, "high": 2, "critical": 3}
                if sev_rank.get(ctrl.severity, 0) > sev_rank.get(merged[merge_key]["severity"], 0):
                    merged[merge_key]["severity"] = ctrl.severity
                # Extend why if useful
                if why_parts:
                    existing = merged[merge_key].get("why_applies") or ""
                    add = "\n".join([p for p in why_parts if p and p not in existing])
                    merged[merge_key]["why_applies"] = (existing + ("\n" if existing and add else "") + add).strip()

    items = list(merged.values())
    # deterministic ordering: domain, severity desc, title
    sev_rank = {"critical": 3, "high": 2, "medium": 1, "low": 0}
    items.sort(key=lambda x: (x["domain"], -sev_rank.get(x["severity"], 0), x["title"]))
    return {"items": items, "counts": summarize(items)}

def summarize(items: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {"total": len(items), "by_domain": {}, "by_status": {}}
    for it in items:
        d = it.get("domain")
        counts["by_domain"][d] = counts["by_domain"].get(d, 0) + 1
        s = it.get("status")
        counts["by_status"][s] = counts["by_status"].get(s, 0) + 1
    return counts
