from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from truststack_grc.config import get_settings
from truststack_grc.core.util.yamlio import read_yaml, write_yaml
from truststack_grc.core.storage.auditlog import append_event, AuditEvent
from truststack_grc.core.storage.hashing import sha256_file

def safe_filename(name: str) -> str:
    name = name.strip().replace("\\", "_").replace("/", "_")
    name = "".join(ch for ch in name if ch.isalnum() or ch in {"-", "_", ".", " "}).strip()
    return name[:120] or "upload.bin"

@dataclass(frozen=True)
class StoragePaths:
    workspace_root: Path

class FileSystemStorage:
    def __init__(self, paths: StoragePaths):
        self.paths = paths
        self.paths.workspace_root.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_env(cls) -> "FileSystemStorage":
        settings = get_settings()
        return cls(paths=StoragePaths(workspace_root=settings.workspace_root))

    def project_dir(self, project_id: str) -> Path:
        return self.paths.workspace_root / project_id

    def list_projects(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for d in sorted([p for p in self.paths.workspace_root.iterdir() if p.is_dir() and not p.name.startswith(".")], key=lambda p: p.name):
            proj_path = d / "project.yaml"
            if proj_path.exists():
                try:
                    data = read_yaml(proj_path)
                    out.append(data.get("project", {"id": d.name}))
                except Exception:
                    out.append({"id": d.name, "name": d.name})
        return out

    def read_project(self, project_id: str) -> dict[str, Any] | None:
        path = self.project_dir(project_id) / "project.yaml"
        if not path.exists():
            return None
        return read_yaml(path)

    def write_project(self, project_id: str, data: dict[str, Any]) -> None:
        write_yaml(self.project_dir(project_id) / "project.yaml", data)

    def read_checklist(self, project_id: str) -> dict[str, Any] | None:
        path = self.project_dir(project_id) / "checklist.yaml"
        if not path.exists():
            return None
        return read_yaml(path)

    def write_checklist(self, project_id: str, data: dict[str, Any]) -> None:
        write_yaml(self.project_dir(project_id) / "checklist.yaml", data)

    def audit_path(self, project_id: str) -> Path:
        return self.project_dir(project_id) / "auditlog.ndjson"

    def append_audit(self, project_id: str, event_type: str, actor: str, details: dict[str, Any]) -> None:
        append_event(self.audit_path(project_id), AuditEvent(event_type=event_type, actor=actor, details=details))

    def save_evidence_file(self, project_id: str, item_id: str, filename: str, content: bytes) -> dict[str, Any]:
        proj_dir = self.project_dir(project_id)
        evidence_dir = proj_dir / "evidence" / item_id
        evidence_dir.mkdir(parents=True, exist_ok=True)
        safe = safe_filename(filename)
        target = evidence_dir / safe
        # Avoid overwriting: add suffix
        if target.exists():
            stem, dot, ext = safe.partition(".")
            i = 2
            while True:
                candidate = evidence_dir / f"{stem}_{i}{dot}{ext}" if dot else evidence_dir / f"{stem}_{i}"
                if not candidate.exists():
                    target = candidate
                    break
                i += 1
        target.write_bytes(content)
        return {
            "file_name": target.name,
            "relative_path": str(target.relative_to(proj_dir)),
            "sha256": sha256_file(target),
            "bytes": len(content),
        }
