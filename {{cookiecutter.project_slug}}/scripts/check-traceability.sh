#!/usr/bin/env bash
# scripts/check-traceability.sh — validate specs/traceability.json
#
# When `specs/traceability.json` exists (added in Phase 8), validates:
# 1. JSON well-formedness
# 2. Each criterion's source/tests/evidence globs and paths exist
# 3. Reports drift (orphaned or unmapped criteria)

set -euo pipefail

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

matrix="specs/traceability.json"
schema="specs/traceability.schema.json"
reset_counters

if [[ ! -f "$matrix" ]]; then
  echo "check-traceability: $matrix not present (added in Phase 8)"
  exit 0
fi

if ! command -v jq >/dev/null 2>&1; then
  log_error "jq not installed; required for traceability validation"
  echo "Install via your package manager (brew install jq, apt install jq, ...)" >&2
  exit 1
fi

# Phase-1 validation — JSON well-formedness.
if ! jq empty "$matrix" 2>/dev/null; then
  log_error "$matrix is not valid JSON"
  exit 1
fi

# Phase-2 validation — schema check (when ajv-cli available).
if [[ -f "$schema" ]]; then
  if command -v ajv >/dev/null 2>&1; then
    if ! ajv validate -s "$schema" -d "$matrix" --quiet 2>/dev/null; then
      log_error "$matrix does not conform to $schema"
      exit 1
    fi
  fi
fi

# Phase-3 validation — per-criterion glob and evidence checks.
criteria=$(jq -r '.criteria // [] | length' "$matrix" 2>/dev/null || echo 0)

if [[ "$criteria" -eq 0 ]]; then
  log_ok "check-traceability ($matrix present, 0 criteria mapped)"
  exit 0
fi

# Iterate criteria; for each, validate source / tests / evidence (bash 3.2 compatible).
ids=()
while IFS= read -r id; do
  [[ -z "$id" ]] && continue
  ids+=("$id")
done < <(jq -r '.criteria[].id // empty' "$matrix")

for id in "${ids[@]:-}"; do
  [[ -z "$id" ]] && continue
  # source globs
  sources=()
  while IFS= read -r g; do
    [[ -z "$g" ]] && continue
    sources+=("$g")
  done < <(jq -r --arg id "$id" \
    '.criteria[] | select(.id == $id) | .source // [] | .[]' "$matrix")
  for g in "${sources[@]:-}"; do
    [[ -z "$g" ]] && continue
    if ! compgen -G "$g" >/dev/null 2>&1; then
      log_error "criterion $id source glob matches no files: $g"
    fi
  done

  # tests globs
  tests=()
  while IFS= read -r g; do
    [[ -z "$g" ]] && continue
    tests+=("$g")
  done < <(jq -r --arg id "$id" \
    '.criteria[] | select(.id == $id) | .tests // [] | .[]' "$matrix")
  for g in "${tests[@]:-}"; do
    [[ -z "$g" ]] && continue
    if ! compgen -G "$g" >/dev/null 2>&1; then
      log_error "criterion $id tests glob matches no files: $g"
    fi
  done

  # evidence paths (exact, not globs)
  evidence=()
  while IFS= read -r path; do
    [[ -z "$path" ]] && continue
    evidence+=("$path")
  done < <(jq -r --arg id "$id" \
    '.criteria[] | select(.id == $id) | .evidence // [] | .[]' "$matrix")
  for path in "${evidence[@]:-}"; do
    [[ -z "$path" ]] && continue
    if [[ ! -e "$path" ]]; then
      log_error "criterion $id evidence file missing: $path"
    fi
  done
done

if [[ $(get_errors) -gt 0 ]]; then
  echo "check-traceability FAILED — $(get_errors) drift finding(s)" >&2
  exit 1
fi

log_ok "check-traceability ($criteria criteria, all mappings resolve)"
exit 0
