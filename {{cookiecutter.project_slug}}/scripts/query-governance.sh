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

# Source common utilities for the `governance_python` helper.
# shellcheck disable=SC1091  # path is dynamic via $SCRIPT_DIR; not statically resolvable
source "$SCRIPT_DIR/lib/common.sh"

cd "$REPO_ROOT"

read -r -a _PYTHON_CMD <<< "$(governance_python)"
"${_PYTHON_CMD[@]}" "$SCRIPT_DIR/lib/governance.py" "$@"
