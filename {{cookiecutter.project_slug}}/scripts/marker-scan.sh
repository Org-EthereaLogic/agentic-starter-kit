#!/usr/bin/env bash
# scripts/marker-scan.sh — enforce CRIT-001
#
# Scans the canonical surfaces declared in DIRECTIVES.md CRIT-001
# for the prohibited stub-marker strings. Exits 0 on clean, 1 on
# any match.

set -euo pipefail

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

# --- Governance data source (CRIT-001 source of truth) ---

GOV_RULES="${GOV_RULES:-governance-rules.yaml}"
GOV_LOADER=("python3" "$SCRIPT_DIR/lib/governance.py" "--file" "$GOV_RULES")

if [[ ! -f "$GOV_RULES" ]]; then
  log_error "$GOV_RULES not found; cannot enforce CRIT-001"
  exit 1
fi

# Marker regex is assembled from split [prefix, suffix] pairs in the
# YAML so the rules file itself never carries the literal forbidden
# strings. Surfaces are loaded from governance-rules.yaml. Read-loop
# substitutes for `mapfile -t` (bash 4+) so this stays bash 3.2-safe.
markers="$("${GOV_LOADER[@]}" --marker-regex)"
surfaces=()
while IFS= read -r line; do
  [[ -n "$line" ]] && surfaces+=("$line")
done < <("${GOV_LOADER[@]}" --list-marker-surfaces)

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
