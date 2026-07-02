"""Tests for the scaffold module."""
from threatmodel.model import ComponentType, Stride, ThreatStatus
from threatmodel.scaffold import build_scaffold, _STRIDE_EXAMPLES


def test_default_scaffold_produces_six_threats() -> None:
    m = build_scaffold("My App")
    assert len(m.threats) == 6


def test_default_scaffold_covers_all_stride() -> None:
    m = build_scaffold("My App")
    strides = {t.stride for t in m.threats}
    assert strides == set(Stride)


def test_default_scaffold_single_default_component() -> None:
    m = build_scaffold("My App")
    assert len(m.components) == 1
    assert m.components[0].id == "app"
    assert m.components[0].type == ComponentType.api


def test_threats_reference_default_component() -> None:
    m = build_scaffold("My App")
    for t in m.threats:
        assert "app" in t.components


def test_threat_ids_sequential() -> None:
    m = build_scaffold("My App")
    for i, t in enumerate(m.threats, start=1):
        assert t.id == f"T-{i:03d}"


def test_custom_components_parsed() -> None:
    m = build_scaffold("App", component_specs=["api:backend:Backend", "database:db:Primary DB"])
    assert len(m.components) == 2
    assert m.components[0].id == "backend"
    assert m.components[0].type == ComponentType.api
    assert m.components[1].id == "db"
    assert m.components[1].type == ComponentType.database


def test_custom_components_threats_reference_first() -> None:
    m = build_scaffold("App", component_specs=["web_app:frontend", "database:db"])
    for t in m.threats:
        assert "frontend" in t.components


def test_app_metadata_propagated() -> None:
    m = build_scaffold("TestApp", description="desc", repo="https://github.com/x/y", owner="security-team")
    assert m.app.name == "TestApp"
    assert m.app.description == "desc"
    assert m.app.repo == "https://github.com/x/y"
    assert m.app.owner == "security-team"


def test_threats_default_status_open() -> None:
    m = build_scaffold("App")
    for t in m.threats:
        assert t.status == ThreatStatus.open


def test_threats_have_test_cases() -> None:
    m = build_scaffold("App")
    for t in m.threats:
        assert len(t.test_cases) > 0, f"Threat {t.id} has no test cases"


def test_component_spec_two_part() -> None:
    """TYPE:ID without a name defaults name to the ID."""
    m = build_scaffold("App", component_specs=["api:backend"])
    assert m.components[0].name == "backend"
