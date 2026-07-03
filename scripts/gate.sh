#!/bin/bash
# Runs daily; fires roughly 3-4 times a month (~12% daily chance).
set -euo pipefail
if (( RANDOM % 100 < 12 )); then
    "$(dirname "$0")/run.sh"
fi
