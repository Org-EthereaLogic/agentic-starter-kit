# Security Policy — {{ cookiecutter.project_name }}

> **Authority.** This document declares how to report a security
> issue against {{ cookiecutter.project_name }}, what is in scope,
> and which artifacts hold the working details. It is **tier 1**
> in the decision order for security-relevant decisions — when this
> document conflicts with `CONSTITUTION.md`, `DIRECTIVES.md`, or
> any spec on a security matter, this document wins.

---

## Reporting a vulnerability

Send a private report to **{{ cookiecutter.author_email }}**.

The maintainers may set up a dedicated security mailbox
(e.g., `security@<domain>`); when that is in place, this address
is updated. Until then, the address above is the disclosure
channel.

**What to include:**

- A description of the issue and its impact.
- A minimal reproducer or sequence of steps that triggers the
  issue.
- The affected version (commit SHA or release tag).
- Your preferred contact for follow-up.

**Response timeline:**

| Stage | Target |
|---|---|
| Acknowledgement of report | Within 5 working days |
| Initial triage and severity classification | Within 10 working days |
| Public disclosure (after fix) | Coordinated with reporter |

Working day definitions follow the maintainer's location and
working calendar; a more specific SLA lands when the project has a
dedicated security responder.

**Public reports.** Do not file a public GitHub issue describing
the vulnerability. Use the private channel above. Once a fix is
released, a public advisory is appropriate.

## Supported versions

Security fixes apply to the versions listed below. Other versions
do not receive backports.

| Version | Supported |
|---|---|
| `latest` | yes |
| `prior major` | yes — until `YYYY-MM-DD + 12 months` |
| earlier | no |

Concrete version numbers and dates land in this table after the
project's first tagged release. Until then, supported versions
default to `main`.

## Scope

This policy covers vulnerabilities affecting:

### General software issues

- Memory corruption, code injection, command injection.
- Authentication bypass, authorization bypass, privilege
  escalation.
- Information disclosure (PII, credentials, internal paths).
- Cryptographic weaknesses (broken algorithms, weak parameters).

### Agentic-specific issues

These categories are non-traditional but are explicitly in scope
for {{ cookiecutter.project_name }}. The full enumeration follows
the OWASP Top 10 for Agentic Applications 2026
(`docs/THREAT_MODEL.md §2`); the four below are the most common
classes of report:

- **Prompt injection.** Untrusted content (user input, retrieved
  documents, tool output) that steers the agent into actions
  outside its policy. The threat model documents the trust
  boundaries that prompt injection violates.
- **Hook bypass.** Any technique that allows a Bash command
  matching `.claude/hooks/pre-tool-use.js`'s forbidden patterns to
  execute. The hook's regression suite enumerates the known
  bypass classes; new bypass classes are reported through this
  channel.
- **Agent-tooling supply chain.** Dependencies of the slash
  commands, agent prompts, or build tooling that introduce
  vulnerabilities downstream into the agent's execution context.
- **Configuration tampering.** Any change to `.claude/settings.json`,
  `.claude/hooks/`, or `CONSTITUTION.md` / `DIRECTIVES.md` /
  `SECURITY.md` that bypasses the documented amendment process
  is in scope as a security issue.

### Out of scope

- Denial of service against developer tooling (`make`, local
  Python interpreter, CI runner) when triggered by the developer's
  own input.
- Vulnerabilities in third-party services this project integrates
  with (Codacy, Snyk, Codecov, Databricks). Report those to the
  service vendor.
- Theoretical attacks against language runtimes (CPython, V8) that
  do not have a working reproducer in this project's context.

## Working artifacts

As later layers land, the full security program is documented
across these files. This SECURITY.md is the *entry point*; until
those artifacts exist, treat the table below as the planned depth
map.

| Artifact | Purpose |
|---|---|
| `docs/THREAT_MODEL.md` | OWASP Agentic Top 10 (2026) coverage matrix (§2 — every ASI mapped to directives + enforcement); STRIDE table; ML-specific section (model poisoning, evasion, prompt injection); container/cloud security |
| `docs/SECURITY_PROGRAM.md` | DevSecOps lifecycle integration: requirements, design, build, run |
| `docs/cert-top-10-compliance.md` | Self-audit map against the CERT Top 10 secure-coding rules |
| `docs/sbom-policy.md` | CycloneDX SBOM generation and review policy |
| `docs/security/vulnerability-management.md` | CVE / CWE / CAPEC / CVSS triage process |
| `docs/security/container-security.md` | Container and cloud security posture |
| `docs/security/secrets-policy.md` | Secrets-handling rules |
| `specs/security-requirements/` | Per-feature security requirements with acceptance criteria |

## Disclosure history

Acknowledged disclosures are recorded in
`docs/security/disclosure-history.md` once that file exists
(created when the first disclosure lands).

## Amendment

Substantive changes to this policy — disclosure address,
supported-versions matrix, scope additions or removals — require
an ADR under `specs/deep_specs/`. Editorial corrections do not.

---

*This policy applies from first commit. Amended via ADR.*
