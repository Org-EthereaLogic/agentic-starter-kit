# Extension-Build Decisions Record

> **Purpose:** captures decisions made on review of the original
> extension-build planning files (`RESEARCH_FINDINGS.md`,
> `SWEBOK_GAP_REGISTER_EXTENSIONS.md`, `IDE_PROMPT_PHASE_12.md`)
> in response to the IDE agent's three concerns raised before the
> rails PR opened. Where this file conflicts with the original
> three planning files, **this file wins.**
>
> **Status:** binding. Append-only — corrections become new dated
> decisions, never edits to existing ones (per IMP-001).
>
> **Created:** 2026-05-01.

---

## Decision 1 — Rails-landing pattern

**Concern raised:** the three new planning files
(`RESEARCH_FINDINGS.md`, `SWEBOK_GAP_REGISTER_EXTENSIONS.md`,
`IDE_PROMPT_PHASE_12.md`) plus this decisions file are untracked
in the working tree. They cannot govern Phase 12 from outside the
audit trail.

**Decision.** Open a single PR titled
`chore(scaffold): land extension-build rails`
on branch `chore/extension-rails`, branched from current `main`.
The PR contains, and only contains, these four files:

- `RESEARCH_FINDINGS.md`
- `SWEBOK_GAP_REGISTER_EXTENSIONS.md`
- `IDE_PROMPT_PHASE_12.md`
- `EXTENSIONS_DECISIONS.md` (this file)

