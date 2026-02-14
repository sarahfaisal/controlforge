from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import json

from truststack_grc.config import get_settings
from truststack_grc.core.util.yamlio import read_yaml

ROOT_KEYS = {"industry", "segment", "use_case", "tags", "pattern", "data", "deployment", "jurisdiction", "model", "system"}

@dataclass(frozen=True)
class TaxonomyPaths:
    root: Path
    industries_dir: Path

class TaxonomyLoader:
    def __init__(self, paths: TaxonomyPaths, schema_dir: Path):
        self.paths = paths
        self.schema_dir = schema_dir
        self._use_case_validator = Draft202012Validator(json.loads((schema_dir / "use_case.schema.json").read_text(encoding="utf-8")))

    @classmethod
    def from_env(cls) -> "TaxonomyLoader":
        settings = get_settings()
        root = settings.config_root / "taxonomy"
        return cls(
            paths=TaxonomyPaths(root=root, industries_dir=root / "industries"),
            schema_dir=(settings.config_root.parent / "schemas"),
        )

    def _industry_paths(self) -> list[Path]:
        if not self.paths.industries_dir.exists():
            return []
        return [p for p in self.paths.industries_dir.iterdir() if p.is_dir()]

    def list_industries(self) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for ind_dir in self._industry_paths():
            ind_file = ind_dir / "industry.yaml"
            if not ind_file.exists():
                continue
            industry = read_yaml(ind_file)
            industry.setdefault("segments", [])
            # add segments
            seg_root = ind_dir / "segments"
            segments = []
            if seg_root.exists():
                for seg_dir in sorted([d for d in seg_root.iterdir() if d.is_dir()], key=lambda p: p.name):
                    seg_file = seg_dir / "segment.yaml"
                    if not seg_file.exists():
                        continue
                    seg = read_yaml(seg_file)
                    seg["use_cases"] = self._list_use_cases_in_segment(seg_dir)
                    segments.append(seg)
            industry["segments"] = segments
            items.append(industry)
        return sorted(items, key=lambda x: x.get("name", x.get("id", "")))

    def _list_use_cases_in_segment(self, seg_dir: Path) -> list[dict[str, Any]]:
        uc_root = seg_dir / "use-cases"
        out: list[dict[str, Any]] = []
        if not uc_root.exists():
            return out
        for uc_dir in sorted([d for d in uc_root.iterdir() if d.is_dir()], key=lambda p: p.name):
            uc_file = uc_dir / "use_case.yaml"
            if not uc_file.exists():
                continue
            uc = read_yaml(uc_file)
            # validate; raise is ok for dev; in prod we'd log and skip
            self._use_case_validator.validate(uc)
            out.append(uc)
        return out

    def get_industry(self, industry_id: str) -> dict[str, Any] | None:
        for industry in self.list_industries():
            if industry.get("id") == industry_id:
                return industry
        return None

    def get_use_case(self, use_case_id: str) -> dict[str, Any] | None:
        for industry in self.list_industries():
            for segment in industry.get("segments", []):
                for uc in segment.get("use_cases", []):
                    if uc.get("id") == use_case_id:
                        # include pointers
                        return {
                            "industry": {"id": industry.get("id"), "name": industry.get("name")},
                            "segment": {"id": segment.get("id"), "name": segment.get("name")},
                            **uc,
                        }
        return None
