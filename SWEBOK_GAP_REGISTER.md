# SWEBOK v4 Gap Register

> **Purpose:** explicit machine-readable inventory of every gap
> identified in the SWEBOK v4 analysis (pasted in this conversation's
> context), each mapped to one or more deliverable files in the
> template. This file is the source of truth for "are we done?"
>
> **Status convention:**
> - `planned` — design committed, file not yet authored
> - `in_progress` — file exists but is incomplete or stub
> - `landed` — file complete and verified
> - `needs_fix` — file exists but does not satisfy the gap
>
> **Closing criterion:** every row reaches `landed` and the verifying
> CI gate (where applicable) is green.

---

## Section A — Software Engineering Operations (SWEBOK v4 Ch 6)

Anchored to ISO/IEC/IEEE 32675:2022 (DevOps).

| ID | SWEBOK Ref | Gap | Deliverable | CI Verifier | Status |
|---|---|---|---|---|---|
| GAP-001 | §2.1.1 | Operations Plan as a living doc — capacity, availability, backup, DR, environments | `docs/OPERATIONS.md` (full content, not skeleton) | `make governance-check` | planned |
| GAP-002 | §2.5 | Backup & recovery cadence, restore-test record | `docs/OPERATIONS.md §1.3` + `docs/operations/backup-restore-runbook.md` | n/a | planned |
| GAP-003 | §2.6 | Disaster recovery plan + rehearsal cadence | `docs/OPERATIONS.md §1.4` | n/a | planned |
| GAP-004 | §3.2 | Release strategies — canary, blue-green, rolling — explicitly chosen | `docs/OPERATIONS.md §2.1` + `docs/operations/release-strategy.md` | n/a | planned |
| GAP-005 | §3.2 | Feature flags / toggles strategy | `docs/operations/feature-flags-policy.md` | n/a | planned |
| GAP-006 | §3.3 | Rollback procedure with data-migration contract | `docs/operations/rollback-runbook.md` | n/a | planned |
| GAP-007 | §4.3, §6.4 | Monitoring and Telemetry strategy with named KPIs (production telemetry, V&V results, end-user activity, dependency status, unauthorized config changes, security signals) | `docs/monitoring-strategy.md` | n/a | planned |
| GAP-008 | §5.2 (cites IEEE 2675) | Continuous risk management — automated risk monitoring with thresholds | `docs/operations/risk-management.md` | n/a | planned |
| GAP-009 | Ch 6 anchor | ISO/IEC/IEEE 32675:2022 referenced as the canonical DevOps standard | `docs/STANDARDS.md` (new) + `docs/tooling-versions.md` | n/a | planned |
| GAP-010 | §3.4 | Environment matrix (local / staging / production) with access controls | `docs/OPERATIONS.md §1.5` | n/a | planned |
| GAP-011 | §4.1 | Incident management with severity classification + on-call (or solo-operator equivalent) | `docs/operations/incident-runbook.md` | n/a | planned |
| GAP-012 | §4.2 | Change management — change classes + approval thresholds | `docs/OPERATIONS.md §3.2` | n/a | planned |

---

## Section B — Software Security (SWEBOK v4 Ch 13) and DevSecOps

