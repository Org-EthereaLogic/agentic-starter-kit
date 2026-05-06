# SWEBOK Gap Register — Extensions

> **Precedence note:** `EXTENSIONS_DECISIONS.md` supersedes specific
> portions of this file. Specifically:
>
> - **Decision 2** replaces the symlink mechanic in GAP-EXT-001 and
>   the related Section EXT-M with a sync-script + drift-check
>   pattern (`scripts/sync-agent-files.sh`, `make sync-agents`,
>   pre-commit `agent-files-current` hook).
> - **Decision 3** replaces the hard 16 KiB cap on AGENTS.md with a
>   tiered target (soft warn ≥16 KiB, hard fail ≥24 KiB).
>
> Read `EXTENSIONS_DECISIONS.md` first when these subjects come up.
> Other rows in this register remain authoritative.
>
> **Purpose:** continuation of `SWEBOK_GAP_REGISTER.md` capturing
> **24 additional gaps** identified through external-template
> research (`RESEARCH_FINDINGS.md`). These are NOT SWEBOK-driven —
> they're driven by survey of popular GitHub templates, OpenSSF
> standards, and the agentic-tooling ecosystem.
>
> **Status convention:** same as parent register (`planned`,
> `in_progress`, `landed`, `needs_fix`).
>
> **Closing criterion:** every row reaches `landed` and the
> verifying CI gate (where applicable) is green.
>
> **Read first:** `RESEARCH_FINDINGS.md` for the full rationale
> behind each row, then `EXTENSIONS_DECISIONS.md` for binding
> overrides.

---

## Section EXT-A — Cross-Tool Agent Compatibility

| ID | Gap | Deliverable | CI Verifier | Status |
|---|---|---|---|---|
| GAP-EXT-001 | AGENTS.md becomes the **primary** cross-tool standard file (Linux Foundation Agentic AI Foundation); CLAUDE.md and GEMINI.md become **derived artifacts** kept in sync via `scripts/sync-agent-files.sh` (replaces the originally-proposed symlink mechanic — see `EXTENSIONS_DECISIONS.md` Decision 2); `AGENTS.override.md` documented for nested overrides; three-tier boundary structure (always do / ask first / never do); soft-target 16 KiB / hard-cap 24 KiB per Decision 3 | Rewrite `{{cookiecutter.project_slug}}/AGENTS.md`; add `scripts/sync-agent-files.sh` + `make sync-agents`; add pre-commit `local` hook `agent-files-current`; extend `hooks/post_gen_project.py` to invoke the sync script after rendering; extend `scripts/check-governance.sh` with the same byte-compare; add `docs/agent-runtimes.md` section on AGENTS.md spec compliance | `make governance-check` (extended: verify CLAUDE.md and GEMINI.md bodies match AGENTS.md after stripping the auto-generated header) + pre-commit `agent-files-current` hook | planned |
| GAP-EXT-002 | Skills system per Linux Foundation SKILL.md spec — portable directory: `SKILL.md` + optional `scripts/` + `references/` + `assets/`; progressive disclosure via frontmatter; 2 seed skills shipped | `{{cookiecutter.project_slug}}/.claude/skills/governance-audit/SKILL.md` + `{{cookiecutter.project_slug}}/.claude/skills/spec-bump/SKILL.md`; `docs/agent-skills-pattern.md` | `scripts/lint-agents.sh` (BLOATED_SKILL check) | planned |

---

## Section EXT-B — Supply-Chain Security (OpenSSF stack)

| ID | Gap | Deliverable | CI Verifier | Status |
|---|---|---|---|---|
| GAP-EXT-003 | OpenSSF Scorecard GitHub Action — runs 18+ security checks; baseline target ≥7/10; SARIF results uploaded to code-scanning | `.github/workflows/scorecard.yml` (SHA-pinned per IMP-006); `docs/security/scorecard-policy.md` | scorecard workflow | planned |
| GAP-EXT-004 | SLSA L3 build provenance via `slsa-framework/slsa-github-generator` for release artifacts (conditional on `include_sbom=yes`) | `.github/workflows/slsa-provenance.yml`; `docs/security/slsa-policy.md` | slsa-provenance workflow | planned (conditional) |
| GAP-EXT-005 | SECURITY-INSIGHTS.yml — machine-readable security info per OpenSSF format; required file in governance-check | `{{cookiecutter.project_slug}}/SECURITY-INSIGHTS.yml`; updated `scripts/check-governance.sh` | `make governance-check` | planned |
| GAP-EXT-006 | OpenSSF Best Practices Badge opt-in process documented (not auto-enrolled); CERT-Top-10-style self-audit aligned to badge criteria | `docs/security/openssf-badge-path.md`; updated `docs/cert-top-10-compliance.md` cross-references | n/a | planned |

