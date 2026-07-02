"""tm — AppSec Toolkit threat-model CLI."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import click
import yaml
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from .model import ThreatModel
from .scaffold import build_scaffold

console = Console()
err_console = Console(stderr=True, style="bold red")


def _load_model(path: Path) -> ThreatModel:
    try:
        data = yaml.safe_load(path.read_text())
    except FileNotFoundError:
        err_console.print(f"File not found: {path}")
        sys.exit(1)
    except yaml.YAMLError as exc:
        err_console.print(f"YAML parse error: {exc}")
        sys.exit(1)

    try:
        return ThreatModel.model_validate(data)
    except ValidationError as exc:
        err_console.print(f"Schema validation failed:\n{exc}")
        sys.exit(1)


def _dump_model(model: ThreatModel, path: Path) -> None:
    # model_dump with mode='json' converts enums to their string values.
    raw = model.model_dump(mode="json", exclude_none=True)
    path.write_text(yaml.dump(raw, sort_keys=False, allow_unicode=True))


@click.group()
def cli() -> None:
    """AppSec Toolkit — threat-model toolchain."""


@cli.command("init")
@click.argument("name")
@click.option("--description", "-d", default="", help="Short description of the application.")
@click.option("--repo", "-r", default="", help="Source repository URL or path.")
@click.option("--owner", "-o", default="", help="Owning team or individual.")
@click.option(
    "--component", "-c", "components",
    multiple=True,
    metavar="TYPE:ID[:NAME]",
    help=(
        "Component to add. Repeatable. Format: TYPE:ID or TYPE:ID:Name. "
        "TYPE must be one of: web_app, api, database, queue, external_service, "
        "client, identity_provider, storage, other."
    ),
)
@click.option(
    "--output", "-f",
    default="threat-model.yaml",
    show_default=True,
    help="Output file path.",
)
@click.option("--force", is_flag=True, help="Overwrite an existing file.")
def init_cmd(
    name: str,
    description: str,
    repo: str,
    owner: str,
    components: tuple[str, ...],
    output: str,
    force: bool,
) -> None:
    """Scaffold a new threat model for APP_NAME.

    Creates a YAML file pre-populated with one illustrative STRIDE threat per
    category. Edit the file to describe your actual threats, then use
    'tm list' to review them.

    \b
    Examples:
      tm init "My API"
      tm init "My API" -c api:backend:Backend -c database:db:Primary\\ DB -f myapp.yaml
    """
    out = Path(output)
    if out.exists() and not force:
        err_console.print(
            f"{out} already exists. Use --force to overwrite."
        )
        sys.exit(1)

    model = build_scaffold(
        name=name,
        description=description,
        repo=repo,
        owner=owner,
        component_specs=list(components) if components else None,
    )
    _dump_model(model, out)
    console.print(f"[green]Created[/green] {out} with {len(model.threats)} example threats.")
    console.print("Edit the file to describe your actual threats, then run [bold]tm list[/bold].")


@cli.command("list")
@click.argument("file", default="threat-model.yaml")
@click.option(
    "--status", "-s",
    default=None,
    help="Filter by status (open, mitigated, accepted, transferred, wont_fix).",
)
@click.option(
    "--severity", "-S",
    default=None,
    help="Filter by severity (Critical, High, Medium, Low, Info).",
)
def list_cmd(file: str, status: Optional[str], severity: Optional[str]) -> None:
    """List threats in FILE (default: threat-model.yaml).

    \b
    Examples:
      tm list
      tm list myapp.yaml --status open
      tm list myapp.yaml --severity High
    """
    path = Path(file)
    model = _load_model(path)

    threats = model.threats
    if status:
        threats = [t for t in threats if t.status.value == status]
    if severity:
        threats = [t for t in threats if t.severity.value == severity]

    table = Table(title=f"Threats — {model.app.name}", show_lines=True)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title")
    table.add_column("STRIDE", style="magenta")
    table.add_column("Severity", style="yellow")
    table.add_column("Status")
    table.add_column("Evidence", justify="right")

    severity_colours = {
        "Critical": "bold red",
        "High":     "red",
        "Medium":   "yellow",
        "Low":      "green",
        "Info":     "dim",
    }
    status_colours = {
        "open":        "bold",
        "mitigated":   "green",
        "accepted":    "blue",
        "transferred": "blue",
        "wont_fix":    "dim",
    }

    for t in threats:
        sev_style  = severity_colours.get(t.severity.value, "")
        stat_style = status_colours.get(t.status.value, "")
        table.add_row(
            t.id,
            t.title,
            t.stride.value,
            f"[{sev_style}]{t.severity.value}[/{sev_style}]",
            f"[{stat_style}]{t.status.value}[/{stat_style}]",
            str(len(t.evidence)),
        )

    console.print(table)
    console.print(
        f"[dim]{len(threats)} threat(s) shown"
        + (f" (filtered from {len(model.threats)})" if len(threats) != len(model.threats) else "")
        + "[/dim]"
    )
