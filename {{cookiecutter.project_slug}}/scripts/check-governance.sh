#!/usr/bin/env bash
# scripts/check-governance.sh — enforce CRIT-002
#
# Verifies the required governance files and folders are present.
# Per DIRECTIVES.md CRIT-002, "exist now" is checked strictly;
# "later layers add" is checked tolerantly (warn + continue).

set -euo pipefail

# Source common utilities. Note: this script operates on the
# current working directory (callers like Make and the
# skill-contract test suite invoke it from the project root they
# want to validate; that may not be the script's own repo).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091  # path is dynamic via $SCRIPT_DIR; not statically resolvable
source "$SCRIPT_DIR/lib/common.sh"

# --- Governance data source (CRIT-002 source of truth) ---

GOV_RULES="${GOV_RULES:-governance-rules.yaml}"
read -r -a _PYTHON_CMD <<< "$(governance_python)"
GOV_LOADER=("${_PYTHON_CMD[@]}" "$SCRIPT_DIR/lib/governance.py" "--file" "$GOV_RULES")

if [[ ! -f "$GOV_RULES" ]]; then
  log_error "$GOV_RULES not found; cannot enforce CRIT-002"
  exit 1
fi

frontmatter_has_key() {
  local file="$1"
  local key="$2"
  grep -q "^[[:space:]]*$key:" "$file"
}

frontmatter_value() {
  local file="$1"
  local key="$2"
  grep -m1 "^[[:space:]]*$key:" "$file" \
    | sed -E "s/^[[:space:]]*$key:[[:space:]]*//" \
    | tr -d '"' \
    | tr -d "'"
}

# --- Strictly required files (Layer 1 + Layer 2 + Layer 4) ---
# Loaded from governance-rules.yaml ▸ required_files. The read-loop
# below replaces an inline bash array; `mapfile` would be cleaner
# but is bash 4+ and these scripts target bash 3.2 (macOS default).

required_files=()
while IFS= read -r line; do
  [[ -n "$line" ]] && required_files+=("$line")
done < <("${GOV_LOADER[@]}" --list-required-files)

for f in "${required_files[@]}"; do
  check_file_exists "$f" || true
done

# --- .mcp.json structural check ---

if [[ -f ".mcp.json" ]]; then
  if ! command -v node >/dev/null 2>&1; then
    log_error "node is required to validate .mcp.json (see docs/MCP_POLICY.md)"
  elif ! node -e 'const fs = require("fs"); const parsed = JSON.parse(fs.readFileSync(".mcp.json", "utf8")); const servers = parsed && parsed.mcpServers; const isObject = typeof servers === "object" && servers !== null && !Array.isArray(servers); process.exit(isObject ? 0 : 1);' 2>/dev/null; then
    log_error ".mcp.json must contain a top-level \"mcpServers\" object (see docs/MCP_POLICY.md)"
  fi
fi

# --- Hook content checks (CRIT-008) ---
#
# CRIT-008 is enforced at two layers. Assert the presence/wiring of both
# as repo-state facts only (files exist, are executable, and the install
# wiring is checked in). Deliberately do NOT read the live
# `git config core.hooksPath` value: on a fresh render / CI checkout the
# operator has not run `make hooks-install` yet, and governance-check
# must stay green there. The runtime wiring is exercised by the
# hooks-test suite (tests/test_git_hooks.sh), not by this static check.

# Agent-layer defense-in-depth: the Claude Code PreToolUse:Bash hook.
hook_path=".claude/hooks/pre-tool-use.js"
check_file_not_empty "$hook_path" || true

settings_path=".claude/settings.json"
if [[ -f "$settings_path" ]]; then
  if ! grep -q "pre-tool-use.js" "$settings_path"; then
    log_error "$settings_path does not register pre-tool-use.js"
  fi
fi

# Git-layer primary boundary: the checked-in git hooks must exist and be
# executable (git will not run a non-executable hook).
for githook in .githooks/pre-commit .githooks/pre-merge-commit .githooks/pre-push; do
  if [[ ! -f "$githook" ]]; then
    log_error "$githook missing (git-layer CRIT-008 boundary)"
  elif [[ ! -x "$githook" ]]; then
    log_error "$githook is not executable (git will not run it)"
  fi
