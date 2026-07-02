"""Integration tests for the tm CLI via Click's test runner."""
import yaml
from click.testing import CliRunner

from threatmodel.cli import cli


def test_init_creates_file(tmp_path) -> None:
    runner = CliRunner()
    out = tmp_path / "tm.yaml"
    result = runner.invoke(cli, ["init", "My App", "-f", str(out)])
    assert result.exit_code == 0, result.output
    assert out.exists()
    data = yaml.safe_load(out.read_text())
    assert data["app"]["name"] == "My App"
    assert data["version"] == "1"
    assert len(data["threats"]) == 6


def test_init_with_components(tmp_path) -> None:
    runner = CliRunner()
    out = tmp_path / "tm.yaml"
    result = runner.invoke(
        cli,
        ["init", "App", "-c", "api:backend:Backend", "-c", "database:db:DB", "-f", str(out)],
    )
    assert result.exit_code == 0, result.output
    data = yaml.safe_load(out.read_text())
    ids = [c["id"] for c in data["components"]]
    assert "backend" in ids
    assert "db" in ids


def test_init_refuses_overwrite_without_force(tmp_path) -> None:
    runner = CliRunner()
    out = tmp_path / "tm.yaml"
    out.write_text("existing")
    result = runner.invoke(cli, ["init", "App", "-f", str(out)])
    assert result.exit_code != 0
    assert out.read_text() == "existing"


def test_init_force_overwrites(tmp_path) -> None:
    runner = CliRunner()
    out = tmp_path / "tm.yaml"
    out.write_text("old content")
    result = runner.invoke(cli, ["init", "New App", "--force", "-f", str(out)])
    assert result.exit_code == 0, result.output
    data = yaml.safe_load(out.read_text())
    assert data["app"]["name"] == "New App"


def test_list_shows_table(tmp_path) -> None:
    runner = CliRunner()
    out = tmp_path / "tm.yaml"
    runner.invoke(cli, ["init", "My App", "-f", str(out)])
    result = runner.invoke(cli, ["list", str(out)])
    assert result.exit_code == 0, result.output
    assert "T-001" in result.output
    assert "My App" in result.output


def test_list_filter_status(tmp_path) -> None:
    runner = CliRunner()
    out = tmp_path / "tm.yaml"
    runner.invoke(cli, ["init", "App", "-f", str(out)])
    # All threats start as 'open', so filtering on 'mitigated' should show 0.
    result = runner.invoke(cli, ["list", str(out), "--status", "mitigated"])
    assert result.exit_code == 0, result.output
    assert "0 threat(s)" in result.output


def test_list_filter_severity(tmp_path) -> None:
    runner = CliRunner()
    out = tmp_path / "tm.yaml"
    runner.invoke(cli, ["init", "App", "-f", str(out)])
    result = runner.invoke(cli, ["list", str(out), "--severity", "High"])
    assert result.exit_code == 0, result.output
    # High-severity threats include Spoofing, Tampering, EoP — expect >= 1.
    assert "T-" in result.output


def test_list_missing_file(tmp_path) -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["list", str(tmp_path / "missing.yaml")])
    assert result.exit_code != 0


def test_list_invalid_yaml(tmp_path) -> None:
    runner = CliRunner()
    bad = tmp_path / "bad.yaml"
    bad.write_text(": invalid: yaml: [")
    result = runner.invoke(cli, ["list", str(bad)])
    assert result.exit_code != 0


def test_list_invalid_schema(tmp_path) -> None:
    runner = CliRunner()
    bad = tmp_path / "bad.yaml"
    bad.write_text("version: '1'\napp:\n  name: App\ncomponents: []\nthreats: bad\n")
    result = runner.invoke(cli, ["list", str(bad)])
    assert result.exit_code != 0
