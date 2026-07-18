# Standards Register

This document is the human-readable companion to the
`governance-review` validator. Each `GOV-NNN` finding includes a link
to one of the sections below; the section explains the rule, why it
exists, what artifact enforces it, and how to fix a failure.

The validator's check inventory and severity levels are the source
of truth for the IDs (`governance-review --list-checks`). When this
document and the validator drift, the validator wins — update the
section here to match.

## Standards anchored by these checks

- **SWEBOK v4 (2024)** — knowledge area coverage drives which surfaces
  must exist (governance, configuration, quality, security).
- **ISO/IEC/IEEE 32675:2022** — DevOps governance vocabulary and
  enforcement-point taxonomy (script / hook / reviewer).
- **IEEE 42010:2022** — architecture description: directives are
  framework constraints, traceability matrices link them to evidence.
- **IEEE 2675:2021** — DevOps lifecycle requirements; maps to the
  Plan / Act / Verify / Report loop in `AGENTS.md`.
- **AGENTS.md format** — tier-1 navigation contract for AI coding
  agents (Codex, Cursor, Aider, Jules, Roo). The hard rule is that
  human and machine readers see the same source.
- **CycloneDX 1.6 / SPDX 2.3** — SBOM formats accepted by the
  `make sbom` job when `include_sbom == "yes"`.
- **CERT Top 10 (2025)** — secure-coding rules referenced from the
  language linters (`ruff S`, `eslint security`).

A finding's `helpUri` (in SARIF output) and the rendered text output
both point back to the corresponding `GOV-NNN` section here.

---

## GOV-001 — Stub markers in canonical surfaces

<a id="gov-001-stub-markers"></a>

**Severity:** error · **Replaces:** `scripts/marker-scan.sh` · **Directive:** `CRIT-001`

The four marker strings catalogued in `governance-rules.yaml` under
`CRIT-001` — abbreviations for "to do", "fix me", "to be
determined", and "place holder" — must not appear (whole-word match)
inside the canonical surfaces:

- `specs/`
- `.claude/`
- `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`
- `docs/`

A stub marker in a contract is a confession that the contract is
incomplete; canonical surfaces are contracts. Use a tracked issue or
a real comment instead.

**Fix:** replace the marker with the actual content, or move the
discussion into a tracking issue and remove the marker.

---

## GOV-002 — Required governance files

<a id="gov-002-required-files"></a>

**Severity:** error · **Replaces:** `scripts/check-governance.sh` · **Directive:** `CRIT-002`

The five-layer scaffold's anchor files must exist at canonical
paths on every commit:

- Layer 1 navigation: `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `README.md`
- Layer 2 constitutional: `CONSTITUTION.md`, `DIRECTIVES.md`, `SECURITY.md`
- Layer 4 runtime: `.githooks/`, `.claude/settings.json`,
  `.claude/hooks/pre-tool-use.js`, `.mcp.json`
- Reference docs: `docs/MCP_POLICY.md`

The legacy governance check also emits non-blocking warnings when the
later-phase directories are still absent (`specs/deep_specs/`,
`specs/security-requirements/`, `report/`) or when `specs/deep_specs/`
exists but does not yet contain any Markdown specs. The Python port
preserves those warnings so downstream automation does not lose the
audit surface during cutover.

**Fix:** restore the missing file from the template source. Projects
generated with copier can run `copier update`; projects generated with
cookiecutter copy the missing file from the template or regenerate the
scaffold intentionally.

---

## GOV-003 — `.mcp.json` structure

<a id="gov-003-mcp-structure"></a>

**Severity:** error · **Replaces:** `scripts/check-governance.sh` (mcp section)

`.mcp.json` must parse as JSON and expose a top-level
`mcpServers` object. The MCP policy in `docs/MCP_POLICY.md`
describes the allowed servers and how to add a new one.

**Fix:** if you are intentionally clearing the MCP registry,
write `{ "mcpServers": {} }` rather than removing the key.

---

## GOV-004 — Pre-tool-use hook is registered

<a id="gov-004-pretool-hook"></a>

**Severity:** error · **Replaces:** `scripts/check-governance.sh` (hook section) · **Directive:** `CRIT-008`

The executable `.githooks/pre-commit`, `.githooks/pre-merge-commit`,
and `.githooks/pre-push` guards and their `core.hooksPath` install
wiring must exist. `.claude/hooks/pre-tool-use.js` must remain
registered as agent-facing defense in depth.

**Fix:** restore the hook file and ensure
`.claude/settings.json.hooks.PreToolUse` registers it on `Bash`.

---

## GOV-005 — Required Claude agents exist

<a id="gov-005-required-agents"></a>

**Severity:** error · **Replaces:** `scripts/check-governance.sh` (agent inventory)

The six baseline Layer-3 agents must ship in `.claude/agents/`:

- `.claude/agents/lead-software-engineer.md`
- `.claude/agents/sdlc-technical-writer.md`
- `.claude/agents/test-automator.md`
- `.claude/agents/ux-delight-specialist.md`
- `.claude/agents/security-reviewer.md`
- `.claude/agents/governance-auditor.md`

Generated projects may add more agents; they may not delete one
of these without changing the template contract.

---

## GOV-006 — Agent frontmatter is complete

<a id="gov-006-agent-frontmatter"></a>

**Severity:** error · **Replaces:** `scripts/check-governance.sh` (agent frontmatter)

Every `.claude/agents/*.md` file (other than `README.md`) must
declare YAML frontmatter with `name`, `description`, `model`,
and `memory`. The fields drive Claude Code's invocation contract;
a missing field can cause the agent to silently degrade to the
default tool set.

---

## GOV-007 — Language-specific agent present

<a id="gov-007-language-agent"></a>

**Severity:** error · **Replaces:** `scripts/check-governance.sh` (language agent)

At least one of the language-specific agents (python-pro or
typescript-pro under `.claude/agents/`) must be present. The
`primary_language` cookiecutter answer determines which one ships,
and the post-render hook prunes the other; polyglot projects keep
both.

---

## GOV-008 — Required Claude skills exist

<a id="gov-008-required-skills"></a>

**Severity:** error · **Replaces:** `scripts/check-governance.sh` (skill inventory)

The starter skills in `.claude/skills/` must be present:

- `.claude/skills/run-validate.md`
- `.claude/skills/audit-trail-tail.md`
- `.claude/skills/traceability-update.md`

Skills follow the Linux Foundation SKILL progressive-disclosure
specification (one Markdown file per skill with a `paths:` glob that
gates lazy loading).

---

## GOV-009 — Skill frontmatter and filename match

<a id="gov-009-skill-frontmatter"></a>

**Severity:** error · **Replaces:** `scripts/check-governance.sh` (skill frontmatter)

Every `.claude/skills/*.md` file must declare `name`, `description`,
and `paths` in YAML frontmatter, and the declared `name` must equal
the filename stem. Mismatches break path-based skill discovery.

---

## GOV-010 — Traceability matrix is valid JSON

<a id="gov-010-traceability-json"></a>

**Severity:** error · **Replaces:** `scripts/check-traceability.sh` (json well-formedness)

When `specs/traceability.json` is present (Phase 8 onwards) it
must parse as JSON. If `specs/traceability.schema.json` is present and
`ajv` is available, the matrix must also conform to that schema.
Earlier phases skip this check.

---

## GOV-011 — Traceability mappings resolve

<a id="gov-011-traceability-resolve"></a>

**Severity:** error · **Replaces:** `scripts/check-traceability.sh` (per-criterion checks)

Every criterion in `specs/traceability.json` must declare
`source` and `tests` globs that match real files, and any
`evidence` paths must exist. This is what proves the
traceability matrix is not stale.

---

## GOV-012 — Documentation references resolve

<a id="gov-012-doc-drift"></a>

**Severity:** warning · **Replaces:** `scripts/check-doc-drift.sh`

Every backtick-wrapped path in `docs/` and `specs/` markdown
must resolve to a file that exists on disk. The check ignores
absolute paths and URLs. Reported as warnings so renames can
land in stages; promote to error via `--warnings-as-errors`.

---

## See also

- `DIRECTIVES.md` — full directive register (`CRIT-NNN`, `IMP-NNN`,
  `REC-NNN`) with rationale and enforcement.
- `governance-rules.yaml` — machine-readable directive registry
  consumed by `scripts/query-governance.sh`.
- `scripts/governance_review/README.md` — install and usage notes
  for the validator itself.
