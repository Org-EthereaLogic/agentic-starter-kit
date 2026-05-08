#!/usr/bin/env bash
# scripts/lib/common.sh — shared utilities for validation scripts
#
# Provides common functions for logging, file checking, pattern
# matching, and reporting across all validation scripts.

set -euo pipefail

# Color codes for output (no-op if not a TTY)
if [[ -t 1 ]]; then
  RED='\033[0;31m'
  YELLOW='\033[1;33m'
  GREEN='\033[0;32m'
  NC='\033[0m'  # No Color
else
  RED=''
  YELLOW=''
  GREEN=''
  NC=''
fi

# Global counters
_ERRORS=0
_WARNINGS=0

# Log functions
log_error() {
  echo -e "${RED}ERROR${NC}: $*" >&2
  _ERRORS=$((_ERRORS + 1))
}

log_warn() {
  echo -e "${YELLOW}WARN${NC}: $*"
  _WARNINGS=$((_WARNINGS + 1))
}

log_info() {
  echo -e "${GREEN}ℹ${NC}  $*"
}

log_ok() {
  echo -e "${GREEN}✓${NC}  $*"
}

# File and directory checks
check_file_exists() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    log_error "required file missing: $path"
    return 1
  fi
  return 0
}

check_file_not_empty() {
  local path="$1"
  if [[ ! -f "$path" || ! -s "$path" ]]; then
    log_error "$path is empty or missing"
    return 1
  fi
  return 0
}

check_dir_exists() {
  local path="$1"
  if [[ ! -d "$path" ]]; then
    return 1
  fi
  return 0
}

# Pattern matching
find_pattern_in_files() {
  local pattern="$1"
  shift
  local paths=("$@")

  if command -v rg >/dev/null 2>&1; then
    rg --no-heading --line-number --color=never \
      --regexp "$pattern" "${paths[@]}" 2>/dev/null || true
  else
    local matches=""
    for path in "${paths[@]}"; do
      if [[ -d "$path" ]]; then
        matches="$(grep -rnE "$pattern" "$path" 2>/dev/null || true)${matches:+$'\n'}${matches}"
      elif [[ -f "$path" ]]; then
        matches="$(grep -nE "$pattern" "$path" 2>/dev/null || true)${matches:+$'\n'}${matches}"
      fi
    done
    echo -n "$matches"
  fi
}

# Status reporting
report_status() {
  local script_name="$1"
  local subject="$2"

  if [[ $_ERRORS -gt 0 ]]; then
    echo "" >&2
    echo "${script_name} FAILED — ${_ERRORS} error(s), ${_WARNINGS} warning(s)" >&2
    echo "$subject" >&2
    return 1
  fi

  if [[ $_WARNINGS -gt 0 ]]; then
    echo "${script_name} OK (${_WARNINGS} warning(s))"
  else
    echo "${script_name} OK"
  fi
  return 0
}

# Get counters
get_errors() {
  echo $_ERRORS
}

get_warnings() {
  echo $_WARNINGS
}

# Reset counters (for testing)
reset_counters() {
  _ERRORS=0
  _WARNINGS=0
}

# Resolve a Python interpreter that can import PyYAML. Governance
# scripts read `governance-rules.yaml` via PyYAML; in a clean dev
# container the system `python3` has no third-party packages, so
# hardcoding `python3` made governance checks fail immediately after
# `make sync` succeeded.
#
# Resolution order:
#   1. `.venv/bin/python` — exists for Python/polyglot variants
#      after `uv sync` (PyYAML installed via project deps).
#   2. `uv run --quiet python` if uv is on PATH and pyproject.toml
#      is present — uv resolves the project venv on demand.
#   3. `uv run --quiet --with pyyaml python` if uv is on PATH but
#      no pyproject.toml — TS-only variants. uv materializes a
#      transient env with PyYAML on first call (cached after).
#   4. `python3` as a last resort — works only when the operator
#      has PyYAML installed globally.
#
# Output is space-separated command words. Callers should split
# into an array via `read -r -a` so multi-word commands (like
# `uv run --quiet python`) are passed as individual argv entries:
#
#   read -r -a PYTHON_CMD <<< "$(governance_python)"
#   "${PYTHON_CMD[@]}" path/to/script.py "$@"
governance_python() {
  if [[ -x ".venv/bin/python" ]]; then
    echo ".venv/bin/python"
  elif command -v uv >/dev/null 2>&1; then
    if [[ -f "pyproject.toml" ]]; then
      echo "uv run --quiet python"
    else
      echo "uv run --quiet --with pyyaml python"
    fi
  else
    echo "python3"
  fi
}
