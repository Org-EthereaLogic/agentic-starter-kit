# Threat Model — {{ cookiecutter.project_name }}

> **Authority.** This document is the working threat model for
> {{ cookiecutter.project_name }}. It enumerates assets, trust
> boundaries, and risks; for each risk it names the directive that
> codifies the rule and the runtime hook or CI gate that enforces
> it. The model derives from `SECURITY.md` (tier 1 authority on
> security matters per `CONSTITUTION.md §3`) and `DIRECTIVES.md`.
>
> **Anchored to.** SWEBOK v4.0a Ch 13 (Software Security);
> ISO/IEC/IEEE 32675:2022 (DevOps); the OWASP Top 10 for Agentic
> Applications 2026.
>
> **Scope.** The agent runtime, the template's governance plane,
> and the project's own production code. External services
> (Codacy, Snyk, Codecov, Databricks) are referenced where the
> integration creates trust dependencies but their internal threats
> are owned by the vendor.

---

## §1 — Assets and trust boundaries

The threat model treats the following as primary assets and
boundaries. The full asset inventory and data classification land
in Phase 6 of the build plan; this section sketches the surface so
§2's mappings have referents.

### Primary assets

| Asset | Type | Trust class |
|---|---|---|
| Source code on the default branch | Integrity-critical | High |
| Governance contracts (`CONSTITUTION.md`, `DIRECTIVES.md`, `SECURITY.md`) | Authority | Highest |
| Layer 4 hooks (`.claude/hooks/*.js`) | Enforcement | Highest |
| Layer 3 agent and command definitions (`.claude/agents/`, `.claude/commands/`) | Behavior | High |
| Evidence trail (`report/`) | Forensic | High (append-only per `IMP-001`) |
| Secrets in operator environment | Confidentiality | High |
| Generated SBOM artifacts (`sbom/`) | Supply-chain audit | Medium |

### Trust boundaries

1. **Operator ↔ agent.** The operator's prompt is trusted; the
   agent's reasoning trace is not.
2. **Agent ↔ tool.** Tool invocations are subject to
   `pre-tool-use.js`. Tool output is untrusted (see ASI-02).
3. **Project ↔ third-party code.** Third-party dependencies cross
   the boundary at install time; SBOM, audit, and SHA-pinning
   policies apply.
4. **Project ↔ MCP servers.** When `.mcp.json` is shipped (Phase A4
   of the roadmap), MCP servers are an explicit untrusted boundary
   per `docs/MCP_POLICY.md`.

The full boundary diagram lands in Phase 6.

---

## §2 — OWASP Agentic Top 10 (2026) coverage

Source:
[OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/).

Each row maps an Agentic Security Issue (`ASI-NN`) to:

- **Directives** — the directive IDs (and constitutional
  principles) that codify the rule;
- **Enforcement** — the runtime hook (Layer 4) or CI gate (Layer 5)
  that mechanically prevents or detects the failure;
- **Status** — `Covered` if all controls are landed;
  `Partial` if some controls are scheduled in a later phase (the
  phase is named); `Deferred` if the risk is out of scope under
  current template posture.

