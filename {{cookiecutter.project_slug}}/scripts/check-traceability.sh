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
ids_raw="$(jq -r '.criteria[].id // empty' "$matrix")"
read_lines_into_array "$ids_raw"
ids=( ${READ_LINES_RESULT[@]+"${READ_LINES_RESULT[@]}"} )

for id in "${ids[@]:-}"; do
  [[ -z "$id" ]] && continue
  # source / tests / evidence, extracted in a single jq pass per
  # criterion (down from three) as tab-separated `field<TAB>value`
  # lines, then demuxed per field.
  #
  # The tab-delimited line protocol frames exactly one value per line
  # (`field<TAB>value\n`). A value containing an embedded NEWLINE cannot
  # be represented: it would split across physical lines and the untagged
  # continuation line would be silently dropped by the awk demux below.
  # This site consumes jq output from "$matrix", not governance.py --emit,
  # so it is NOT protected by that emitter's newline guard — mirror the
  # same loud-failure philosophy here: detect any newline-bearing
  # source/tests/evidence value inside the single jq pass (`error(...)`
  # makes jq exit non-zero) and turn a non-zero jq exit into an explicit
  # log_error + exit 1, rather than silently dropping the value. An
  # embedded TAB is fine — the demux strips only the leading `field<TAB>`
  # prefix and preserves the rest of the value verbatim.
  if ! fields_raw="$(jq -r --arg id "$id" \
    'def reject_newline(field):
       if (type == "string" and contains("\n")) then
         error("criterion \($id) \(field) value contains an embedded newline: \(.)")
       else . end;
     .criteria[] | select(.id == $id) | (
       ((.source // [])[]   | reject_newline("source")   | "source\t\(.)"),
       ((.tests // [])[]    | reject_newline("tests")    | "tests\t\(.)"),
       ((.evidence // [])[] | reject_newline("evidence") | "evidence\t\(.)")
     )' "$matrix")"; then
    log_error "criterion $id: a source/tests/evidence value contains an embedded newline, which cannot be represented in the tab-delimited field protocol (refusing to silently drop it)"
    exit 1
  fi

  # Demux per field by stripping only the leading `field<TAB>` prefix
  # (`sub(/^[^\t]*\t/, "")`) rather than printing `$2`, so a source/tests
  # glob or evidence path that itself contains a tab is preserved in full
  # instead of being truncated at its first embedded tab. Byte-identical
  # to `print $2` for tab-free values.
  sources_raw="$(printf '%s\n' "$fields_raw" | awk -F'\t' '$1 == "source" { sub(/^[^\t]*\t/, ""); print }')"
  read_lines_into_array "$sources_raw"
  sources=( ${READ_LINES_RESULT[@]+"${READ_LINES_RESULT[@]}"} )
  for g in "${sources[@]:-}"; do
    [[ -z "$g" ]] && continue
    if ! compgen -G "$g" >/dev/null 2>&1; then
      log_error "criterion $id source glob matches no files: $g"
    fi
  done

  tests_raw="$(printf '%s\n' "$fields_raw" | awk -F'\t' '$1 == "tests" { sub(/^[^\t]*\t/, ""); print }')"
  read_lines_into_array "$tests_raw"
  tests=( ${READ_LINES_RESULT[@]+"${READ_LINES_RESULT[@]}"} )
  for g in "${tests[@]:-}"; do
    [[ -z "$g" ]] && continue
    if ! compgen -G "$g" >/dev/null 2>&1; then
      log_error "criterion $id tests glob matches no files: $g"
    fi
  done

  evidence_raw="$(printf '%s\n' "$fields_raw" | awk -F'\t' '$1 == "evidence" { sub(/^[^\t]*\t/, ""); print }')"
  read_lines_into_array "$evidence_raw"
  evidence=( ${READ_LINES_RESULT[@]+"${READ_LINES_RESULT[@]}"} )
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
