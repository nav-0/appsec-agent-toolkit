# Roadmap

Items are rough priority order; everything is subject to the "one
self-contained increment per run" constraint.

## Near-term

- **`tm show <id>`** — pretty-print a single threat: description,
  mitigations, test cases, and any captured evidence.
- **`tm capture <id> <file>`** — attach an evidence file to a threat
  (screenshot, HTTP trace, log snippet) and record a pass/fail result;
  timestamps automatically.
- **`tm report`** — render a threat model to Markdown or HTML, suitable
  for pasting into a pentest report or sending to a dev team.

## Medium-term

- **`tm validate`** — explicit JSON Schema validation command with
  human-readable output; useful as a pre-commit hook.
- **`tm walk`** — interactive tester mode: for each open threat, show
  test cases one at a time, prompt for evidence capture, and record a
  result.
- **SARIF export** — map threats to SARIF so findings can be imported
  into GitHub Security or other tooling that speaks SARIF.

## Speculative / needs a real itch

- Bidirectional sync with a ticketing system (Linear, Jira) — map each
  threat to a ticket and pull back status.
- MITRE ATT&CK / CAPEC mapping on threats to cross-reference with
  detection coverage.
- Diff two threat model versions to surface newly added or removed
  threats (useful for security reviews of feature PRs).
