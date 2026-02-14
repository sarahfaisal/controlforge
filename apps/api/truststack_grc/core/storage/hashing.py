from __future__ import annotations

import hashlib
from pathlib import Path

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def sha256_dir(path: Path) -> str:
    h = hashlib.sha256()
    files = [p for p in path.rglob("*") if p.is_file()]
    for f in sorted(files, key=lambda p: str(p)):
        h.update(str(f.relative_to(path)).encode("utf-8"))
        h.update(b"\x00")
        h.update(f.read_bytes())
        h.update(b"\x00")
    return h.hexdigest()
