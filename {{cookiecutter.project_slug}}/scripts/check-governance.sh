#!/usr/bin/env bash
# scripts/check-governance.sh — enforce CRIT-002
#
# Verifies the required governance files and folders are present.
# Per DIRECTIVES.md CRIT-002, "exist now" is checked strictly;
# "later layers add" is checked tolerantly (warn + continue).

set -euo pipefail

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

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
  ".mcp.json"
  "docs/MCP_POLICY.md"
)

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

hook_path=".claude/hooks/pre-tool-use.js"
check_file_not_empty "$hook_path" || true

settings_path=".claude/settings.json"
if [[ -f "$settings_path" ]]; then
  if ! grep -q "pre-tool-use.js" "$settings_path"; then
    log_error "$settings_path does not register pre-tool-use.js"
  fi
fi

# --- Layer 3 agent inventory (Phase B1) ---
#
# Six agents are always required regardless of primary_language.
# At least one of python-pro / typescript-pro must be present; the
# polyglot path keeps both, single-language paths keep one.

required_agents=(
  ".claude/agents/lead-software-engineer.md"
  ".claude/agents/sdlc-technical-writer.md"
  ".claude/agents/test-automator.md"
  ".claude/agents/ux-delight-specialist.md"
  ".claude/agents/security-reviewer.md"
  ".claude/agents/governance-auditor.md"
)

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
    if ! grep -q "^name:" "$agent" || \
       ! grep -q "^description:" "$agent" || \
       ! grep -q "^model:" "$agent" || \
       ! grep -q "^memory:" "$agent"; then
      log_error "$agent missing required frontmatter (name, description, model, memory)"
    fi
  done
fi

# --- Layer 3 skill inventory (Phase B3) ---
#
# Skills are progressive-disclosure capability packs per the Linux
# Foundation SKILL.md spec. Each skill is a single .md with YAML
# frontmatter declaring `name`, `description`, and `paths:` (a glob
# list that gates lazy loading). Three starter skills ship with the
# template; renaming one without updating this list is a finding.

required_skills=(
  ".claude/skills/run-validate.md"
  ".claude/skills/audit-trail-tail.md"
  ".claude/skills/traceability-update.md"
)

for f in "${required_skills[@]}"; do
  check_file_exists "$f" || true
done

if [[ -d ".claude/skills" ]]; then
  for skill in .claude/skills/*.md; do
    [[ -f "$skill" ]] || continue
    [[ "$(basename "$skill")" == "README.md" ]] && continue
    if ! grep -q "^name:" "$skill" || \
       ! grep -q "^description:" "$skill" || \
       ! grep -q "^paths:" "$skill"; then
      log_error "$skill missing required frontmatter (name, description, paths)"
      continue
    fi
    expected_name="$(basename "$skill" .md)"
    declared_name="$(grep -m1 "^name:" "$skill" | sed -E 's/^name:[[:space:]]*//' | tr -d '"' | tr -d "'")"
    if [[ "$declared_name" != "$expected_name" ]]; then
      log_error "$skill frontmatter name '$declared_name' does not match filename '$expected_name'"
    fi
  done
fi

# --- Optionally required (later phases populate) ---

optional_dirs=(
  "docs"
  "specs/deep_specs"
  "specs/security-requirements"
  "report"
)

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
