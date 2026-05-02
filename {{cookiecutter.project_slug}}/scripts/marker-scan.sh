#!/usr/bin/env bash
# scripts/marker-scan.sh — enforce CRIT-001
#
# Scans the canonical surfaces declared in DIRECTIVES.md CRIT-001
# for the prohibited stub-marker strings. Exits 0 on clean, 1 on
# any match.
#
# Self-reference avoidance: the marker tokens are constructed at
# runtime by string concatenation so the script source never
# contains the literal strings the regex matches. The script lives
# in scripts/ which is not a canonical surface, but the
# concatenation pattern is defensive in case the script is ever
# moved or copied.

set -euo pipefail

# Build the marker regex from concatenated halves so this source
# file does not match the regex it constructs.
m1="TO"; m2="DO"
m3="FIX"; m4="ME"
m5="TB"; m6="D"
m7="PLACE"; m8="HOLDER"
markers="${m1}${m2}|${m3}${m4}|${m5}${m6}|${m7}${m8}"

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
  if [[ -e "$s" ]]; then
    present+=("$s")
  fi
done

if [[ ${#present[@]} -eq 0 ]]; then
  echo "marker-scan: no canonical surfaces present yet"
  exit 0
fi

# Run rg if available (faster + better defaults), grep fallback.
matches=""
if command -v rg >/dev/null 2>&1; then
  matches="$(rg --no-heading --line-number --color=never \
    --regexp "\\b(${markers})\\b" "${present[@]}" 2>/dev/null || true)"
else
  for s in "${present[@]}"; do
    if [[ -d "$s" ]]; then
      hits="$(grep -rnE "\\b(${markers})\\b" "$s" 2>/dev/null || true)"
    else
      hits="$(grep -nE "\\b(${markers})\\b" "$s" 2>/dev/null || true)"
    fi
    if [[ -n "$hits" ]]; then
      matches="${matches}${hits}"$'\n'
    fi
  done
fi

if [[ -n "$matches" ]]; then
  echo "marker-scan FAILED — stub markers in canonical surfaces:" >&2
  echo "$matches" >&2
  echo "" >&2
  echo "Per CRIT-001, the following strings must not appear in" >&2
  echo "canonical surfaces: see DIRECTIVES.md for the full list" >&2
  echo "and surface scope. Replace with angle-bracket placeholders" >&2
  echo "or rewrite the prose." >&2
  exit 1
fi

echo "marker-scan OK (${#present[@]} surface(s) scanned)"
exit 0
