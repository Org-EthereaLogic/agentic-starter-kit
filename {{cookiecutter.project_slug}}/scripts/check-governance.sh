#!/usr/bin/env bash
# scripts/check-governance.sh — enforce CRIT-002
#
# Verifies the required governance files and folders are present.
# Per the phased-enforcement framing in DIRECTIVES.md CRIT-002,
# the "exist now" set is checked strictly; the "later layers add"
# set is checked tolerantly (warn + continue).
#
# Exits 0 if the strict set is satisfied; exits 1 if any strictly-
# required artifact is missing or invalid.

set -euo pipefail

errors=0
warnings=0

check_required_file() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    echo "ERROR: required file missing: $path" >&2
    errors=$((errors + 1))
  fi
}

warn_optional_dir() {
  local path="$1"
  if [[ ! -d "$path" ]]; then
    echo "WARN: optional directory not yet present: $path"
    warnings=$((warnings + 1))
  fi
}

warn_optional_file_in_dir() {
  local dir="$1"
  local pattern="$2"
  if [[ ! -d "$dir" ]]; then
    return
  fi
  if ! find "$dir" -maxdepth 2 -name "$pattern" -print -quit | grep -q .; then
    echo "WARN: $dir contains no files matching '$pattern' yet"
    warnings=$((warnings + 1))
  fi
}

# --- Strictly required files (Layer 1 + Layer 2 + Layer 4) ---

required_files=(
  "CONSTITUTION.md"
  "DIRECTIVES.md"
  "SECURITY.md"
  "README.md"
  "CLAUDE.md"
  "AGENTS.md"
  "GEMINI.md"
  ".claude/settings.json"
  ".claude/hooks/pre-tool-use.js"
)

for f in "${required_files[@]}"; do
  check_required_file "$f"
done

# --- Hook content checks (CRIT-008) ---

hook_path=".claude/hooks/pre-tool-use.js"
if [[ -f "$hook_path" && ! -s "$hook_path" ]]; then
  echo "ERROR: $hook_path is empty" >&2
  errors=$((errors + 1))
fi

settings_path=".claude/settings.json"
if [[ -f "$settings_path" ]]; then
  if ! grep -q "pre-tool-use.js" "$settings_path"; then
    echo "ERROR: $settings_path does not register pre-tool-use.js" >&2
    errors=$((errors + 1))
  fi
fi

# --- Optionally required (later phases populate) ---

optional_dirs=(
  "docs"
  "specs/deep_specs"
  "specs/security-requirements"
  "report"
)

for d in "${optional_dirs[@]}"; do
  warn_optional_dir "$d"
done

warn_optional_file_in_dir "specs/deep_specs" "*.md"

# --- Verdict ---

if [[ $errors -gt 0 ]]; then
  echo "" >&2
  echo "governance-check FAILED — $errors error(s), $warnings warning(s)" >&2
  echo "Per DIRECTIVES.md CRIT-002, the strictly-required artifacts" >&2
  echo "must exist on every commit to the default branch." >&2
  exit 1
fi

echo "governance-check OK ($warnings warning(s) about future-phase artifacts)"
exit 0
