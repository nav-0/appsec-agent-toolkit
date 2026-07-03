#!/bin/bash
set -euo pipefail

# Hard stop: never let this run bill outside the subscription.
if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
    echo "ANTHROPIC_API_KEY is set — refusing to run to avoid API billing." >&2
    exit 1
fi

cd "$(dirname "$0")/.."
mkdir -p logs

claude -p "$(cat GOAL.md)" \
  --allowedTools "Read,Write,Edit,Grep,Glob,Bash(git *),Bash(gh pr create *),Bash(gh pr view *),Bash(gh pr list *),Bash(gh pr comment *)" \
  --permission-mode dontAsk \
  --model claude-sonnet-4-6 \
  --max-turns 40 \
  --output-format json \
  >> "logs/run-$(date +%F-%H%M).json" 2>&1
