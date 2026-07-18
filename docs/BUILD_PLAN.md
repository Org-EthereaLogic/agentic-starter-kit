# Build Plan — Agentic Starter Kit

> **Audience:** the IDE agent authoring this template's contents.
> **Read first:** `BRIEFING.md` and `SWEBOK_GAP_REGISTER.md`.
> **Authoring order matters:** files in earlier phases are referenced
> by later phases. Author phase-by-phase. Run the gate at the end of
> each phase before moving on.

---

## Phase 0 — Top-level template scaffolding

| File | Notes |
|---|---|
| `cookiecutter.json` | Variable schema per BRIEFING §7. Pin `_copy_without_render` for paths containing `{{ }}` literals if needed. |
| `hooks/post_gen_project.py` | Conditionally remove files based on cookiecutter answers (e.g., remove `.codacy.yml` when `include_codacy == "no"`; remove `pyproject.toml` when `primary_language == "typescript"`; remove `package.json` when `primary_language == "python"`). |
| `README.md` (top-level) | How to use the template. Bring-up via `pipx install cookiecutter` then `cookiecutter gh:OrgName/agentic-starter-kit`. Lists prerequisites and the cookiecutter variable surface. |
| `METHODOLOGY.md` | The standalone essay. ~3000–5000 words. Walks through all five layers, the SWEBOK v4 bridge, and a Day-1/Day-2/Day-3 bring-up plan. Designed to be useful even without the template. |
| `LICENSE` (top-level) | MIT license for the template repo itself. Distinct from the templated `LICENSE` shipped to instantiated projects. |
| `.gitignore` (top-level) | Python + node + editor + cookiecutter test output (`/tmp/cookiecutter-test/`). |

**Phase 0 gate:**

```bash
pipx run cookiecutter . --no-input -o /tmp/cookiecutter-test/
ls /tmp/cookiecutter-test/<default-slug>/
# expect: a directory with at least the .git skeleton placeholder (empty for now)
```

Failure here means cookiecutter syntax errors. Fix before proceeding.

---

## Phase 1 — Layer 2: Constitutional foundation

| File | Notes |
|---|---|
| `{{cookiecutter.project_slug}}/CONSTITUTION.md` | The 8 principles (P1–P8) per BRIEFING §3. Six-tier decision order. |
| `{{cookiecutter.project_slug}}/DIRECTIVES.md` | The 18 directives (8 Critical, 6 Important, 4 Recommended) per BRIEFING §4. Each directive has: ID, statement, rationale, enforcement mechanism. |
| `{{cookiecutter.project_slug}}/SECURITY.md` | Disclosure process (`security@<author_email_domain>`), supported versions placeholder, agentic-specific scope (prompt injection, hook bypass, agent-tooling supply chain), and explicit cross-reference to the threat model and CERT compliance docs. |

**Phase 1 gate:** all three files exist, contain no stub markers, and
the directive IDs are unique and sequential.

---

## Phase 2 — Layer 1: Navigation

| File | Notes |
|---|---|
| `{{cookiecutter.project_slug}}/CLAUDE.md` | Tells Claude Code where to read first. Lists CONSTITUTION → DIRECTIVES → AGENTS → relevant spec → relevant module README in that order. References the autonomy-demotion rules (P8). |
| `{{cookiecutter.project_slug}}/AGENTS.md` | The Linux Foundation AGENTS.md format. Required pre-read protocol, decision order, communication style, the Plan/Act/Verify/Report loop. |
| `{{cookiecutter.project_slug}}/GEMINI.md` | Symlink-equivalent for Gemini CLI. Same content as AGENTS.md or a thin pointer. |

**Phase 2 gate:** files exist; CLAUDE.md and AGENTS.md cite the
correct directive IDs from Phase 1.

---

## Phase 3 — Layer 4: Runtime enforcement

| File | Notes |
|---|---|
| `{{cookiecutter.project_slug}}/.githooks/{pre-commit,pre-merge-commit,pre-push}` | Primary CRIT-008 boundary. POSIX `sh`; installed through `core.hooksPath`; resolves branch and destination refs after shell processing. Document the client-side and replay-operation limitations. |
| `{{cookiecutter.project_slug}}/.claude/hooks/pre-tool-use.js` | Agent-facing defense in depth. Parameterize the protected branch list and block recognized protected-branch operations early without claiming to be the primary guarantee. |
| `{{cookiecutter.project_slug}}/.claude/hooks/README.md` | Explains what the hook does, how to test it, and the rule that any new bypass class needs a test added before the bypass is fixed. |
| `{{cookiecutter.project_slug}}/.githooks/README.md` | Explains installation, pre-commit-framework chaining, the coverage map, and the honest boundary. |
| `{{cookiecutter.project_slug}}/.claude/settings.json` | Registers the hook on `PreToolUse:Bash`. JSON, not JSON-with-comments. |
| `{{cookiecutter.project_slug}}/tests/test_pre_tool_use_hook.py` | Python test suite (Python path). One test per payload class. Uses `subprocess.run` to invoke `node .claude/hooks/pre-tool-use.js` with stdin per Claude Code hook protocol. Asserts exit code and stderr. |
| `{{cookiecutter.project_slug}}/tests/test_pre_tool_use_hook.js` | TypeScript-path equivalent using node:test (`node --test`). Same coverage as Python. |
| `{{cookiecutter.project_slug}}/tests/test_git_hooks.sh` | Language-neutral real-git regression suite for the primary boundary. |

