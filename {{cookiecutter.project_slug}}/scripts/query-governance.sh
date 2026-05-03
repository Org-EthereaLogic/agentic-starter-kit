#!/usr/bin/env bash
# scripts/query-governance.sh — Query governance-rules.yaml
#
# Usage:
#   query-governance.sh --list
#   query-governance.sh --class Critical
#   query-governance.sh --automated
#   query-governance.sh --id CRIT-001
#   query-governance.sh --validate

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 not found; required for governance rule queries"
  exit 1
fi

python3 "$SCRIPT_DIR/lib/governance.py" "$@"