---

## Section EXT-C — Reproducible Environments

| ID | Gap | Deliverable | CI Verifier | Status |
|---|---|---|---|---|
| GAP-EXT-007 | Devcontainer support — `.devcontainer/devcontainer.json` with language-conditional features, `postCreateCommand` running `make sync && pre-commit install`, curated VS Code extensions list | `{{cookiecutter.project_slug}}/.devcontainer/devcontainer.json`; conditional `Dockerfile`; `docs/codespaces-and-devcontainers.md` | manual: open in Codespace, verify `make validate` succeeds | planned |

---

## Section EXT-D — Release Automation

| ID | Gap | Deliverable | CI Verifier | Status |
|---|---|---|---|---|
| GAP-EXT-008 | release-please (Google) GitHub Action that creates a single Release PR aggregating conventional commits; merging the PR publishes; conditional on `include_release_automation=yes` | `.github/workflows/release-please.yml`; `release-please-config.json`; `release-please-manifest.json`; `.cz.toml` (Commitizen helper); CONTRIBUTING.md release section | release-please workflow | landed (conditional) |
| GAP-EXT-014 | commitlint as commit-msg pre-commit hook to mechanically enforce IMP-002 | Updated `.pre-commit-config.yaml` (commit-msg stage); `commitlint.config.cjs`; documented `commitizen` as optional helper in CONTRIBUTING.md | pre-commit (commit-msg stage) | planned |

---

## Section EXT-E — Documentation Site

| ID | Gap | Deliverable | CI Verifier | Status |
|---|---|---|---|---|
| GAP-EXT-009 | Documentation site generator — MkDocs Material (Python path) or VitePress (TS path); GitHub Pages auto-deploy; conditional on `include_docs_site=yes` | `mkdocs.yml` OR `.vitepress/config.ts`; `.github/workflows/docs-deploy.yml`; `docs/index.md` landing page | docs-deploy workflow | planned (conditional) |

---

## Section EXT-F — Repository Hygiene & Community Files

| ID | Gap | Deliverable | CI Verifier | Status |
|---|---|---|---|---|
| GAP-EXT-010 | CHANGELOG.md per Keep a Changelog format; required by release-please anyway | `{{cookiecutter.project_slug}}/CHANGELOG.md` (seed entry only); update `scripts/check-governance.sh` to require it | `make governance-check` | planned |
| GAP-EXT-011 | CODE_OF_CONDUCT.md per Contributor Covenant 2.1 | `{{cookiecutter.project_slug}}/CODE_OF_CONDUCT.md`; update `scripts/check-governance.sh` to require it | `make governance-check` | planned |
| GAP-EXT-012 | Issue templates — bug_report, feature_request, support — as GitHub issue forms (YAML) | `.github/ISSUE_TEMPLATE/bug_report.yml`, `feature_request.yml`, `support.yml`, `config.yml` | n/a | planned |
| GAP-EXT-013 | Optional community files: CITATION.cff (academic), FUNDING.yml (sponsorship), MAINTAINERS.md (ownership) — conditional on cookiecutter options | `{{cookiecutter.project_slug}}/CITATION.cff` (conditional `include_citation`); `.github/FUNDING.yml` (conditional `include_funding`); `MAINTAINERS.md` (always; seeds with author info) | n/a | planned (some conditional) |

---

## Section EXT-G — Python Dependency Hygiene

| ID | Gap | Deliverable | CI Verifier | Status |
|---|---|---|---|---|
| GAP-EXT-015 | deptry — unused / undeclared / misused dependency detection (Python path only) | Updated `pyproject.toml` (deptry in dev group); `Makefile` (`make deptry`); `make validate` adds the gate | `make validate` | planned (Python / polyglot only) |

---

## Section EXT-H — Spec-Driven Development Compatibility

