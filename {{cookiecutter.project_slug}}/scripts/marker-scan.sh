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
# strings. Surfaces are loaded from governance-rules.yaml. The
# surfaces read is captured into a plain variable first, then parsed
# line-by-line into an array (rather than read directly from a
# `done < <(...)` process substitution): under `set -euo pipefail`, a
# process substitution's exit status is invisible to the enclosing
# `while` loop, so a governance loader crash specific to
# `--list-marker-surfaces` would otherwise silently leave `surfaces`
# empty and the scan would proceed against zero surfaces instead of
# failing (see CHANGELOG.md, issue #119). The `if ! var="$(...)"`
# guard form propagates the loader's exit code and lets the script
# log a diagnostic naming the exact failing invocation before exiting
# non-zero. The `<<<` here-string parse (rather than `mapfile -t`,
# bash 4+) keeps this bash 3.2-safe.
markers="$("${GOV_LOADER[@]}" --marker-regex)"
if ! surfaces_raw="$("${GOV_LOADER[@]}" --list-marker-surfaces)"; then
  log_error "governance loader failed: ${GOV_LOADER[*]} --list-marker-surfaces"
  exit 1
fi
surfaces=()
while IFS= read -r line; do
  [[ -n "$line" ]] && surfaces+=("$line")
done <<< "$surfaces_raw"

if [[ -z "$markers" ]]; then
  log_error "no prohibited markers configured in $GOV_RULES"
  exit 1
fi

# Filter present surfaces (some land in later phases).
present=()
for s in "${surfaces[@]}"; do
  [[ -e "$s" ]] && present+=("$s")
done

if [[ ${#present[@]} -eq 0 ]]; then
  log_info "no canonical surfaces present yet"
  exit 0
fi

# Check for markers using common function.
matches="$(find_pattern_in_files "$markers" "${present[@]}")"

if [[ -n "$matches" ]]; then
  log_error "stub markers in canonical surfaces:"
  echo "$matches" >&2
  echo "Per CRIT-001, see DIRECTIVES.md for marker list and surface scope." >&2
  exit 1
fi

log_ok "marker-scan (${#present[@]} surface(s) scanned)"
exit 0