**Why.** Mirrors how the original five planning files
(BRIEFING, BUILD_PLAN, etc.) landed in Phase 0. Keeps Phase 2 (PR
#3) free of scope creep. Lets Phases 3–11 continue cleanly while
the extension scope sits documented and reviewable on `main`.

**Rejected alternative.** Folding rails into Phase 2's PR (#3) was
considered and rejected for scope-mixing reasons. Folding rails
into Phase 12's PR was considered and rejected because it
deferred the audit-trail visibility for an unbounded number of
PRs.

**Implication for the build plan.** Total PR count is 14 (was
13): nine remaining base-scaffold PRs (Phases 3–11), this rails
PR, and four extension PRs (Phases 12–15).

---

## Decision 2 — AGENTS.md → CLAUDE.md / GEMINI.md mechanic

**Concern raised.** The original `IDE_PROMPT_PHASE_12.md` Step 2
(GAP-EXT-001) instructs `os.symlink("AGENTS.md", "CLAUDE.md")` in
the post-gen hook. Symlinks are fragile cross-platform:

- Windows with default `core.symlinks=false` turns the symlink
  into a plain text file containing the target path.
- Some Codespaces / container configurations interact unpredictably
  with `git checkout` of symlinks.
- WSL → Windows-host file sharing has historically broken
  symlink semantics.

**Decision — REJECT symlinks. Use a sync-script + drift-check
pattern instead.**

The mechanic:

1. **AGENTS.md is canonical.** It is the source of truth.
   `CLAUDE.md` and `GEMINI.md` are *derived artifacts*, not source.
2. **Sync script.** `scripts/sync-agent-files.sh` copies
   `AGENTS.md` → `CLAUDE.md` and `AGENTS.md` → `GEMINI.md`,
   prepending a header to each derived file:
   ```
   <!-- AUTO-GENERATED from AGENTS.md by scripts/sync-agent-files.sh.
        Do not edit directly. Edit AGENTS.md and run `make sync-agents`. -->
   ```
3. **Makefile target.** `make sync-agents` wraps the script.
   Idempotent.
4. **Pre-commit hook.** A `local` hook in
   `.pre-commit-config.yaml` named `agent-files-current` strips
   the header from `CLAUDE.md` and `GEMINI.md` and compares the
   bodies byte-for-byte against `AGENTS.md`. Fails the commit
   if they differ, with a one-line remediation message:
   ```
   CLAUDE.md / GEMINI.md drift detected. Run: make sync-agents
   ```
5. **Post-gen hook (`hooks/post_gen_project.py`).** Runs
   `scripts/sync-agent-files.sh` once after cookiecutter
   instantiation so a freshly-generated project has all three
   files in sync from commit zero.
6. **`scripts/check-governance.sh` extension.** Adds a check
   that runs the same byte-compare as the pre-commit hook, so
   `make governance-check` catches drift even outside a commit.

**Why this is better than symlinks.**

| Property | Symlink | Sync + drift check |
|---|---|---|
| Cross-platform clean | ❌ Windows breaks default | ✅ Pure text-file ops |
| Codespaces / container safe | ⚠️ depends | ✅ Always |
| Single edit point | ✅ | ✅ (AGENTS.md) |
| Drift detection | n/a — drift impossible | ✅ Pre-commit + governance gate |
| Edit-friendly in editors | ⚠️ some editors follow target unpredictably | ✅ All editors handle plain files |
| Fits our governance model | ⚠️ silent | ✅ Mechanical, surfaced |

**Tradeoff acknowledged.** The user can edit `CLAUDE.md` directly
and the change appears to "work" until the next commit (when
pre-commit catches it). This is fine — the failure is mechanical
and the message tells them exactly what to do. The symlink
alternative had a worse failure: silent divergence on
Windows-hosted repos with no user-facing signal.

**Implication for GAP-EXT-001.** The deliverable text changes
from:

> *Replace CLAUDE.md / GEMINI.md with symlinks via
> `hooks/post_gen_project.py`*

To:

> *Add `scripts/sync-agent-files.sh` and `make sync-agents`;
> register pre-commit hook `agent-files-current`; extend
> `scripts/check-governance.sh` to verify CLAUDE.md and
> GEMINI.md are in sync with AGENTS.md.*

Section EXT-M of the gap register similarly: "symlink check"
becomes "sync-currency check."

---

## Decision 3 — AGENTS.md size targets

**Concern raised.** The original prompt set a hard 16 KiB cap.
The Phase 2 AGENTS.md is currently ~6 KB / 208 lines, but the
LF-spec rewrite (six core sections, three-tier boundaries,
directive ID citations) will probably grow rather than shrink.
16 KiB is roughly 400 lines at our wrap width — headroom but
not infinite.

**Decision.** Convert the hard cap into a tiered target:

- **Soft target: ≤16 KiB.** Aligns with the Princeton study's
  optimum. The lint check WARNs above this.
- **Hard cap: ≤24 KiB.** Aligns well below Codex's 32 KiB silent-
  truncation point. The lint check FAILs above this.
- **If the file legitimately needs more than 24 KiB**, that is
  a signal of over-specification. The remediation is one of:
  1. Push directory-specific detail into nested
     `AGENTS.override.md` files (the OpenAI Codex-repo pattern).
  2. Push capability detail into linked SKILL.md files
     (progressive disclosure).
  3. Split the project's surface — likely the project itself is
     trying to do too much.

**Lint check change.** `scripts/lint-agents.sh` adds two checks:

- `agents_md_size_warn` — exit 0 with stderr warning if
  `wc -c AGENTS.md` ≥ 16384.
- `agents_md_size_fail` — exit 1 if `wc -c AGENTS.md` ≥ 24576.

`make validate` does not block on warnings, only failures.

**Why not raise the soft target to 24 KiB.** The Princeton finding
is empirical: shorter agent-instruction files outperform longer
ones. Keeping the soft target at 16 KiB preserves the discipline.
The hard cap exists to prevent Codex truncation, not to bless
larger files.

**Implication for Phase 12.** The rewrite of AGENTS.md aims for
the soft target. If it lands between 16 and 24 KiB, the warning
is acceptable — but if it lands above 16 KiB, the agent should
explain why in the Phase 12 PR description (one of: legitimate
domain coverage, deferred refactor into AGENTS.override.md, or
deferred refactor into SKILL.md files).

---

## Decision 4 — Decisions file precedence

This file (`EXTENSIONS_DECISIONS.md`) joins the existing planning
set as a peer of `BRIEFING.md` and `RESEARCH_FINDINGS.md`. When
it conflicts with `RESEARCH_FINDINGS.md`,
`SWEBOK_GAP_REGISTER_EXTENSIONS.md`, or `IDE_PROMPT_PHASE_12.md`,
this file wins — but only on the points it explicitly addresses
(Decisions 1–3 above). Everything else in those files remains
authoritative.

Future decisions append below as `## Decision 5 — …`,
`## Decision 6 — …` and so on. Existing decision sections are
never edited. Corrections are new dated decisions referencing
the prior one.

---

## Decision 5 — Sync mechanic scope (template repo vs instantiated projects)

**Concern raised.** Decision 2 describes the `agent-files-current`
pre-commit hook and a `make sync-agents` target as part of the
template's pre-commit configuration. The template repository itself
(`agentic-starter-kit`) does not install pre-commit hooks on itself
— only instantiated projects do. This leaves an unstated question:
does the rails PR (and any future work that touches the rails files
at the template repo root) need the same sync mechanic running
against a top-level AGENTS.md?

**Decision.** **The sync mechanic ships in instantiated projects
only.** The template repo does not install the
`agent-files-current` hook on itself. Its AGENTS.md (when authored
at the top level) is non-templated and does not have
CLAUDE.md / GEMINI.md siblings to keep in sync. The files governed
by Decision 2 all live under `{{cookiecutter.project_slug}}/`,
which is rendered into instantiated projects.

If the template repo later acquires a top-level AGENTS.md (for
agent-assisted maintenance of the template itself), the sync
mechanic can be opted into at that time by adding the same hook
configuration to a (currently nonexistent) top-level
`.pre-commit-config.yaml`.

**Why this matters for the rails PR.** This decision documents
that the rails PR's modifications to the planning files (which
discuss the sync mechanic) do not trigger the sync mechanic's own
pre-commit check, because no such check is installed on the
template repo. Future-you reading this PR's history should not
expect to find one.

