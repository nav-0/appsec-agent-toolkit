"""Pydantic models for threat_model_v1 schema."""
from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ComponentType(str, Enum):
    process = "process"
    data_store = "data_store"
    external_entity = "external_entity"
    other = "other"


class Stride(str, Enum):
    spoofing = "Spoofing"
    tampering = "Tampering"
    repudiation = "Repudiation"
    information_disclosure = "Information Disclosure"
    denial_of_service = "Denial of Service"
    elevation_of_privilege = "Elevation of Privilege"


class Severity(str, Enum):
    critical = "Critical"
    high = "High"
    medium = "Medium"
    low = "Low"
    info = "Info"


class ThreatStatus(str, Enum):
    open = "open"
    mitigated = "mitigated"
    accepted = "accepted"
    transferred = "transferred"
    wont_fix = "wont_fix"


class EvidenceResult(str, Enum):
    pass_ = "pass"
    fail = "fail"
    inconclusive = "inconclusive"


class App(BaseModel):
    name: str
    description: Optional[str] = None
    repo: Optional[str] = None
    owner: Optional[str] = None


class Component(BaseModel):
    id: str
    name: str
    type: ComponentType
    trust_boundary: Optional[str] = None
    description: Optional[str] = None


class TrustBoundary(BaseModel):
    id: str
    name: str
    description: Optional[str] = None


class Evidence(BaseModel):
    path: str
    note: Optional[str] = None
    timestamp: Optional[str] = None
    result: Optional[EvidenceResult] = None


class Threat(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    stride: Stride
    components: List[str] = Field(min_length=1)
    severity: Severity
    mitigations: List[str] = Field(default_factory=list)
    test_cases: List[str] = Field(default_factory=list)
    status: ThreatStatus = ThreatStatus.open
    evidence: List[Evidence] = Field(default_factory=list)


class ThreatModel(BaseModel):
    version: str = "1"
    app: App
    components: List[Component] = Field(default_factory=list)
    trust_boundaries: List[TrustBoundary] = Field(default_factory=list)
    threats: List[Threat] = Field(default_factory=list)

    def component_by_id(self, cid: str) -> Optional[Component]:
        return next((c for c in self.components if c.id == cid), None)
