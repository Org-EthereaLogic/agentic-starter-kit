#!/usr/bin/env bash
# scripts/marker-scan.sh — enforce CRIT-001
#
# Scans the canonical surfaces declared in DIRECTIVES.md CRIT-001
# for the prohibited stub-marker strings. Exits 0 on clean, 1 on
# any match.

set -euo pipefail

# Source common utilities. Note: this script operates on the
# current working directory (callers like Make and the
# skill-contract test suite invoke it from the project root they
# want to validate; that may not be the script's own repo).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091  # path is dynamic via $SCRIPT_DIR; not statically resolvable
source "$SCRIPT_DIR/lib/common.sh"

# --- Governance data source (CRIT-001 source of truth) ---

GOV_RULES="${GOV_RULES:-governance-rules.yaml}"
read -r -a _PYTHON_CMD <<< "$(governance_python)"
GOV_LOADER=("${_PYTHON_CMD[@]}" "$SCRIPT_DIR/lib/governance.py" "--file" "$GOV_RULES")

if [[ ! -f "$GOV_RULES" ]]; then
  log_error "$GOV_RULES not found; cannot enforce CRIT-001"
  exit 1
fi

# Marker regex is assembled from split [prefix, suffix] pairs in the
# YAML so the rules file itself never carries the literal forbidden
# strings. Both the regex and the surfaces list are loaded from
# governance-rules.yaml in a single loader invocation via `--emit`
# (one Python interpreter startup instead of two). The combined
# tab-separated output is captured into a plain variable first, then
# demuxed per section (rather than read directly from a
# `done < <(...)` process substitution): under `set -euo pipefail`, a
# process substitution's exit status is invisible to the enclosing
# `while` loop, so a governance loader crash would otherwise silently
# leave `surfaces` empty and the scan would proceed against zero
# surfaces instead of failing (see CHANGELOG.md, issue #119). The
# `if ! var="$(...)"` guard form propagates the loader's exit code and
# lets the script log a diagnostic naming the exact failing invocation
# before exiting non-zero. The `<<<` here-string parse (rather than
# `mapfile -t`, bash 4+) keeps this bash 3.2-safe.
if ! marker_data_raw="$("${GOV_LOADER[@]}" --emit marker_regex,marker_surfaces)"; then
  log_error "governance loader failed: ${GOV_LOADER[*]} --emit marker_regex,marker_surfaces"
  exit 1
fi
# Demux per section by stripping only the leading `section<TAB>` prefix
# (`sub(/^[^\t]*\t/, "")`) rather than printing `$2`, so a value that
# itself contains a tab (e.g. a marker regex) survives intact instead of
# being truncated at its first embedded tab. Byte-identical to `print $2`
# for tab-free values; `governance.py --emit` rejects newline-bearing
# values, so the line framing is always intact.
markers="$(printf '%s\n' "$marker_data_raw" | awk -F'\t' '$1 == "marker_regex" { sub(/^[^\t]*\t/, ""); print }')"
surfaces_raw="$(printf '%s\n' "$marker_data_raw" | awk -F'\t' '$1 == "marker_surfaces" { sub(/^[^\t]*\t/, ""); print }')"
read_lines_into_array "$surfaces_raw"
surfaces=( ${READ_LINES_RESULT[@]+"${READ_LINES_RESULT[@]}"} )

if [[ -z "$markers" ]]; then
  log_error "no prohibited markers configured in $GOV_RULES"
  exit 1
fi

# Filter present surfaces (some land in later phases).
present=()
for s in ${surfaces[@]+"${surfaces[@]}"}; do
  [[ -e "$s" ]] && present+=("$s")
done

if [[ ${#present[@]} -eq 0 ]]; then
  log_info "no canonical surfaces present yet"
  exit 0
fi

# Check for markers using common function.
matches="$(find_pattern_in_files "$markers" ${present[@]+"${present[@]}"})"

if [[ -n "$matches" ]]; then
  log_error "stub markers in canonical surfaces:"
  echo "$matches" >&2
  echo "Per CRIT-001, see DIRECTIVES.md for marker list and surface scope." >&2
  exit 1
fi

log_ok "marker-scan (${#present[@]} surface(s) scanned)"
exit 0
