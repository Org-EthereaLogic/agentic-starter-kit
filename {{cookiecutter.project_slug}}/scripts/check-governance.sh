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
  awk -v key="$key" '
    NR == 1 {
      if ($0 != "---") exit 1
      opened = 1
      next
    }
    $0 == "---" {
      closed = 1
      exit
    }
    {
      line = $0
      sub(/^[[:space:]]*/, "", line)
      if (index(line, key ":") == 1) found = 1
    }
    END {
      if (!opened || !closed || !found) exit 1
    }
  ' "$file"
}

frontmatter_value() {
  local file="$1"
  local key="$2"
  local value
  if ! value="$(awk -v key="$key" '
    NR == 1 {
      if ($0 != "---") exit 1
      opened = 1
      next
    }
    $0 == "---" {
      closed = 1
      exit
    }
    {
      line = $0
      sub(/^[[:space:]]*/, "", line)
      prefix = key ":"
      if (!found && index(line, prefix) == 1) {
        value = substr(line, length(prefix) + 1)
        sub(/^[[:space:]]*/, "", value)
        found = 1
      }
    }
    END {
      if (!opened || !closed || !found) exit 1
      print value
    }
  ' "$file")"; then
    return 1
  fi
  value="${value//\"/}"
  value="${value//\'/}"
  printf '%s\n' "$value"
}

# --- Governance list data (required_files, required_agents, ---
# --- required_skills, optional_dirs) ---
# Loaded from governance-rules.yaml in a single loader invocation via
# `--emit`, rather than one `--list-*` subprocess per list (4 Python
# interpreter startups collapsed to 1). `mapfile` would be cleaner but
# is bash 4+ and these scripts target bash 3.2 (macOS default), so the
# combined tab-separated `section<TAB>value` output is captured into a
# plain variable first, then demuxed per section via
# `read_lines_into_array`. Capturing first (rather than reading
# directly from a `done < <(...)` process substitution) matters under
# `set -euo pipefail`: a process substitution's exit status is
# invisible to the enclosing `while` loop, so a governance loader
# crash (corrupt governance-rules.yaml, missing PyYAML) would
# silently leave every list empty and every loader-driven check would
# be skipped instead of failing — this is what let CRIT-002 pass
# vacuously (see CHANGELOG.md, issue #104). The `if ! var="$(...)"`
# guard form propagates the loader's exit code and lets the script
# log a diagnostic naming the exact failing invocation before
# exiting non-zero, and now covers all four lists since they share
# one invocation. (`scripts/marker-scan.sh` carried a milder instance
# of this same vacuous-pass risk in its `--list-marker-surfaces`
# read, which used the unguarded `done < <(...)` form; issue #119
# applied this same capture-first guard there too.)

if ! governance_lists_raw="$("${GOV_LOADER[@]}" --emit required_files,required_agents,required_skills,optional_dirs)"; then
  log_error "governance loader failed: ${GOV_LOADER[*]} --emit required_files,required_agents,required_skills,optional_dirs"
  exit 1
fi

# Demux the combined `section<TAB>value` stream per section. Strip only
# the leading `section<TAB>` prefix (`sub(/^[^\t]*\t/, "")`) rather than
# printing `$2`, so a value that itself contains a tab is preserved in
# full instead of being truncated at its first embedded tab. For the
# common tab-free values this is byte-identical to `print $2`. The
# emitter (`governance.py --emit`) refuses to emit a value containing a
# newline, so the one-item-per-line framing here is always intact.
required_files_raw="$(printf '%s\n' "$governance_lists_raw" | awk -F'\t' '$1 == "required_files" { sub(/^[^\t]*\t/, ""); print }')"
required_agents_raw="$(printf '%s\n' "$governance_lists_raw" | awk -F'\t' '$1 == "required_agents" { sub(/^[^\t]*\t/, ""); print }')"
required_skills_raw="$(printf '%s\n' "$governance_lists_raw" | awk -F'\t' '$1 == "required_skills" { sub(/^[^\t]*\t/, ""); print }')"
optional_dirs_raw="$(printf '%s\n' "$governance_lists_raw" | awk -F'\t' '$1 == "optional_dirs" { sub(/^[^\t]*\t/, ""); print }')"

# --- Strictly required files (Layer 1 + Layer 2 + Layer 4) ---

read_lines_into_array "$required_files_raw"
required_files=( ${READ_LINES_RESULT[@]+"${READ_LINES_RESULT[@]}"} )

for f in ${required_files[@]+"${required_files[@]}"}; do
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

read_lines_into_array "$required_agents_raw"
required_agents=( ${READ_LINES_RESULT[@]+"${READ_LINES_RESULT[@]}"} )

for f in ${required_agents[@]+"${required_agents[@]}"}; do
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

read_lines_into_array "$required_skills_raw"
required_skills=( ${READ_LINES_RESULT[@]+"${READ_LINES_RESULT[@]}"} )

for f in ${required_skills[@]+"${required_skills[@]}"}; do
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

read_lines_into_array "$optional_dirs_raw"
optional_dirs=( ${READ_LINES_RESULT[@]+"${READ_LINES_RESULT[@]}"} )

for d in ${optional_dirs[@]+"${optional_dirs[@]}"}; do
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
