from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from truststack_grc.config import get_settings
from truststack_grc.core.mapping.engine import generate_checklist
from truststack_grc.core.packs.loader import PackRegistry
from truststack_grc.core.storage.filesystem import FileSystemStorage
from truststack_grc.core.storage.hashing import sha256_text
from truststack_grc.core.taxonomy.loader import TaxonomyLoader
from truststack_grc.core.projects.context import build_context

def _slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "project"

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

class ProjectService:
    def __init__(self, storage: FileSystemStorage):
        self.storage = storage
        self.settings = get_settings()

    def create_project(self, req: dict[str, Any], actor: str) -> dict[str, Any]:
        taxonomy = TaxonomyLoader.from_env()
        uc = taxonomy.get_use_case(req["use_case_id"])
        if not uc:
            raise ValueError("Unknown use case")

        # Trust but verify: ensure selected industry/segment match the use-case definition
        if uc.get("industry", {}).get("id") != req["industry_id"] or uc.get("segment", {}).get("id") != req["segment_id"]:
            raise ValueError("industry_id/segment_id do not match the selected use_case_id")

        context = build_context(
            project_name=req["name"],
            industry_id=req["industry_id"],
            segment_id=req["segment_id"],
            use_case=uc,
            scope_answers=req.get("scope_answers") or {},
        )

        # Load packs
        reg = PackRegistry.from_env()
        packs = []
        for p in req.get("selected_packs", []):
            pack = reg.load_pack(domain=p["domain"], pack_id=p["pack_id"], version=p["version"])
            if not pack:
                raise ValueError(f"Unknown pack: {p}")
            packs.append(pack)

        checklist = generate_checklist(context=context, packs=packs)

        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        project_id = f"{_slug(req['name'])}-{ts}"

        taxonomy_hash = sha256_text(str(taxonomy.list_industries()))
        packs_hash = sha256_text("|".join([f"{p.pack.domain}:{p.pack.id}:{p.pack.version}:{p.hash}" for p in packs]))
        checklist_hash = sha256_text(str([(i["merge_key"], i["severity"], i["title"]) for i in checklist["items"]]))

        project_doc = {
            "project": {
                "id": project_id,
                "name": req["name"],
                "description": req.get("description"),
                "created_at": utc_now(),
                "updated_at": utc_now(),
            },
            "inputs": {
                "industry_id": req["industry_id"],
                "segment_id": req["segment_id"],
                "use_case_id": req["use_case_id"],
                "selected_packs": req.get("selected_packs", []),
                "scope_answers": req.get("scope_answers", {}),
            },
            "context": context,
            "generated": {
                "generator_version": self.settings.generator_version,
                "taxonomy_hash": taxonomy_hash,
                "packs_hash": packs_hash,
                "checklist_hash": checklist_hash,
            },
        }

        checklist_doc = {
            "project_id": project_id,
            "generated_at": utc_now(),
            "items": checklist["items"],
            "counts": checklist["counts"],
        }

        self.storage.write_project(project_id, project_doc)
        self.storage.write_checklist(project_id, checklist_doc)
        self.storage.append_audit(project_id, "project.created", actor, {"project": {"id": project_id, "name": req["name"]}})

        return {"project": project_doc["project"], "project_id": project_id}

    def update_checklist_item(self, project_id: str, item_id: str, patch: dict[str, Any], actor: str) -> dict[str, Any] | None:
        proj = self.storage.read_project(project_id)
        checklist = self.storage.read_checklist(project_id)
        if not proj or not checklist:
            return None

        items = checklist.get("items", [])
        found = None
        for it in items:
            if it.get("item_id") == item_id:
                found = it
                break
        if not found:
            return None

        before = {k: found.get(k) for k in ["status", "owner", "notes"]}
        for k in ["status", "owner", "notes"]:
            if k in patch:
                found[k] = patch[k]
        after = {k: found.get(k) for k in ["status", "owner", "notes"]}

        proj["project"]["updated_at"] = utc_now()
        self.storage.write_project(project_id, proj)
        self.storage.write_checklist(project_id, checklist)
        self.storage.append_audit(project_id, "checklist.item.updated", actor, {"item_id": item_id, "before": before, "after": after})
        return found

    async def add_evidence(self, project_id: str, item_id: str, upload_file, actor: str) -> dict[str, Any] | None:
        proj = self.storage.read_project(project_id)
        checklist = self.storage.read_checklist(project_id)
        if not proj or not checklist:
            return None
        items = checklist.get("items", [])
        found = None
        for it in items:
            if it.get("item_id") == item_id:
                found = it
                break
        if not found:
            return None

        content = await upload_file.read()
        meta = self.storage.save_evidence_file(project_id, item_id, upload_file.filename or "upload.bin", content)
        meta.update({
            "content_type": upload_file.content_type,
            "uploaded_at": utc_now(),
        })
        found.setdefault("evidence", []).append(meta)

        proj["project"]["updated_at"] = utc_now()
        self.storage.write_project(project_id, proj)
        self.storage.write_checklist(project_id, checklist)
        self.storage.append_audit(project_id, "evidence.uploaded", actor, {"item_id": item_id, "file": meta})
        return meta
