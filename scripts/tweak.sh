#!/bin/bash
set -euo pipefail
PR_NUMBER="$1"
cd "$(dirname "$0")/.."
mkdir -p logs

BRANCH=$(gh pr view "$PR_NUMBER" --json headRefName -q .headRefName)
git fetch origin "$BRANCH" && git checkout "$BRANCH"

claude -p "Read all review comments and the description on PR #$PR_NUMBER using \
'gh pr view $PR_NUMBER --comments' and 'gh api repos/{owner}/{repo}/pulls/$PR_NUMBER/comments'. \
Address every unresolved comment with a code change. Commit each fix separately \
with a message referencing the comment it addresses. Push directly to the existing \
branch '$BRANCH' — do not open a new PR. When done, post a summary comment on the \
PR via 'gh pr comment' describing what changed." \
  --allowedTools "Read,Write,Edit,Grep,Glob,Bash(git *),Bash(gh pr view *),Bash(gh pr comment *),Bash(gh api *)" \
  --permission-mode dontAsk \
  --model claude-sonnet-4-6 \
  --max-turns 30 \
  --output-format json \
  >> "logs/tweak-pr-$PR_NUMBER-$(date +%F-%H%M).json" 2>&1

git push origin "$BRANCH"
