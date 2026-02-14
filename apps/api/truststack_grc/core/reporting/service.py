from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from truststack_grc.core.storage.filesystem import FileSystemStorage

class ReportingService:
    def __init__(self, storage: FileSystemStorage):
        self.storage = storage
        tmpl_dir = Path(__file__).parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(tmpl_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def _load(self, project_id: str) -> tuple[dict[str, Any], dict[str, Any]] | None:
        project = self.storage.read_project(project_id)
        checklist = self.storage.read_checklist(project_id)
        if not project or not checklist:
            return None
        return project, checklist

    def render_html(self, project_id: str) -> str | None:
        loaded = self._load(project_id)
        if not loaded:
            return None
        project, checklist = loaded
        tmpl = self.env.get_template("report.html.j2")
        return tmpl.render(project=project, checklist=checklist)

    def export_json(self, project_id: str) -> dict[str, Any] | None:
        loaded = self._load(project_id)
        if not loaded:
            return None
        project, checklist = loaded
        return {"project": project, "checklist": checklist}

    def export_csv(self, project_id: str) -> str | None:
        loaded = self._load(project_id)
        if not loaded:
            return None
        project, checklist = loaded
        exports = self.storage.project_dir(project_id) / "exports"
        exports.mkdir(parents=True, exist_ok=True)
        path = exports / f"{project_id}.csv"

        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["item_id","domain","severity","status","title","objective","owner","evidence_count","pack_refs"])
            for item in checklist.get("items", []):
                refs = ";".join([f'{r["pack_id"]}@{r["version"]}:{r["control_id"]}' for r in item.get("pack_refs", [])])
                w.writerow([
                    item.get("item_id"),
                    item.get("domain"),
                    item.get("severity"),
                    item.get("status"),
                    item.get("title"),
                    item.get("objective"),
                    item.get("owner") or "",
                    len(item.get("evidence") or []),
                    refs,
                ])
        return str(path)

    def export_pdf(self, project_id: str) -> str | None:
        # Minimal scaffold PDF export. Replace with your enterprise template.
        loaded = self._load(project_id)
        if not loaded:
            return None
        project, checklist = loaded
        exports = self.storage.project_dir(project_id) / "exports"
        exports.mkdir(parents=True, exist_ok=True)
        path = exports / f"{project_id}.pdf"

        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        c = canvas.Canvas(str(path), pagesize=letter)
        width, height = letter
        y = height - 48

        c.setFont("Helvetica-Bold", 16)
        c.drawString(48, y, "TrustStack AI GRC — Audit Report")
        y -= 22

        c.setFont("Helvetica", 11)
        c.drawString(48, y, f"Project: {project['project']['name']} ({project['project']['id']})")
        y -= 16
        c.drawString(48, y, f"Generated: {checklist.get('generated_at')}")
        y -= 24

        c.setFont("Helvetica-Bold", 12)
        c.drawString(48, y, "Checklist (top items)")
        y -= 18

        c.setFont("Helvetica", 10)
        items = checklist.get("items", [])[:20]
        for item in items:
            line = f"[{item.get('domain')}] {item.get('severity')} — {item.get('status')} — {item.get('title')}"
            if y < 72:
                c.showPage()
                y = height - 48
                c.setFont("Helvetica", 10)
            c.drawString(48, y, line[:110])
            y -= 14

        c.save()
        return str(path)
