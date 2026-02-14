from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

def _find_repo_root(start: Path) -> Path:
    # Find a parent directory containing `registry/` (works in both monorepo and packaged layouts).
    for p in [start, *start.parents]:
        if (p / "registry").exists():
            return p
    # Fallback to current working directory
    cwd = Path.cwd()
    if (cwd / "registry").exists():
        return cwd
    return cwd

_REPO_ROOT = _find_repo_root(Path(__file__).resolve())

DEFAULT_CONFIG_ROOT = (_REPO_ROOT / "registry").resolve()
DEFAULT_WORKSPACE_ROOT = (_REPO_ROOT / "workspaces").resolve()

@dataclass(frozen=True)
class Settings:
    # Config-first roots (override with env vars for containerized deployments)
    config_root: Path = Path(os.getenv("TRUSTSTACK_CONFIG_ROOT", str(DEFAULT_CONFIG_ROOT))).resolve()
    workspace_root: Path = Path(os.getenv("TRUSTSTACK_WORKSPACE_ROOT", str(DEFAULT_WORKSPACE_ROOT))).resolve()

    # Stored in project metadata for reproducible checklist generation
    generator_version: str = "0.1.0"

def get_settings() -> Settings:
    return Settings()