| ID | Gap | Deliverable | CI Verifier | Status |
|---|---|---|---|---|
| GAP-EXT-016 | OpenSpec-style brownfield change-proposal pattern — `specs/changes/<change-id>/{proposal,delta,acceptance}.md`; lighter than full ADR; archives to `specs/deep_specs/changes-archive/` on merge; plus Spec Kit + BMAD compatibility docs | `{{cookiecutter.project_slug}}/specs/changes/README.md`; `specs/changes/change-template/{proposal,delta,acceptance}.md`; `docs/sdd-frameworks-compatibility.md` covering Spec Kit, OpenSpec, BMAD | `scripts/check-traceability.sh` (extended to walk `specs/changes/`) | planned |
| GAP-EXT-022 | BMAD persona mapping — show how a BMAD user finds the equivalent agent in our template | `docs/bmad-mapping.md` | n/a | planned |

---

## Section EXT-I — Agentic Workflow Patterns

| ID | Gap | Deliverable | CI Verifier | Status |
|---|---|---|---|---|
| GAP-EXT-017 | Adversarial review pattern — `/adversarial-review` runs `security-reviewer` + `lead-software-engineer` in opposition until APPROVED or 5 rounds; catches errors single-pass review misses | `{{cookiecutter.project_slug}}/.claude/commands/adversarial-review.md` | n/a | planned |
| GAP-EXT-018 | Live AI monitoring — `PostToolUse` logging hook appends to `.claude/agent-memory/tool-trace.jsonl`; `make monitor` tails the trace | `{{cookiecutter.project_slug}}/.claude/hooks/post-tool-use.js`; `Makefile` (`make monitor`); update `.claude/settings.json` to register the hook | manual smoke test | planned |
| GAP-EXT-019 | PreCompact context-snapshot hook — saves session state before Claude Code's auto-compression triggers; appends to `report/<UTC-timestamp>-pre-compact-snapshot.md` per IMP-001 | `{{cookiecutter.project_slug}}/.claude/hooks/pre-compact.js`; update `.claude/settings.json` | manual smoke test | planned |
| GAP-EXT-020 | MCP server documentation — recommended servers (filesystem, git, semgrep, sequential-thinking), security-scanner pattern for vetting third-party MCP servers; **no auto-install** | `docs/mcp-servers.md`; sample `.mcp.json.example` (gitignored canonical, example committed) | n/a | planned |

---

## Section EXT-J — Agent / Command Quality Gate

| ID | Gap | Deliverable | CI Verifier | Status |
|---|---|---|---|---|
| GAP-EXT-021 | `lint-agents.sh` — static-analysis layer for agents and commands; detects EMPTY_DESCRIPTION, MISSING_TRIGGER, BLOATED_SKILL, ORPHAN_REFERENCE, DEAD_CROSS_REF, OVER_CONSTRAINED, AGENTS_MD_OVERSIZE_WARN, AGENTS_MD_OVERSIZE_FAIL; STUB_MARKER reuses marker-scan | `{{cookiecutter.project_slug}}/scripts/lint-agents.sh`; `Makefile` (`make lint-agents`); add to `make validate` | `make validate` | planned |

---

## Section EXT-K — Operational Polish

| ID | Gap | Deliverable | CI Verifier | Status |
|---|---|---|---|---|
| GAP-EXT-023 | Just (justfile) as alternative to Makefile — cleaner syntax, cross-platform; conditional on `task_runner=just` cookiecutter option | `{{cookiecutter.project_slug}}/justfile`; `hooks/post_gen_project.py` removes the unused one (Makefile vs justfile) | manual: `just validate` works the same as `make validate` | planned (conditional) |
| GAP-EXT-024 | Onboarding automation — strengthen `/start` to detect missing tooling per OS; `bootstrap.sh` installs uv / Node / pre-commit / gh CLI then runs `make sync` | `{{cookiecutter.project_slug}}/scripts/bootstrap.sh`; updated `.claude/commands/start.md`; README quickstart references both | manual smoke test | planned |

---

## Section EXT-L — Cookiecutter Variable Schema Additions

The above introduce new cookiecutter variables. These get added to
the existing `cookiecutter.json` (do not break parent schema):

```json
{
  "include_docs_site": ["yes", "no"],
  "include_release_automation": ["yes", "no"],
  "include_citation": ["no", "yes"],
  "include_funding": ["no", "yes"],
  "include_scorecard": ["yes", "no"],
  "include_slsa": ["no", "yes"],
  "task_runner": ["make", "just"]
}
```