**Phase 3 gate:**

```bash
cd {{cookiecutter.project_slug}}
git init && make hooks-install && make hooks-test
# expect: git-layer and agent-layer suites pass
```

For both Python and TS path, the test suite runs with at least
6 distinct payload classes covered.

---

## Phase 4 — Layer 5: External validation

| File | Notes |
|---|---|
| `{{cookiecutter.project_slug}}/Makefile` | Targets: `help`, `sync`, `marker-scan`, `governance-check`, `check-traceability`, `check-doc-drift`, `lint`, `typecheck`, `test`, `coverage`, `validate`, `hooks-test`, `codacy-local`, `snyk-local`, `sbom`, `clean`. `validate` aggregates the gates per CRIT-001/002/008 plus traceability + drift. Conditional language blocks via Jinja2 (`{% if cookiecutter.primary_language in ("python", "polyglot") %}…{% endif %}`). |
| `{{cookiecutter.project_slug}}/scripts/marker-scan.sh` | Bash, `set -euo pipefail`. Concatenated regex (so script doesn't match itself). Surfaces canonical: `specs/`, `.claude/`, `CLAUDE.md`, `AGENTS.md`, `docs/`. Uses `rg` with `grep` fallback. |
| `{{cookiecutter.project_slug}}/scripts/check-governance.sh` | Bash. Verifies required files and folders, the executable `.githooks` guards and `core.hooksPath` wiring, plus the agent-layer hook and its `.claude/settings.json` registration. |
| `{{cookiecutter.project_slug}}/scripts/check-traceability.sh` | Bash + jq. Reads `specs/traceability.json`. For each acceptance criterion: confirm referenced source globs match at least one file; confirm referenced test globs match at least one file; confirm referenced evidence artifact exists. Surface unmapped criteria and orphaned tests. |
| `{{cookiecutter.project_slug}}/scripts/check-doc-drift.sh` | Bash. Greps every relative path-like token in `docs/*.md` and `specs/**/*.md` and verifies it exists. Initial mode: warn (exit 0 with output). After stabilization: block. |
| `{{cookiecutter.project_slug}}/scripts/generate-sbom.sh` | Bash. Conditional on `include_sbom`. CycloneDX for Python (`cyclonedx-py`) or for Node (`@cyclonedx/cyclonedx-npm`), polyglot path runs both. Output to `sbom/` directory. |
| `{{cookiecutter.project_slug}}/.github/workflows/ci.yml` | Single workflow with multiple jobs: `validate` (runs `make validate`), `hooks-test`, `codacy` (conditional), `snyk` (conditional), `codecov-upload` (conditional), `sbom` (conditional), `secret-scan` (always-on, TruffleHog OSS by default). Every action SHA-pinned per IMP-006. |

**Phase 4 gate:** instantiate template, run `make sync && make validate`
inside the instantiated project. All gates pass on the empty (but
fully-scaffolded) project.

---

## Phase 5 — Build glue

| File | Notes |
|---|---|
| `{{cookiecutter.project_slug}}/pyproject.toml` | Conditional Python path. Pins ruff, mypy, pytest, pytest-cov, pre-commit. uv-managed dep groups. |
| `{{cookiecutter.project_slug}}/package.json` | Conditional TS path. Pins typescript, eslint, prettier (optional). Test/coverage scripts run Node's built-in `node --test` / `--experimental-test-coverage` directly against the `tests/` suites — no vitest dependency ([#106](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/106)). |
| `{{cookiecutter.project_slug}}/tsconfig.json` | TS path. `"strict": true`, `"noUncheckedIndexedAccess": true`. |
| `{{cookiecutter.project_slug}}/.gitignore` | Per prior turn's content. |
| `{{cookiecutter.project_slug}}/.editorconfig` | Per prior turn's content. |
| `{{cookiecutter.project_slug}}/.env.example` | Per prior turn's content; conditional credential blocks. |
| `{{cookiecutter.project_slug}}/.pre-commit-config.yaml` | Per prior turn's content. |
| `{{cookiecutter.project_slug}}/CONTRIBUTING.md` | Per prior turn's content; reference `/sync` post-merge as a contributor obligation. |
| `{{cookiecutter.project_slug}}/LICENSE` | Conditional on `cookiecutter.license`. |
| `{{cookiecutter.project_slug}}/.codacy.yml` | Conditional on `include_codacy`. |
| `{{cookiecutter.project_slug}}/codecov.yaml` | Conditional on `include_codecov`. |
| `{{cookiecutter.project_slug}}/.snyk` | Conditional on `include_snyk`. |
| `{{cookiecutter.project_slug}}/.github/dependabot.yml` | Always present; conditional ecosystems. |
| `{{cookiecutter.project_slug}}/.github/PULL_REQUEST_TEMPLATE.md` | Per prior turn's content. |

**Phase 5 gate:** `pre-commit install && pre-commit run --all-files`
inside the instantiated project succeeds.

---

## Phase 6 — Standards register + SWEBOK doc anchors

| File | SWEBOK Anchor | GAP IDs |
|---|---|---|
| `{{cookiecutter.project_slug}}/docs/STANDARDS.md` | All standards (32675, 42010, AGENTS.md, IEEE 2675, CycloneDX/SPDX, CERT, SWEBOK v4) | GAP-040–046 |
| `{{cookiecutter.project_slug}}/docs/tooling-versions.md` | Cross-references STANDARDS.md | GAP-009 |
| `{{cookiecutter.project_slug}}/docs/PRD.md` | Requirements KA | n/a |
| `{{cookiecutter.project_slug}}/docs/ARCHITECTURE.md` | Ch 2 (full content, not skeleton): logical, process, deployment, data views; stakeholders & concerns; ASD section | GAP-026–030 |
| `{{cookiecutter.project_slug}}/docs/OPERATIONS.md` | Ch 6 (full content): Operations Planning / Delivery / Control; capacity, availability, backup/recovery, DR, environments, change management | GAP-001–003, 010, 012 |
| `{{cookiecutter.project_slug}}/docs/THREAT_MODEL.md` | Ch 13 (full content): assets, trust boundaries, STRIDE table, ML-specific section, container/cloud security, agentic-specific threats | GAP-013, 014, 015, 024 |
| `{{cookiecutter.project_slug}}/docs/SECURITY_PROGRAM.md` | Ch 13 (cross-cutting): DevSecOps lifecycle integration, SDLC security activities, security-testing levels | GAP-017, 025 |

**Phase 6 gate:** every doc in this phase passes `make marker-scan`
and references its SWEBOK anchor in the document header.

---

## Phase 7 — SWEBOK gap closure docs

| File | GAP IDs |
|---|---|
| `{{cookiecutter.project_slug}}/docs/monitoring-strategy.md` | GAP-007, 020 |
| `{{cookiecutter.project_slug}}/docs/operations/release-strategy.md` | GAP-004 |
| `{{cookiecutter.project_slug}}/docs/operations/feature-flags-policy.md` | GAP-005 |
| `{{cookiecutter.project_slug}}/docs/operations/rollback-runbook.md` | GAP-006 |
| `{{cookiecutter.project_slug}}/docs/operations/backup-restore-runbook.md` | GAP-002 |
| `{{cookiecutter.project_slug}}/docs/operations/risk-management.md` | GAP-008 |
| `{{cookiecutter.project_slug}}/docs/operations/incident-runbook.md` | GAP-011 |
| `{{cookiecutter.project_slug}}/docs/security/vulnerability-management.md` | GAP-016 |
| `{{cookiecutter.project_slug}}/docs/security/container-security.md` | GAP-015 |
| `{{cookiecutter.project_slug}}/docs/security/secrets-policy.md` | GAP-023 |
| `{{cookiecutter.project_slug}}/docs/cert-top-10-compliance.md` | GAP-021 |
| `{{cookiecutter.project_slug}}/docs/sbom-policy.md` | GAP-022, 044 |
| `{{cookiecutter.project_slug}}/docs/prompt-versioning-policy.md` | GAP-036 |
| `{{cookiecutter.project_slug}}/docs/llm-output-verification-rubric.md` | GAP-037, 038 |
| `{{cookiecutter.project_slug}}/docs/agent-runtimes.md` | GAP-039 |
| `{{cookiecutter.project_slug}}/docs/documentation-ownership.md` | GAP-034 |

**Phase 7 gate:** every file in this phase exists; every GAP-NNN
listed has at least one delivering file referenced.

---

## Phase 8 — Spec scaffolding & traceability

| File | GAP IDs |
|---|---|
| `{{cookiecutter.project_slug}}/specs/README.md` | n/a |
| `{{cookiecutter.project_slug}}/specs/deep_specs/README.md` | n/a |
| `{{cookiecutter.project_slug}}/specs/deep_specs/adr-template.md` | n/a |
| `{{cookiecutter.project_slug}}/specs/deep_specs/rfc-template.md` | n/a |
| `{{cookiecutter.project_slug}}/specs/deep_specs/design-template.md` | GAP-019 |
| `{{cookiecutter.project_slug}}/specs/deep_specs/adr-0001-governance-foundation.md` | seed example, GAP-029 |
| `{{cookiecutter.project_slug}}/specs/security-requirements/README.md` | GAP-018 |
| `{{cookiecutter.project_slug}}/specs/security-requirements/sec-req-template.md` | GAP-018 |
| `{{cookiecutter.project_slug}}/specs/traceability.json` | seed instance with the governance ADR mapped, GAP-031 |
| `{{cookiecutter.project_slug}}/specs/traceability.schema.json` | JSON Schema validating the matrix structure, GAP-031 |
| `{{cookiecutter.project_slug}}/report/README.md` | append-only policy, IMP-001 |

**Phase 8 gate:** `make check-traceability` returns clean on the seed
matrix.

---

## Phase 9 — Layer 3: Slash commands

Author 16 commands. Sources:

- **Port from govforge** (parameterize project-specific names, scopes,
  paths to `{{ cookiecutter.* }}`):
  CMD-001 prime, CMD-002 start, CMD-003 status, CMD-004 plan,
  CMD-005 implement, CMD-006 test, CMD-007 review, CMD-008 verify,
  CMD-010 commit, CMD-011 pull-request, CMD-012 session-log,
  CMD-014 spec-bump.
- **New, full text in `COMMAND_AND_AGENT_SPECS.md`:**
  CMD-013 sync, CMD-015 threat-model, CMD-016 check-traceability.
- **Port + extend:** CMD-009 audit. Add steps 10 and 11 covering
  sync recency and traceability validity.

**Phase 9 gate:** every command file passes marker-scan, has YAML
frontmatter with `description`, `argument-hint` (or omitted if no
args), and `allowed-tools`.

---

## Phase 10 — Layer 3: Agents

Author 7 agents. Sources:

- Port from govforge with parameterization:
  AGENT-001 lead-software-engineer, AGENT-002 sdlc-technical-writer,
  AGENT-003 test-automator, AGENT-004 ux-delight-specialist,
  AGENT-005 python-pro (Python path).
- New: AGENT-006 typescript-pro (TS path), AGENT-007 security-reviewer.

The conditional logic for AGENT-005 / AGENT-006 lives in
`hooks/post_gen_project.py`.

**Phase 10 gate:** each agent file has `name`, `description`, `model`,
`memory` frontmatter. Pass marker-scan.

---

## Phase 11 — Validation

1. From the template root, instantiate three test projects:
   - Python path with all integrations on
   - TypeScript path with all integrations on
   - Polyglot path with everything off (minimum surface)
2. For each: `cd <slug> && git init && make sync && make validate
   && make hooks-test && make check-traceability`.
3. For each: try `git checkout -b feat/test && touch x && git add x
   && git commit -m "test: hook"` then attempt `git push origin
   main:main`. Confirm the hook blocks. Then push to `feat/test` and
   confirm the hook allows.
4. Verify: `cookiecutter . --no-input` produces a directory passing
   all of the above on the first try.
5. Write the success artifact:
   `report/<UTC-timestamp>-validate-pass.md` summarizing the run.

**Phase 11 gate:** the success artifact exists and `git log` shows
no `--no-verify` commits anywhere in the build history.

---

## Status update protocol

After completing each phase, update
`SWEBOK_GAP_REGISTER.md` — change the relevant `Status` cells from
`planned` to `landed`. Commit per IMP-002:

```
chore(scaffold): land Phase N — <phase name>
```

Never amend a prior phase's commit. If a phase's deliverable is wrong,
write a follow-up commit with the fix.

---

## Hard rules during the build

- Never commit to `main` of this template repo. Use a `feat/scaffold-phase-<N>`
  branch and PR pattern, even if you're the only one merging.
- Never use `--no-verify` (CRIT-007 applies to this repo too).
- Author with no stub markers anywhere (CRIT-001).
- If a phase gate fails, stop and surface the failure. Do not skip ahead.
- The build itself is governed by the same rules the template ships.
  This is the dogfood test.
