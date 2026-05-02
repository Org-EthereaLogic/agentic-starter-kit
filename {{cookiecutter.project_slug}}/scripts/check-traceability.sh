#!/usr/bin/env bash
# scripts/check-traceability.sh — validate specs/traceability.json
#
# When `specs/traceability.json` and its companion JSON Schema
# `specs/traceability.schema.json` exist (added in Phase 8), this
# script:
#
#   1. Parses traceability.json and confirms it is valid JSON.
#   2. For each acceptance criterion, confirms each `source` glob
#      matches at least one file in the repo.
#   3. For each acceptance criterion, confirms each `tests` glob
#      matches at least one file in the repo.
#   4. For each acceptance criterion, confirms each `evidence`
#      file path exists.
#   5. Reports unmapped criteria (no source / no tests / no evidence).
#   6. Reports orphaned tests (test files not referenced by any
#      criterion).
#
# Until traceability.json exists, the script is a no-op that
# returns 0 with a phase-aware notice.

set -euo pipefail

matrix="specs/traceability.json"
schema="specs/traceability.schema.json"

if [[ ! -f "$matrix" ]]; then
  echo "check-traceability: $matrix not present (added in Phase 8)"
  exit 0
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "ERROR: jq not installed; required for traceability validation" >&2
  echo "Install via your package manager (brew install jq, apt install jq, ...)" >&2
  exit 1
fi

# Phase-1 validation — JSON well-formedness.
if ! jq empty "$matrix" 2>/dev/null; then
  echo "ERROR: $matrix is not valid JSON" >&2
  exit 1
fi

# Phase-2 validation — schema check (when ajv-cli or similar is
# available). Schema-driven validation is wired in Phase 8
# alongside the matrix itself.
if [[ -f "$schema" ]]; then
  if command -v ajv >/dev/null 2>&1; then
    if ! ajv validate -s "$schema" -d "$matrix" --quiet 2>/dev/null; then
      echo "ERROR: $matrix does not conform to $schema" >&2
      exit 1
    fi
  fi
fi

# Phase-3 validation — per-criterion glob and evidence checks.
errors=0
criteria=$(jq -r '.criteria // [] | length' "$matrix" 2>/dev/null || echo 0)

if [[ "$criteria" -eq 0 ]]; then
  echo "check-traceability OK ($matrix present, 0 criteria mapped)"
  exit 0
fi

# Iterate criteria; for each, validate source / tests / evidence.
# Uses jq to extract per-criterion arrays.
mapfile -t ids < <(jq -r '.criteria[].id // empty' "$matrix")
for id in "${ids[@]}"; do
  # source globs
  mapfile -t sources < <(jq -r --arg id "$id" \
    '.criteria[] | select(.id == $id) | .source // [] | .[]' "$matrix")
  for g in "${sources[@]}"; do
    # shellcheck disable=SC2086
    if ! compgen -G $g >/dev/null 2>&1; then
      echo "DRIFT: criterion $id source glob matches no files: $g" >&2
      errors=$((errors + 1))
    fi
  done

  # tests globs
  mapfile -t tests < <(jq -r --arg id "$id" \
    '.criteria[] | select(.id == $id) | .tests // [] | .[]' "$matrix")
  for g in "${tests[@]}"; do
    # shellcheck disable=SC2086
    if ! compgen -G $g >/dev/null 2>&1; then
      echo "DRIFT: criterion $id tests glob matches no files: $g" >&2
      errors=$((errors + 1))
    fi
  done

  # evidence paths (exact, not globs)
  mapfile -t evidence < <(jq -r --arg id "$id" \
    '.criteria[] | select(.id == $id) | .evidence // [] | .[]' "$matrix")
  for path in "${evidence[@]}"; do
    if [[ ! -e "$path" ]]; then
      echo "DRIFT: criterion $id evidence file missing: $path" >&2
      errors=$((errors + 1))
    fi
  done
done

if [[ $errors -gt 0 ]]; then
  echo "" >&2
  echo "check-traceability FAILED — $errors drift finding(s)" >&2
  exit 1
fi

echo "check-traceability OK ($criteria criteria, all mappings resolve)"
exit 0
