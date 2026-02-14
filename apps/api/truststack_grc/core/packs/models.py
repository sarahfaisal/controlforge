from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field

Domain = Literal["security", "safety", "governance"]
PackType = Literal["control_catalog", "threat_catalog", "suggestion_catalog"]

class PackSource(BaseModel):
    name: str
    reference: str
    url: str | None = None

class PackInfo(BaseModel):
    id: str
    name: str
    version: str
    domain: Domain
    type: PackType
    description: str | None = None
    license_hint: str | None = None
    source: PackSource
    extra: dict[str, Any] = Field(default_factory=dict)

class EvidenceSpec(BaseModel):
    type: str
    name: str
    optional: bool = False
    extra: dict[str, Any] = Field(default_factory=dict)

class ControlRef(BaseModel):
    name: str
    ref: str
    url: str | None = None

class ControlSuggestion(BaseModel):
    type: str
    id: str | None = None
    name: str | None = None
    url: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)

class ControlDefinition(BaseModel):
    id: str
    canonical_id: str | None = None
    title: str
    objective: str
    severity: Literal["low", "medium", "high", "critical"]
    category: str | None = None
    applicability: dict[str, Any] = Field(default_factory=dict)
    why: str | None = None
    evidence_required: list[dict[str, Any]] = Field(default_factory=list)
    test_procedures: list[str] = Field(default_factory=list)
    references: list[dict[str, Any]] = Field(default_factory=list)
    suggestions: list[dict[str, Any]] = Field(default_factory=list)
    extra: dict[str, Any] = Field(default_factory=dict)

class Pack(BaseModel):
    pack: PackInfo
    controls: list[ControlDefinition]
    path: str
    hash: str