| ID | SWEBOK Ref | Gap | Deliverable | CI Verifier | Status |
|---|---|---|---|---|---|
| GAP-013 | §3.1 | Formal STRIDE threat model with explicit assets and trust boundaries | `docs/THREAT_MODEL.md` (full content) | n/a | planned |
| GAP-014 | §6.3 | ML-specific threats — model poisoning (training data integrity), evasion (adversarial inputs), prompt injection — promoted to dedicated section | `docs/THREAT_MODEL.md §6` | n/a | planned |
| GAP-015 | §6.1 | Container & cloud security posture | `docs/THREAT_MODEL.md §7` + `docs/security/container-security.md` | n/a | planned |
| GAP-016 | §4.6 | Vulnerability management covering CVE + CWE + CAPEC + CVSS quarterly review | `docs/security/vulnerability-management.md` | n/a | planned |
| GAP-017 | §3.1, §3.6 | DevSecOps lifecycle integration — security in requirements, design, build, run | `docs/SECURITY_PROGRAM.md` (new) | n/a | planned |
| GAP-018 | §3.1 | `security-requirements/` folder pattern with template | `specs/security-requirements/README.md` + `specs/security-requirements/sec-req-template.md` | `make governance-check` | planned |
| GAP-019 | §3.4 | Security design patterns referenced from design docs | `specs/deep_specs/design-template.md` (security-patterns section) | n/a | planned |
| GAP-020 | §6.4 | Security telemetry KPIs surfaced in monitoring | `docs/monitoring-strategy.md §4` | n/a | planned |
| GAP-021 | §4.4 | CERT Top 10 self-audit map | `docs/cert-top-10-compliance.md` | n/a | planned |
| GAP-022 | §1, §4.6 | SBOM policy + generation tooling (CycloneDX or SPDX) | `docs/sbom-policy.md` + `scripts/generate-sbom.sh` + CI job | `.github/workflows/ci.yml` (sbom job) | planned |
| GAP-023 | §3.2 | Secrets-handling policy (template-level, not project-specific) | `docs/security/secrets-policy.md` | `make marker-scan` (extended) | planned |
| GAP-024 | §1.1 | Asset inventory and data classification | `docs/THREAT_MODEL.md §2` | n/a | planned |
| GAP-025 | §3.5 | Security testing levels (SAST + DAST + dependency + secret scan) | `docs/SECURITY_PROGRAM.md §4` + CI jobs | `.github/workflows/ci.yml` | planned |

---

## Section C — Software Architecture (SWEBOK v4 Ch 2)

Anchored to IEEE 42010.

| ID | SWEBOK Ref | Gap | Deliverable | CI Verifier | Status |
|---|---|---|---|---|---|
| GAP-026 | Ch 2 anchor | IEEE 42010 referenced as the canonical architecture-description standard | `docs/STANDARDS.md` + `docs/ARCHITECTURE.md` header | n/a | planned |
| GAP-027 | §2.1 | Architecture description with **named views**: logical, process, deployment, data | `docs/ARCHITECTURE.md §3` | n/a | planned |
| GAP-028 | §1.2 | Stakeholders & concerns table | `docs/ARCHITECTURE.md §2` | n/a | planned |
| GAP-029 | §2.2 | Architecturally-significant decisions cross-referenced to ADRs | `docs/ARCHITECTURE.md §4` + `specs/deep_specs/adr-0001-governance-foundation.md` (seed example) | n/a | planned |
| GAP-030 | §3 | Architectural patterns selection rationale | `docs/ARCHITECTURE.md §5` | n/a | planned |

---

## Section D — Living Documentation & Traceability

| ID | SWEBOK Ref | Gap | Deliverable | CI Verifier | Status |
|---|---|---|---|---|---|
| GAP-031 | §1.7.3 (Requirements KA) | Machine-readable traceability matrix | `specs/traceability.json` + `specs/traceability.schema.json` | `make check-traceability` | planned |
| GAP-032 | §1.7.3 | Traceability validator script | `scripts/check-traceability.sh` | `make validate` (new gate) | landed |
| GAP-033 | §1.7.3, §6 (Operations) | Doc-code drift detector — verifies every file path mentioned in specs/docs exists in repo | `scripts/check-doc-drift.sh` + CI job | `make validate` (new gate) | landed |
| GAP-034 | §1.7.3 | Documentation ownership matrix (RACI) per living doc | `docs/documentation-ownership.md` | n/a | planned |
| GAP-035 | n/a (operational) | `/sync` command runs after every PR merge to refresh local state and detect drift | `.claude/commands/sync.md` (full text in `COMMAND_AND_AGENT_SPECS.md`) | `/audit` step 10 | planned |

---

## Section E — AI-Assisted Development (Construction §4.16–4.17)

| ID | SWEBOK Ref | Gap | Deliverable | CI Verifier | Status |
|---|---|---|---|---|---|
| GAP-036 | §4.16 | Prompt versioning policy — slash-command and agent-prompt changes are contract changes | `docs/prompt-versioning-policy.md` | n/a | planned |
| GAP-037 | §4.17 | LLM output verification rubric — explicit checks for fabricated metrics, hallucinated paths, unsupported external state, missing citations | `docs/llm-output-verification-rubric.md` | n/a | planned |
| GAP-038 | §4.17, P8 | Risk-class human-in-the-loop policy — when does autonomy demote to ask-mode | `docs/llm-output-verification-rubric.md §3` + `CONSTITUTION.md P8` (extended) | n/a | planned |
| GAP-039 | §5.1 | IDE / cloud-IDE integration notes — Claude Code, Cursor, Copilot configuration | `docs/agent-runtimes.md` | n/a | planned |

