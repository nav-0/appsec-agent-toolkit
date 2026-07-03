"""Tests for the Pydantic threat model."""
import pytest
from pydantic import ValidationError

from threatmodel.model import (
    App, Component, ComponentType, Evidence, EvidenceResult,
    Severity, Stride, Threat, ThreatModel, ThreatStatus,
)


def _minimal_model() -> ThreatModel:
    return ThreatModel(
        version="1",
        app=App(name="Test App"),
        components=[Component(id="api", name="API", type=ComponentType.process)],
        threats=[
            Threat(
                id="T-001",
                title="Example spoofing threat",
                stride=Stride.spoofing,
                components=["api"],
                severity=Severity.high,
            )
        ],
    )


def test_minimal_model_valid() -> None:
    m = _minimal_model()
    assert m.app.name == "Test App"
    assert len(m.threats) == 1
    assert m.threats[0].status == ThreatStatus.open


def test_threat_defaults() -> None:
    m = _minimal_model()
    t = m.threats[0]
    assert t.mitigations == []
    assert t.test_cases == []
    assert t.evidence == []
    assert t.status == ThreatStatus.open


def test_component_by_id_found() -> None:
    m = _minimal_model()
    c = m.component_by_id("api")
    assert c is not None
    assert c.name == "API"


def test_component_by_id_missing() -> None:
    m = _minimal_model()
    assert m.component_by_id("nonexistent") is None


def test_threat_requires_at_least_one_component() -> None:
    with pytest.raises(ValidationError):
        Threat(
            id="T-001",
            title="Bad",
            stride=Stride.tampering,
            components=[],  # violates min_length=1
            severity=Severity.low,
        )


def test_evidence_optional_fields() -> None:
    ev = Evidence(path="evidence/screenshot.png")
    assert ev.note is None
    assert ev.result is None


def test_evidence_result_enum() -> None:
    ev = Evidence(path="f.png", result=EvidenceResult.fail)
    assert ev.result == EvidenceResult.fail


def test_model_roundtrip_json() -> None:
    m = _minimal_model()
    raw = m.model_dump(mode="json", exclude_none=True)
    m2 = ThreatModel.model_validate(raw)
    assert m2.app.name == m.app.name
    assert m2.threats[0].id == m.threats[0].id


def test_all_stride_values() -> None:
    expected = {
        "Spoofing", "Tampering", "Repudiation",
        "Information Disclosure", "Denial of Service", "Elevation of Privilege",
    }
    assert {s.value for s in Stride} == expected


def test_optional_app_fields() -> None:
    app = App(name="Minimal")
    assert app.repo is None
    assert app.owner is None