done

# The core.hooksPath install wiring must be checked in (Makefile
# fragment), so `make hooks-install` can wire the boundary reproducibly.
hooks_mk="Makefile.fragments/hooks.mk"
if [[ -f "$hooks_mk" ]]; then
  if ! grep -q "core.hooksPath" "$hooks_mk" || ! grep -q "\.githooks" "$hooks_mk"; then
    log_error "$hooks_mk does not wire core.hooksPath to .githooks (hooks-install)"
  fi
else
  log_error "$hooks_mk missing; cannot verify core.hooksPath install wiring"
fi

# --- Layer 3 agent inventory (Phase B1) ---
#
# Six agents are always required regardless of primary_language.
# Loaded from governance-rules.yaml ▸ required_agents.
# At least one of python-pro / typescript-pro must be present; the
# polyglot path keeps both, single-language paths keep one (this
# language-conditional check stays here, not in YAML).

required_agents=()
while IFS= read -r line; do
  [[ -n "$line" ]] && required_agents+=("$line")
done < <("${GOV_LOADER[@]}" --list-required-agents)

for f in "${required_agents[@]}"; do
  check_file_exists "$f" || true
done

if [[ -d ".claude/agents" ]]; then
  if [[ ! -f ".claude/agents/python-pro.md" && ! -f ".claude/agents/typescript-pro.md" ]]; then
    log_error "no language-specific agent present; expected python-pro.md or typescript-pro.md"
  fi
  for agent in .claude/agents/*.md; do
    [[ -f "$agent" ]] || continue
    [[ "$(basename "$agent")" == "README.md" ]] && continue
    if ! frontmatter_has_key "$agent" "name" || \
       ! frontmatter_has_key "$agent" "description" || \
       ! frontmatter_has_key "$agent" "model" || \
       ! frontmatter_has_key "$agent" "memory"; then
      log_error "$agent missing required frontmatter (name, description, model, memory)"
    fi
  done
fi

# --- Layer 3 skill inventory (Phase B3) ---
#
# Skills are progressive-disclosure capability packs per the Linux
# Foundation SKILL.md spec. Each skill is a single .md with YAML
# frontmatter declaring `name`, `description`, and `paths:` (a glob
# list that gates lazy loading). Loaded from
# governance-rules.yaml ▸ required_skills.

required_skills=()
while IFS= read -r line; do
  [[ -n "$line" ]] && required_skills+=("$line")
done < <("${GOV_LOADER[@]}" --list-required-skills)

for f in "${required_skills[@]}"; do
  check_file_exists "$f" || true
done

if [[ -d ".claude/skills" ]]; then
  for skill in .claude/skills/*.md; do
    [[ -f "$skill" ]] || continue
    [[ "$(basename "$skill")" == "README.md" ]] && continue
    if ! frontmatter_has_key "$skill" "name" || \
       ! frontmatter_has_key "$skill" "description" || \
       ! frontmatter_has_key "$skill" "paths"; then
      log_error "$skill missing required frontmatter (name, description, paths)"
      continue
    fi
    expected_name="$(basename "$skill" .md)"
    declared_name="$(frontmatter_value "$skill" "name")"
    if [[ "$declared_name" != "$expected_name" ]]; then
      log_error "$skill frontmatter name '$declared_name' does not match filename '$expected_name'"
    fi
  done
fi

# --- Optionally required (later phases populate) ---
# Loaded from governance-rules.yaml ▸ optional_dirs.

optional_dirs=()
while IFS= read -r line; do
  [[ -n "$line" ]] && optional_dirs+=("$line")
done < <("${GOV_LOADER[@]}" --list-optional-dirs)

for d in "${optional_dirs[@]}"; do
  check_dir_exists "$d" || log_warn "optional directory not yet present: $d"
done

if check_dir_exists "specs/deep_specs"; then
  if ! find "specs/deep_specs" -maxdepth 2 -name "*.md" -print -quit | grep -q .; then
    log_warn "specs/deep_specs contains no .md files yet"
  fi
fi

# --- Report ---

report_status "governance-check" \
  "Per DIRECTIVES.md CRIT-002, strictly-required artifacts must exist on every commit."
