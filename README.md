# AppSec Agent Toolkit

A growing set of small, practical AppSec tools, built incrementally by
an autonomous Claude Code agent under human PR review. See GOAL.md for
the agent's operating mandate.

---

## tm — threat-model CLI

`tm` scaffolds, validates, and lists structured threat models. Threat
models live in YAML files that conform to `schema/threat_model_v1.json`.

### Install

```bash
pip install -e .
```

### Quickstart

```bash
# Create a starter threat model for a two-tier app:
tm init "My API" \
    --description "REST API backed by Postgres" \
    -c api:backend:Backend \
    -c database:db:Primary\ DB \
    -f threat-model.yaml

# Review the threats at a glance:
tm list threat-model.yaml

# Filter to open, high-severity threats only:
tm list threat-model.yaml --status open --severity High
```

`tm init` pre-populates one illustrative STRIDE threat per category.
Edit the YAML to replace the examples with the real threats for your app,
then use `tm list` to review them during a test session.

### Schema

`schema/threat_model_v1.json` is the canonical shape for all threat
model files. Fields of note:

| Field | Description |
|---|---|
| `app` | App metadata (name, description, repo, owner) |
| `components` | System components being modelled |
| `trust_boundaries` | Logical security zones |
| `threats[].stride` | STRIDE category |
| `threats[].severity` | Critical / High / Medium / Low / Info |
| `threats[].test_cases` | Concrete test steps for the tester |
| `threats[].evidence` | Captured artefacts; filled in during testing |
| `threats[].status` | open / mitigated / accepted / transferred / wont_fix |

---

## Roadmap

See [ROADMAP.md](ROADMAP.md).
