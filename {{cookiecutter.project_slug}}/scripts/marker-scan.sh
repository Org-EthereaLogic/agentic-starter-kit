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

# Build the marker regex from concatenated halves (defensive self-ref avoidance).
m1="TO"; m2="DO"
m3="FIX"; m4="ME"
m5="TB"; m6="D"
m7="PLACE"; m8="HOLDER"
markers="\\b(${m1}${m2}|${m3}${m4}|${m5}${m6}|${m7}${m8})\\b"

# Canonical surfaces per CRIT-001.
surfaces=(
  "specs"
  ".claude"
  "CLAUDE.md"
  "AGENTS.md"
  "GEMINI.md"
  "docs"
)

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
