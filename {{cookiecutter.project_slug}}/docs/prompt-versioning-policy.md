# Prompt Versioning Policy

> **SWEBOK anchor:** v4.0a §4.16 (AI-assisted development —
> construction with LLMs).
> **Gap closed:** `GAP-036` (Prompt versioning policy — slash-command
> and agent-prompt changes are contract changes).
> **Status:** active.

---

## 1. Why this policy exists

LLM prompts are part of the running system's behavior. Changing a
prompt changes the contract between {{ cookiecutter.project_name }}
and its model provider in the same way changing a function signature
changes the contract between modules. SWEBOK v4 §4.16 calls out
prompt management as a first-class construction artifact precisely
because unmanaged prompt drift is one of the most common ways
agentic systems regress silently.

This policy makes prompt changes **mechanically auditable**:

- Every shipped prompt lives in version control under a known path.
- Every change to behavior produces a new file with a new version,
  not a mutation of the old file.
- Every shipped version has at least one assertion-bearing test
  in the eval harness.
- The eval harness runs in CI; threshold breaches block merges.

## 2. Scope

This policy governs three categories of prompt:

| Category | Location | Owner |
| --- | --- | --- |
| Application prompts (LLM calls in the runtime) | `prompts/` | feature owner |
| Slash-command prompts (Claude Code commands) | `.claude/commands/` | governance owner |
| Subagent prompts (Claude Code agents) | `.claude/agents/` | governance owner |

The directory layout, frontmatter schema, and immutability rules in
§3 apply to all three. The eval harness in §5 ships configured for
the **application prompts** category; slash-command and subagent
prompts are reviewed via the standard PR review path because their
"correctness" is harder to express as automated assertions.

## 3. Storage convention

Application prompts live under `prompts/`:

```
prompts/
└── <prompt-name>/
    ├── CHANGELOG.md
    └── v<N>.md
```

- The folder name `<prompt-name>` is the prompt's stable identifier.
  Pick once; do not rename. If a rename is unavoidable, ship the
  rename as a deprecation: leave the old folder, add the new folder,
  and remove the old one in a later major version after callers
  migrate.
- Versions are integer-major: `v1.md`, `v2.md`. There is no
  `v1.1.md`. Minor revisions to an unshipped version are fine; once
  the version lands on `{{ cookiecutter.default_branch_name }}`,
  it is immutable.
- The frontmatter schema is fixed:
  ```yaml
  ---
  name: <prompt-folder-name>     # must match the parent directory
  version: v<N>                  # must match the filename
  description: <one sentence>
  owner: <github-handle or team>
  ---
  ```
- Variables in the prompt body use double-brace syntax
  ({% raw %}`{{variable_name}}`{% endraw %}). The same syntax is what
  the eval harness resolves at evaluation time.

## 4. Immutability rule

Once a prompt version is on `{{ cookiecutter.default_branch_name }}`:

- **Allowed in-place:** typo fixes, formatting changes, comment
  additions — anything that does **not** change behavior. Note the
  edit in the prompt's `CHANGELOG.md`.
- **Not allowed in-place:** any change that could affect the model's
  output — instructions, persona, examples, output schema, variable
  semantics. These ship as `v<N+1>.md` and get their own
  `CHANGELOG.md` entry.
- **Never allowed:** deleting a version that has been on
  `{{ cookiecutter.default_branch_name }}`. If a version is broken
  and must not be used, mark it superseded in `CHANGELOG.md` and
  ship the corrected `v<N+1>.md`. The bad version stays on disk so
  the audit trail is complete (this mirrors `IMP-001`'s append-only
  rule for `report/`).

## 5. Eval coverage requirement

Every shipped prompt version has at least one test in
`evals/promptfooconfig.yaml` that exercises it. The test must:

- Reference the specific version file (`file://../prompts/<name>/vN.md`).
- Provide concrete `vars:` for every {% raw %}`{{var}}`{% endraw %} token
  in the body.