---

## Section F — Standards Register

| ID | Standard | Where Anchored | Status |
|---|---|---|---|
| GAP-040 | ISO/IEC/IEEE 32675:2022 (DevOps) | `docs/STANDARDS.md`, `docs/OPERATIONS.md` header | planned |
| GAP-041 | IEEE 42010 (Architecture description) | `docs/STANDARDS.md`, `docs/ARCHITECTURE.md` header | planned |
| GAP-042 | AGENTS.md (Linux Foundation Agentic AI Foundation) | `docs/STANDARDS.md`, `AGENTS.md` itself | planned |
| GAP-043 | IEEE 2675 (Continuous risk for DevOps) | `docs/STANDARDS.md`, `docs/operations/risk-management.md` | planned |
| GAP-044 | CycloneDX or SPDX (SBOM) | `docs/sbom-policy.md`, `docs/STANDARDS.md` | planned |
| GAP-045 | CERT Top 10 (Secure coding) | `docs/cert-top-10-compliance.md`, `docs/STANDARDS.md` | planned |
| GAP-046 | SWEBOK v4.0a (overall reference) | `docs/STANDARDS.md` | planned |

---

## Section G — Cross-cutting CI/Workflow Gates

These are the new CI gates needed to make the above mechanically
enforced rather than aspirational.

| ID | Gate | Trigger | Failure Behavior | Status |
|---|---|---|---|---|
| GAP-047 | `marker-scan` | every PR | block merge | landed |
| GAP-048 | `governance-check` (extended to verify required folders too: `docs/`, `specs/deep_specs/`, `specs/security-requirements/`, `report/`) | every PR | block merge | landed |
| GAP-049 | `check-traceability` | every PR touching `specs/` or `src/` | block merge | landed |
| GAP-050 | `check-doc-drift` | every PR touching `docs/` or `specs/` | warn (not block) initially, harden after stabilization | landed |
| GAP-051 | `sbom-generate` | every push to default branch | upload artifact | landed (conditional on `include_sbom=yes`) |
| GAP-052 | `secret-scan` | every PR | block merge | landed |
| GAP-053 | `dast` (placeholder — language and stack-dependent) | nightly on main | warn | planned |

---

## Section H — Original "core" deliverables (carried forward from prior turns)

These were already designed in prior turns but are listed here for
completeness so the agent has a single inventory to work from.

