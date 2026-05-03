#!/usr/bin/env bash
# scripts/check-doc-drift.sh — verify path references in living docs
#
# Walks every markdown file under docs/ and specs/ and extracts
# backtick-wrapped path-like tokens. For each token, verifies the
# referenced path exists in the repo. Surfaces drift (referenced
# path missing) as findings.

set -euo pipefail

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

mode="${1:-warn}"

if [[ ! -d docs && ! -d specs ]]; then
  echo "check-doc-drift: no docs/ or specs/ directory yet (later phases populate)"
  exit 0
fi

# Collect markdown files (compatible with bash 3.2+).
md_files=()
while IFS= read -r f; do
  [[ -z "$f" ]] && continue
  md_files+=("$f")
done < <(
  { find docs -name '*.md' 2>/dev/null; find specs -name '*.md' 2>/dev/null; } \
    | sort -u
)

if [[ ${#md_files[@]} -eq 0 ]]; then
  echo "check-doc-drift: no markdown files in docs/ or specs/ yet"
  exit 0
fi

# Extract backtick-wrapped path-like tokens from each file.
# Pattern matches a backtick-wrapped relative path with at least
# one segment and a known extension. The pattern is a literal
# regex string with no shell substitutions, so the surrounding
# single quotes are intentional.
# shellcheck disable=SC2016
backtick_path_regex='`[A-Za-z0-9_./-]+\.(md|json|sh|js|py|ts|yml|yaml|toml|cff)`'

reset_counters
declare -A reported
for f in "${md_files[@]}"; do
  while IFS= read -r raw; do
    [[ -z "$raw" ]] && continue
    # Strip surrounding backticks.
    path="${raw//\`/}"
    # Skip absolute paths and URLs.
    [[ "$path" =~ ^/ ]] && continue
    [[ "$path" =~ ^https?:// ]] && continue
    # Skip the bare current-dir / parent-dir refs (always exist;
    # don't actually resolve to a file). Do NOT skip dot-prefixed
    # paths like `.claude/...` or `.github/...` — those are real
    # relative paths and must be drift-checked.
    [[ "$path" == "." || "$path" == ".." ]] && continue
    # Resolve relative to repo root (the script is run from there).
    if [[ ! -e "$path" ]]; then
      key="${f}::${path}"
      if [[ -z "${reported[$key]:-}" ]]; then
        log_error "DRIFT in $f: referenced path does not exist: $path"
        reported[$key]=1
      fi
    fi
  done < <(grep -hoE "$backtick_path_regex" "$f" 2>/dev/null || true)
done

if [[ $(get_errors) -eq 0 ]]; then
  log_ok "check-doc-drift (${#md_files[@]} markdown file(s) scanned)"
  exit 0
fi

if [[ "$mode" == "block" ]]; then
  echo "check-doc-drift: $(get_errors) drift finding(s) (blocking)" >&2
  exit 1
fi

echo "check-doc-drift: $(get_errors) drift finding(s) (warn mode — not blocking)" >&2
exit 0