- Anchor `assert:` rules to a stable property of the expected output
  (proper-noun preservation, length budget, regex match, refusal of
  out-of-scope inputs) — not a verbatim string the model is unlikely
  to reproduce.
- Pass under `defaultTest.options.threshold = 1.0` so a single
  assertion failure breaks the gate.

`make eval` runs the harness. The CI workflow's `eval` job runs the
same target on every PR. A threshold breach is a non-zero exit and
blocks the merge.

The shipped baseline uses promptfoo's built-in `echo` provider so
the gate is hermetic — no API keys are required and CI can run
without secrets. When the project is ready to evaluate against a
real LLM, `evals/promptfooconfig.yaml` swaps the provider and the
assertions tighten. The contract — "every shipped prompt has eval
coverage" — does not change.

## 6. Change workflow

When changing prompt behavior:

1. **Plan.** Open or update an ADR or RFC under `specs/deep_specs/`
   describing the behavior change and the evidence that will
   validate it. Reference the prompt name and current version.
2. **Author.** Create `prompts/<name>/v<N+1>.md` (next integer
   version). Do not edit `v<N>.md`.
3. **Document.** Append a row to `prompts/<name>/CHANGELOG.md`
   covering: date, owner, behavior delta, eval evidence reference,
   rollback step, why.
4. **Test.** Add or update entries in `evals/promptfooconfig.yaml`
   that reference `vN+1.md`. Keep the `vN.md` tests until the
   runtime cuts over to the new version.
5. **Validate.** Run `make eval` locally. The gate must be green.
6. **Switch the runtime.** Update the runtime call site to load the
   new version file. Stage this in the same PR or a follow-up; the
   `CHANGELOG.md` entry should record which PR makes the cutover.
7. **Commit.** Use `IMP-002` conventional-commit format with the
   `prompts` scope: `feat(prompts): <name> v<N+1> — <one-line>`.

## 7. Slash-command and subagent prompts

`.claude/commands/*.md` and `.claude/agents/*.md` are also prompts
in the SWEBOK §4.16 sense. They follow this policy with two
adaptations:

- **Versioning is git-native.** Each file's git history is the
  version log. There is no `v1.md / v2.md` filename pattern; the
  filename is the stable identifier and `git log <file>` is the
  audit trail.
- **Eval coverage is reviewer-mediated.** `make eval` does not
  exercise these prompts because their "correctness" depends on
  the broader Claude Code session state (CWD, files present,
  prior context). The PR review acts as the gate: the reviewer
  must confirm the change is intentional and that the
  governance-auditor agent (Phase B1) has been re-run if a
  CRIT-class behavior is affected.

Behavior changes to slash-command or subagent prompts that affect a
**Critical** directive's enforcement are subject to the same
constraint as runtime hooks: ship the test first, then the
behavior change. See `DIRECTIVES.md` for the directive-class
definitions.

## 8. Auditing

`make validate` invokes `make eval` when an `evals/` directory is
present in the project. The CI `eval` job enforces the same gate
on every PR. To audit prompt history out of band:

```sh
git log --follow prompts/<name>/      # full history including renames
git diff <baseline>..HEAD prompts/    # what changed since <baseline>
make eval                             # green = current behavior holds
```

For the broader auditing path that ties prompt versions to spec
artifacts, see `scripts/check-traceability.sh` and
`specs/traceability.json` (the schema accepts prompt-file globs as
acceptance-criterion sources).

## 9. See also

- `prompts/README.md` — the storage convention.
- `evals/README.md` — how the evaluation harness works.
- `docs/llm-output-verification-rubric.md` *(when scaffolded in
  Phase 7)* — what counts as evidence that a prompt change was safe.
- `DIRECTIVES.md` — `CRIT-001` (no stub markers), `IMP-001`
  (append-only), `IMP-002` (conventional commits).
- SWEBOK Guide v4.0a §4.16 — AI-assisted development construction
  practices.
