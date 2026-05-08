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
| --- | --- | --- |
| Source code on the default branch | Integrity-critical | High |
| Governance contracts (`CONSTITUTION.md`, `DIRECTIVES.md`, `SECURITY.md`) | Authority | Highest |
| Layer 4 hooks (`.claude/hooks/*.js`) | Enforcement | Highest |
| Layer 3 agent and command definitions (`.claude/agents/`, `.claude/commands/`) | Behavior | High |
| Evidence trail (`report/`) | Forensic | High (append-only per `IMP-001`) |
| Secrets in operator environment | Confidentiality | High |

{% if cookiecutter.include_sbom == 'yes' %}
A generated SBOM artifact (`sbom/`) is also a project asset on this
configuration — supply-chain audit class, medium trust.
{% endif %}

### Trust boundaries

1. **Operator ↔ agent.** The operator's prompt is trusted; the
   agent's reasoning trace is not.
2. **Agent ↔ tool.** Tool invocations are subject to
  `.claude/hooks/pre-tool-use.js`. Tool output is untrusted (see
  ASI-02).
3. **Project ↔ third-party code.** Third-party dependencies cross
   the boundary at install time; {% if cookiecutter.include_sbom == 'yes' %}SBOM, audit, and SHA-pinning{% else %}audit and SHA-pinning{% endif %}
   policies apply.
4. **Project ↔ MCP servers.** MCP servers are an explicit
  untrusted boundary; tool output is content, not command. Trust
  policy and vetting procedure live in `docs/MCP_POLICY.md`; the
  baseline `.mcp.json` ships read-only filesystem, read-only git,
  and token-gated GitHub entries.

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
| --- | --- | --- | --- | --- |
| ASI-01 | Agent Goal Hijack — redirected goals via injected instructions or poisoned content | `CRIT-001`, `CRIT-002`, `CRIT-008`; `P1`, `P3` | `scripts/marker-scan.sh` (canonical-surface integrity); `scripts/check-governance.sh` (required-artifact integrity); `.claude/hooks/pre-tool-use.js` (blocks protected-branch git actions, including chained and nested-shell variants) | Partial — canonical-surface and protected-branch guardrails landed; richer prompt-injection-specific controls expand in Phase 6 |
| ASI-02 | Tool Misuse and Exploitation — chained subcommands, manipulated tool outputs | `CRIT-008`, `IMP-004` | `.claude/hooks/pre-tool-use.js` (re-evaluates chained and nested-shell git commands against the protected-branch policy). Broader tool allowlists land in Phase B | Partial — protected-branch chain analysis landed; broader tool-policy enforcement lands in Phase B |
| ASI-03 | Identity and Privilege Abuse — exploiting delegated trust or inherited credentials | `CRIT-008`, `IMP-006` | `.claude/hooks/pre-tool-use.js` (protected-branch push, refspec, broad-push, and commit-producing action gates); `scripts/check-action-pins.sh` (40-char SHA pin enforcement on every workflow `uses:`) | Covered |
| ASI-04 | Agentic Supply Chain — compromised third-party agents, tools, plugins, registries | `IMP-006`; `SECURITY.md` §Scope (agent-tooling supply chain) | {% if cookiecutter.include_sbom == 'yes' %}`scripts/generate-sbom.sh` (CycloneDX); {% endif %}`.github/workflows/supply-chain.yml` (`pip-audit` for Python; `npm audit` for TypeScript); `.github/workflows/release.yml` (SLSA L3 provenance via `slsa-framework/slsa-github-generator`); `.github/workflows/ci.yml` (Snyk, Codacy jobs when enabled); Dependabot | Covered |
| ASI-05 | Runtime Environment Vulnerabilities — leaked secrets, untrusted MCP, container misconfig | `CRIT-002`; `GAP-023` (secrets), `GAP-015` (container) | `.pre-commit-config.yaml` (secret-shape detection); `.gitignore` (env-file exclusion); `.env.example` (no real values); `docs/MCP_POLICY.md` + baseline `.mcp.json` (untrusted-boundary policy + read-only baseline). Full secrets policy and container posture land in Phase 6 | Partial — secrets policy + container posture pending Phase 6 |
| ASI-06 | Poisoned Data and Malicious RAG — corrupted fixtures, prompt injection via retrieved content | `CRIT-006`; `GAP-014`, `GAP-036` | No dedicated runtime hook or CI gate yet. Current posture relies on fixture-provenance review under `CRIT-006`; ML-specific threat modeling and prompt versioning expand in Phase 6 | Partial — no mechanical verifier yet; Phase 6 expansion pending |
| ASI-07 | Insecure Inter-Agent Communication — spoofed messages between agents | (out of scope under current single-agent posture) | When the project introduces multi-agent orchestration, this row gains controls for authenticated channels and trust gates between agents. Until then the risk is structurally absent | Deferred — single-agent posture |
| ASI-08 | Cascading Failures — false signals propagated through automated pipelines | `CRIT-005`, `CRIT-008`, `IMP-001` | `.claude/hooks/pre-tool-use.js` blocks forbidden protected-branch actions before they chain into git history; `.claude/hooks/{session-start,user-prompt-submit,post-tool-use}.cjs` append to `report/audit.jsonl` so propagated failures are forensically reconstructable. A dedicated cross-pipeline verification workflow lands in Phase 6 | Partial — guardrails + audit trail landed; verification workflow pending Phase 6 |
| ASI-09 | Human-Agent Trust Exploitation — confident explanations mislead operators into approving harmful actions | `P1`, `P4`, `P8`; `CRIT-005`; `GAP-037` | No dedicated runtime hook or CI gate yet. Current posture relies on risk-class autonomy demotion in `CLAUDE.md`; the LLM output verification rubric lands later | Partial — rubric and measurable verifier pending |
| ASI-10 | Rogue Agents — misalignment, concealment, self-directed action | `CRIT-008`; `P8` | `.claude/hooks/pre-tool-use.js` as a kill switch on forbidden protected-branch actions; append-only audit trail at `report/audit.jsonl` written by the SessionStart, UserPromptSubmit, and PostToolUse hooks; risk-class autonomy ceiling in `CONSTITUTION.md §P8` | Covered |

### Reading the table

- **Covered** rows have the listed enforcement mechanisms in place
  on the default branch today.
- **Partial** rows have at least one control in place plus a named
  pending control. The named phase (e.g., `Phase 6`) corresponds
  to the matching roadmap issue and to the template repository's
  project dashboard.
- **Deferred** rows are structurally absent under current
  architecture. They become live when the named precondition is
  introduced.

### Update protocol

When a control listed here lands or changes:

1. Update the affected row's `Status` column.
2. Cross-reference the change in the template repository's SWEBOK
  gap register.
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
  and the `report/audit.jsonl` audit trail written by the
  SessionStart, UserPromptSubmit, and PostToolUse hooks.
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
{% if cookiecutter.include_sbom == 'yes' -%}
Today the SBOM (CycloneDX, generated by
`scripts/generate-sbom.sh`) is the only live container-relevant
control.
{%- else -%}
No live container-relevant control is in place today; this gap
closes in Phase 6.
{%- endif %}

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
- CERT Top 10 secure coding rules — CERT Top 10 compliance doc (planned)

---

*Authoritative since first commit. Owned jointly by the operator
and the security-reviewer subagent.*
