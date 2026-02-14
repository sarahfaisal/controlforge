from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

@dataclass
class AuditEvent:
    event_type: str
    actor: str
    details: dict[str, Any]

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def append_event(path: Path, event: AuditEvent) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": utc_now_iso(),
        "event_type": event.event_type,
        "actor": event.actor,
        "details": event.details,
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
