#!/usr/bin/env bash
# scripts/check-doc-drift.sh — verify path references in living docs
#
# Walks every markdown file under docs/ and specs/ and extracts
# backtick-wrapped path-like tokens. For each token, verifies the
# referenced path exists in the repo. Surfaces drift (referenced
# path missing) as findings.
#
# Modes:
#   warn  (default) — exits 0 with findings on stderr
#   block           — exits 1 if any drift finding
#
# Initial deployment uses warn mode while docs and specs are
# stabilizing. A later phase hardens to block.

set -euo pipefail

mode="${1:-warn}"

if [[ ! -d docs && ! -d specs ]]; then
  echo "check-doc-drift: no docs/ or specs/ directory yet (later phases populate)"
  exit 0
fi

# Collect markdown files.
mapfile -t md_files < <(
  { find docs -name '*.md' 2>/dev/null; find specs -name '*.md' 2>/dev/null; } \
    | sort -u
)

if [[ ${#md_files[@]} -eq 0 ]]; then
  echo "check-doc-drift: no markdown files in docs/ or specs/ yet"
  exit 0
fi

# Extract backtick-wrapped path-like tokens from each file.
# Pattern: `<path>` where path has at least one slash, an extension,
# and contains only safe path characters.
findings=0
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
        echo "DRIFT in $f: referenced path does not exist: $path"
        reported[$key]=1
        findings=$((findings + 1))
      fi
    fi
  done < <(grep -hoE '`[A-Za-z0-9_./-]+\.(md|json|sh|js|py|ts|yml|yaml|toml|cff)`' "$f" 2>/dev/null || true)
done

if [[ $findings -eq 0 ]]; then
  echo "check-doc-drift OK (${#md_files[@]} markdown file(s) scanned)"
  exit 0
fi

echo "" >&2
echo "check-doc-drift: $findings drift finding(s)" >&2
if [[ "$mode" == "block" ]]; then
  exit 1
fi
echo "(warn mode — not blocking; pass 'block' as the first arg to harden)" >&2
exit 0