| ASI | Risk | Directives | Enforcement | Status |
|---|---|---|---|---|
| ASI-01 | Agent Goal Hijack — redirected goals via injected instructions or poisoned content | `CRIT-001`, `CRIT-002`, `CRIT-007`, `CRIT-008`; `P1`, `P3` | `.claude/hooks/pre-tool-use.js` (forbidden-action gate); `scripts/marker-scan.sh` (canonical-surface integrity); `scripts/check-governance.sh` (required-artifact integrity) | Covered |
| ASI-02 | Tool Misuse and Exploitation — chained subcommands, manipulated tool outputs | `CRIT-008`, `IMP-004` | `.claude/hooks/pre-tool-use.js` (detects `&&`, `;`, `\|\|`, backticks, `$()` chains containing banned actions); curated `allowed-tools` per slash command | Covered |
| ASI-03 | Identity and Privilege Abuse — exploiting delegated trust or inherited credentials | `CRIT-007`, `CRIT-008`, `IMP-006` | `.claude/hooks/pre-tool-use.js` (protected-branch push and refspec push gates); `scripts/check-action-pins.sh` (SHA-pinned action enforcement) | Covered |
| ASI-04 | Agentic Supply Chain — compromised third-party agents, tools, plugins, registries | `IMP-006`; `SECURITY.md` §Scope (agent-tooling supply chain) | `scripts/generate-sbom.sh` (CycloneDX); `.github/workflows/ci.yml` (Snyk, Codacy jobs when enabled); Dependabot. SLSA L3 provenance and `pip-audit`/`npm audit` land in Phase A3 of the roadmap | Partial — SLSA provenance + language-native audit pending Phase A3 |
| ASI-05 | Runtime Environment Vulnerabilities — leaked secrets, untrusted MCP, container misconfig | `CRIT-002`; `GAP-023` (secrets), `GAP-015` (container) | `.pre-commit-config.yaml` (secret-shape detection); `.gitignore` (env-file exclusion); `.env.example` (no real values). MCP policy lands in Phase A4; full secrets policy and container posture in Phase 6 | Partial — MCP policy + secrets policy + container posture pending |
| ASI-06 | Poisoned Data and Malicious RAG — corrupted fixtures, prompt injection via retrieved content | `CRIT-006`; `GAP-014`, `GAP-036` | `CRIT-006` fixture-source-or-seed rule; ML-specific threat section (this file §4, expanded in Phase 6); prompt versioning policy `docs/prompt-versioning-policy.md` (planned, `GAP-036`) | Partial — ML §4 expansion + prompt-versioning policy pending |
| ASI-07 | Insecure Inter-Agent Communication — spoofed messages between agents | (out of scope under current single-agent posture) | When the project introduces multi-agent orchestration, this row gains controls for authenticated channels and trust gates between agents. Until then the risk is structurally absent | Deferred — single-agent posture |
| ASI-08 | Cascading Failures — false signals propagated through automated pipelines | `CRIT-005`, `CRIT-008`, `IMP-001` | `.claude/hooks/pre-tool-use.js` (breaks the chain at the first forbidden action); `/verify` dual-evidence rule prevents agents from chain-claiming success; append-only `report/` (`IMP-001`) preserves forensic state | Covered |
| ASI-09 | Human-Agent Trust Exploitation — confident explanations mislead operators into approving harmful actions | `P1`, `P4`, `P8`; `CRIT-005`; `GAP-037` | Risk-class autonomy demotion in `CLAUDE.md` (high-risk → ask-mode); `/verify` dual-evidence; LLM output verification rubric `docs/llm-output-verification-rubric.md` (planned, `GAP-037`) | Partial — verification rubric pending |
| ASI-10 | Rogue Agents — misalignment, concealment, self-directed action | `CRIT-007`, `CRIT-008`; `P8` | `.claude/hooks/pre-tool-use.js` as a kill switch on forbidden actions; `report/audit.jsonl` reconstruction trail (lands in Phase A5 of the roadmap); risk-class autonomy ceiling in `CONSTITUTION.md §P8` | Partial — audit trail pending Phase A5 |

### Reading the table

- **Covered** rows have the listed enforcement mechanisms in place
  on the default branch today.
- **Partial** rows have at least one control in place plus a named
  pending control. The named phase (e.g., `Phase A3`) corresponds
  to the roadmap phase in `docs/PROJECT_DASHBOARD.md` (template
  repo) and to a tracking issue in the template repo.
- **Deferred** rows are structurally absent under current
  architecture. They become live when the named precondition is
  introduced.

### Update protocol

When a control listed here lands or changes:

1. Update the affected row's `Status` column.
2. Cross-reference the change in `docs/SWEBOK_GAP_REGISTER.md`.
3. If the change is decision-content (a new mitigation strategy,
   not a wording fix), add an ADR under
   `specs/deep_specs/ADR/`.

---

## §3 — STRIDE table (full table lands in Phase 6)

The classical STRIDE classification covers the non-agentic risks
that survive in any production system. The full STRIDE table —
spoofing, tampering, repudiation, information disclosure, denial
of service, elevation of privilege — is authored as part of Phase
6 of the build plan. This section reserves the heading and points
the reader at the parts the OWASP ASI table already addresses.

Cross-references already in §2:

- **Tampering** — partially covered by `CRIT-001`, `CRIT-002`,
  `CRIT-008` (governance contract integrity).
- **Repudiation** — covered by append-only `report/` (`IMP-001`)
  and the audit trail under construction in Phase A5.
- **Elevation of privilege** — covered by `CRIT-007`, `CRIT-008`
  (protected-branch hook).

---

## §4 — ML-specific threats (full section lands in Phase 6)

The ML-specific axes — model poisoning (training-data integrity),
evasion (adversarial inputs), prompt injection — are partially
addressed in §2 (ASI-01, ASI-06). The full section, including
data-classification rules for training data and a model-supply-
chain section, lands in Phase 6 of the build plan and closes
`GAP-014`.

---

## §5 — Container and cloud security (full section lands in Phase 6)

The container and cloud security posture — image provenance,
runtime configuration, secrets at rest, network egress — is
authored in Phase 6 of the build plan and closes `GAP-015`.
Today the SBOM (CycloneDX, generated by
`scripts/generate-sbom.sh`) is the only live container-relevant
control.

---

## §6 — Disclosure and amendment

Vulnerabilities are reported through the channel in `SECURITY.md`.
Substantive changes to this threat model (changes to a Status
column from `Partial` to `Deferred`, removal of a control, or
addition of a new asset class) require an ADR under
`specs/deep_specs/ADR/`. Editorial corrections do not.

---

## References

- OWASP Top 10 for Agentic Applications 2026 — <https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/>
- SWEBOK Guide v4.0a (September 2025) — Chapter 13, Software Security
- ISO/IEC/IEEE 32675:2022 — DevOps and continuous risk management
- IEEE 2675 — Continuous risk for DevOps
- CERT Top 10 secure coding rules — `docs/cert-top-10-compliance.md` (planned)

---

*Authoritative since first commit. Owned jointly by the operator
and the security-reviewer subagent.*