**Status.** Addendum to Decision 2; appended as Decision 5 per
Decision 4's append-only rule. Suggested by reviewer feedback on
the rails-PR planning step.

---

## Decision 6 — Sync drift detection runs in CI as well as pre-commit

**Concern raised** (reinforcement on Decision 2). The
`agent-files-current` pre-commit hook only fires when the
contributor runs `git commit` locally with the hook installed. A
PR that lands AGENTS.md content via the GitHub web editor, a
force-push from a stale branch, or any path that bypasses local
pre-commit is not caught by the hook alone.

**Decision.** Extend `make hooks-test` to perform the same
byte-compare that `agent-files-current` performs: strip the
auto-generated header from `CLAUDE.md` and `GEMINI.md`, compare
each body byte-for-byte against `AGENTS.md`, fail the test on
mismatch.

**Why.** `make hooks-test` runs unconditionally in CI's `validate`
job, so adding the sync-currency byte-compare to `hooks-test`
forces the check to run on every PR regardless of which files the
PR touches. This closes the gap between pre-commit (local, opt-in)
and CI (remote, mandatory) without inventing a new gate.

**Implication for the build plan.** Phase 4 (which lands
`make hooks-test`) and Phase 12 (which lands the sync mechanic)
must coordinate: whichever phase lands second extends
`hooks-test` to include the byte-compare. Phase 12 lands strictly
after Phase 4 in the current schedule, so Phase 12's author owns
the integration. Phase 12's PR description must call the
extension out explicitly so the dependency on Phase 4 is visible
in the audit trail.

**Status.** Refinement of Decision 2; appended as Decision 6 per
Decision 4's append-only rule. Suggested by reviewer reinforcement
on the rails-PR planning step.

---

## Open items not resolved here

The following questions surfaced in the agent's feedback but did
**not** require a decision before the rails PR opens:

- **Re-planning to fold extension gaps into Phases 0–11** —
  considered and rejected. The base-scaffold phases land
  unchanged. No re-plan.
- **Whether Scorecard / SLSA / docs-deploy workflows run
  successfully on the test instantiations** — that is a Phase 13
  / 14 concern, not a rails-PR concern. Defer.
- **MkDocs Material vs VitePress for the docs site** — defer to
  Phase 14. Cookiecutter variable already accommodates both
  paths.
- **`AGENTS.override.md` nesting depth conventions** — defer to
  Phase 12 authoring; document in `docs/agent-runtimes.md`.

---

## Sign-off

The rails PR (`chore/extension-rails`) is approved to open with
the three planning files plus this decisions file, contingent on
the following landing-time invariants:

1. The PR description references this decisions file in its
   summary.
2. The PR commits do not modify any file under
   `{{cookiecutter.project_slug}}/`. (That would mix scope.)
3. `make validate` runs cleanly on the rails PR — the planning
   files are markdown only, so this should be a no-op except for
   `marker-scan` over the new files (no stub markers permitted).

When merged, Phase 12 (after Phases 3–11 land) reads this file
as part of its required-pre-read alongside `BRIEFING.md`.