`hooks/post_gen_project.py` is extended to handle each conditional
removal, and to invoke `scripts/sync-agent-files.sh` once after
rendering (per `EXTENSIONS_DECISIONS.md` Decision 2).

---

## Section EXT-M — Required-files extensions to `check-governance.sh`

The script now requires:

```text
CONSTITUTION.md         (existing)
DIRECTIVES.md           (existing)
SECURITY.md             (existing)
SECURITY-INSIGHTS.yml   (NEW per GAP-EXT-005)
AGENTS.md               (existing — now primary, source of truth)
CLAUDE.md               (existing — now derived artifact)
GEMINI.md               (existing — now derived artifact)
README.md               (existing)
CHANGELOG.md            (NEW per GAP-EXT-010)
CODE_OF_CONDUCT.md      (NEW per GAP-EXT-011)
MAINTAINERS.md          (NEW per GAP-EXT-013)
```

Plus existence of folders: `docs/`, `specs/deep_specs/`,
`specs/security-requirements/`, `specs/changes/` (NEW per GAP-EXT-016),
`report/`, `.claude/skills/` (NEW per GAP-EXT-002), `.devcontainer/`
(NEW per GAP-EXT-007).

Plus the **agent-files sync-currency check** (NEW per `EXTENSIONS_DECISIONS.md`
Decision 2): after stripping the auto-generated header from
`CLAUDE.md` and `GEMINI.md`, both bodies match `AGENTS.md`
byte-for-byte. **Replaces** the originally-proposed symlink-inode
check.

Plus the **AGENTS.md size check**: ≥16 KiB warns,
≥24 KiB fails (per `EXTENSIONS_DECISIONS.md` Decision 3).

---

## Section EXT-N — `make validate` extensions

The unified validation gate now runs (in order):

```text
marker-scan          (existing)
governance-check     (extended per EXT-M)
sync-agents-currency (NEW — implicit in governance-check)
lint-agents          (NEW per GAP-EXT-021)
check-traceability   (existing, extended for specs/changes/)
check-doc-drift      (existing)
deptry               (NEW per GAP-EXT-015 — Python / polyglot only)
lint                 (existing)
typecheck            (existing)
test                 (existing)
```

CI workflow `.github/workflows/ci.yml` adds parallel jobs for:

```text
scorecard            (NEW per GAP-EXT-003)
slsa-provenance      (NEW per GAP-EXT-004 — release events only)
release-please       (NEW per GAP-EXT-008 — main branch only)
docs-deploy          (NEW per GAP-EXT-009 — main branch only)
```

---

## Section EXT-O — Build phase mapping

These extensions form **Phase 12** through **Phase 15** of the build:

| Phase | Title | Gaps |
|---|---|---|
| 12 | Cross-tool standardization & community files | GAP-EXT-001, 002, 010, 011, 012, 013 |
| 13 | Supply-chain security stack | GAP-EXT-003, 004, 005, 006 |
| 14 | Reproducible env + release automation + docs site | GAP-EXT-007, 008, 009, 014, 015 |
| 15 | Workflow patterns + quality gate + polish | GAP-EXT-016, 017, 018, 019, 020, 021, 022, 023, 024 |

---

## Section EXT-P — Done summary (for the extensions)

The extension is complete when:

1. Every row in this register reads `landed` (24 new rows).
2. The extended `make validate` passes on instantiated projects
   for all three test paths (Python, TypeScript, polyglot-minimum).
3. The extended CI workflow runs cleanly (Scorecard ≥7/10 baseline,
   release-please workflow opens a Release PR after the first
   conventional-commit, docs-deploy publishes to Pages).
4. AGENTS.md is the canonical instruction file; CLAUDE.md and
   GEMINI.md are auto-generated from it and the
   `agent-files-current` pre-commit hook + governance check both
   pass.
5. The 2 seed skills load via Claude Code's progressive-disclosure
   mechanism (smoke test).
6. Devcontainer opens in Codespaces (or local VS Code) and
   `make validate` passes inside it on first boot.
7. `RESEARCH_FINDINGS.md` is updated with each row's `Status`
   column matching this register.

When all seven conditions hold, write a top-level
`report/<UTC-timestamp>-extensions-validate-pass.md` summarizing the
run. That artifact closes Phase 15.
