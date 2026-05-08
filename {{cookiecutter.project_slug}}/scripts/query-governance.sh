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

# Source common utilities for `governance_python` helper.
source "$SCRIPT_DIR/lib/common.sh"

cd "$REPO_ROOT"

PYTHON_CMD="$(governance_python)"
# shellcheck disable=SC2086  # intentional word-split for multi-word commands like `uv run python`
$PYTHON_CMD "$SCRIPT_DIR/lib/governance.py" "$@"