| ID | Deliverable | Layer | Status |
|---|---|---|---|
| CORE-001 | `cookiecutter.json` | infra | landed |
| CORE-002 | `hooks/post_gen_project.py` | infra | landed |
| CORE-003 | `README.md` (top-level) | infra | landed |
| CORE-004 | `METHODOLOGY.md` (essay) | infra | landed |
| CORE-005 | `LICENSE` (top-level) | infra | landed |
| CORE-006 | `{{cookiecutter.project_slug}}/CLAUDE.md` | L1 | landed |
| CORE-007 | `{{cookiecutter.project_slug}}/AGENTS.md` | L1 | landed |
| CORE-008 | `{{cookiecutter.project_slug}}/GEMINI.md` | L1 | landed |
| CORE-009 | `{{cookiecutter.project_slug}}/CONSTITUTION.md` | L2 | landed |
| CORE-010 | `{{cookiecutter.project_slug}}/DIRECTIVES.md` | L2 | landed |
| CORE-011 | `{{cookiecutter.project_slug}}/SECURITY.md` | L2 | landed |
| CORE-012 | `.claude/settings.json` | L4 | landed |
| CORE-013 | `.claude/hooks/pre-tool-use.js` | L4 | landed |
| CORE-014 | `.claude/hooks/README.md` | L4 | landed |
| CORE-015 | `tests/test_pre_tool_use_hook.py` | L4 | landed |
| CORE-016 | `tests/test_pre_tool_use_hook.js` (TS path) | L4 | landed |
| CORE-017 | `.github/workflows/ci.yml` | L5 | landed |
| CORE-018 | `Makefile` | L5 | landed |
| CORE-019 | `scripts/marker-scan.sh` | L5 | landed |
| CORE-020 | `scripts/check-governance.sh` | L5 | landed |
| CORE-021 | `pyproject.toml` (Python path) | L5 | planned |
| CORE-022 | `package.json` (TS path) | L5 | planned |
| CORE-023 | `.gitignore` | infra | planned |
| CORE-024 | `.editorconfig` | infra | planned |
| CORE-025 | `.env.example` | infra | planned |
| CORE-026 | `.pre-commit-config.yaml` | infra | planned |
| CORE-027 | `.codacy.yml` | infra | planned (conditional) |
| CORE-028 | `codecov.yaml` | infra | planned (conditional) |
| CORE-029 | `.snyk` | infra | planned (conditional) |
| CORE-030 | `.github/dependabot.yml` | infra | planned |
| CORE-031 | `.github/PULL_REQUEST_TEMPLATE.md` | infra | planned |
| CORE-032 | `CONTRIBUTING.md` | infra | planned |
| CORE-033 | `LICENSE` (templated) | infra | planned |
| CORE-034 | `docs/PRD.md` | infra | planned |
| CORE-035 | `docs/tooling-versions.md` | infra | planned |
| CORE-036 | `specs/README.md` | infra | planned |
| CORE-037 | `specs/deep_specs/README.md` | infra | planned |
| CORE-038 | `specs/deep_specs/adr-template.md` | infra | planned |
| CORE-039 | `specs/deep_specs/rfc-template.md` | infra | planned |
| CORE-040 | `report/README.md` | infra | planned |

---

## Section I — Slash commands (Layer 3)

The full canonical text for new commands lives in
`COMMAND_AND_AGENT_SPECS.md`. Existing commands may be ported
(parameterized) from `/Users/etherealogic-2/Dev/govforge/.claude/commands/`.

| ID | Command | Source | Status |
|---|---|---|---|
| CMD-001 | `/prime` | port from govforge | planned |
| CMD-002 | `/start` | port from govforge | planned |
| CMD-003 | `/status` | port from govforge | planned |
| CMD-004 | `/plan` | port from govforge | planned |
| CMD-005 | `/implement` | port from govforge | planned |
| CMD-006 | `/test` | port from govforge | planned |
| CMD-007 | `/review` | port from govforge | planned |
| CMD-008 | `/verify` | port from govforge | planned |
| CMD-009 | `/audit` | port from govforge (extend with traceability + sync recency check) | planned |
| CMD-010 | `/commit` | port from govforge | planned |
| CMD-011 | `/pull-request` | port from govforge | planned |
| CMD-012 | `/session-log` | port from govforge | planned |
| CMD-013 | `/sync` | NEW (full text in COMMAND_AND_AGENT_SPECS.md) | planned |
| CMD-014 | `/spec-bump` | port from govforge | planned |
| CMD-015 | `/threat-model` | NEW — runs the STRIDE template, hooks ML extensions | planned |
| CMD-016 | `/check-traceability` | NEW — wrapper around `scripts/check-traceability.sh` for ad-hoc invocation | planned |

---

## Section J — Agents (Layer 3)

| ID | Agent | Source | Status |
|---|---|---|---|
| AGENT-001 | `lead-software-engineer` | port from govforge | planned |
| AGENT-002 | `sdlc-technical-writer` | port from govforge | planned |
| AGENT-003 | `test-automator` | port from govforge | planned |
| AGENT-004 | `ux-delight-specialist` | port from govforge | planned |
| AGENT-005 | `python-pro` | port from govforge (Python path) | planned (conditional) |
| AGENT-006 | `typescript-pro` | NEW — TypeScript counterpart | planned (conditional) |
| AGENT-007 | `security-reviewer` | NEW — owns threat-model maintenance, SBOM review, vulnerability triage | planned |

---

## Done summary

When this register reads `landed` for every row except those marked
`planned (conditional on …)` (which depend on cookiecutter options),
the SWEBOK v4 bridge is closed and the template is shippable.
