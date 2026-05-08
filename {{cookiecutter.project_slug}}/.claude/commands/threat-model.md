---
description: Update the threat model when attack surface changes
argument-hint: "<change description or PR number>"
allowed-tools: Read, Write, Glob, Grep
---

# threat-model

Refresh `docs/THREAT_MODEL.md` when a change introduces new attack
surface. Mandatory invocation triggers:

- New external input is added (HTTP route, file ingestion, queue
  consumer, scheduled fetch).
- New authentication or authorization path is added.
- New third-party runtime dependency is introduced.
- New ML/LLM-driven decision surface is added.
- New data classification appears (PII, PHI, financial, regulated).

## Variables

change: $ARGUMENTS

## Pre-Read

- `docs/THREAT_MODEL.md`
- `CONSTITUTION.md` (hard policy boundaries)
- `SECURITY.md`
- If present: `docs/SECURITY_PROGRAM.md` and related security
  runbooks

## Workflow

1. Identify the new attack surface introduced by `change`. Be
   specific: "new POST /api/v1/orders endpoint accepting JSON
   payloads with user-controllable `quantity` and `notes` fields."

2. For the new surface, walk the STRIDE table:
   - **Spoofing** — can identity be forged at this entry point?
   - **Tampering** — can the data be modified in transit or at
     rest?
   - **Repudiation** — is the action logged with non-repudiable
     evidence?
   - **Information disclosure** — what data is exposed if this
     surface is breached?
   - **Denial of service** — what's the cost-amplification factor
     if this surface is flooded?
   - **Elevation of privilege** — can a low-privilege actor reach
     a high-privilege capability through this surface?

3. If the change involves ML/LLM components, add the ML-specific
   row per SWEBOK v4 Ch 13 §6.3:
   - **Model poisoning** — can training data be influenced?
   - **Evasion** — can adversarial inputs flip the prediction?
   - **Prompt injection** — can untrusted content steer the agent?
   - **Membership inference** — can an attacker confirm whether
     specific data was in the training set?

4. For each non-empty cell, propose a mitigation and identify
   where it lives (code, config, runbook, design pattern).

5. Update `docs/THREAT_MODEL.md` in place. The file is a *living
   doc*, not append-only — but every substantive change must be
   accompanied by an entry in
  `docs/security/threat-model-changelog.md` (create the parent
  directory if missing) with date, change summary, reviewer.

## Forbidden

- Removing entries without justification. STRIDE rows persist;
  only their *mitigation status* changes.
- Marking a threat `mitigated` without naming the mitigation
  artifact.

## Report

Diff summary of `docs/THREAT_MODEL.md`, list of new mitigations
needing implementation, and any open threats with no proposed
mitigation (these become candidates for the next `/plan`).
