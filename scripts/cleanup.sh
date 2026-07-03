#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
gh pr list --state closed --json number,headRefName,mergedAt \
  --jq '.[] | select(.mergedAt == null) | .headRefName' | while read -r branch; do
    git push origin --delete "$branch" || true
done
