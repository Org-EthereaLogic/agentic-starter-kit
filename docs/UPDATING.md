# Updating a Generated Project

The agentic-starter-kit ships a dual-mode template — projects can be
scaffolded with either [cookiecutter] (one-shot render) or [copier]
(scaffold plus an upgrade flow). This document is for projects
rendered with **copier**: it explains how to pull new template
releases into an existing project and resolve the conflicts that
arise on locked governance files.

Projects rendered with cookiecutter cannot be auto-updated; the
remediation is to render a new project with copier and migrate
content over.

[cookiecutter]: https://cookiecutter.readthedocs.io
[copier]: https://copier.readthedocs.io

---

## Why an upgrade flow exists

Phase A and B governance changes (`AGENTS.md`, `DIRECTIVES.md`,
`.claude/hooks/`, CI workflows, `Makefile.fragments/`) land in the
template every release. Without `copier update`, those changes
never reach scaffolds rendered six months ago — the project drifts
out of compliance silently. The Phase C gate is explicit about
this: a six-month-old smoke project must absorb every Phase A/B/C
addition via `copier update` without merge conflicts on locked
governance files.

## Prerequisites

```sh
pipx install copier            # or: pip install --user copier
git status                     # working tree must be clean
ls .copier-answers.yml         # required — created at first render
```

If `.copier-answers.yml` is missing, the project was rendered with
cookiecutter or by hand. To opt in to the copier upgrade flow,
render a fresh project with copier and migrate content. There is
no in-place migration path from cookiecutter to copier.

## Standard upgrade

```sh
copier update --skip-answered
```

What this does:

1. Reads `.copier-answers.yml` to learn the template source URL,
   the commit you rendered from, and your previous answers.
2. Fetches the latest tagged template release.
3. Re-renders the template against your saved answers and
   produces a three-way diff: original render → current files →
   new render.
4. Writes the new render and surfaces conflicts as `*.rej` files
   alongside the originals.

Use `--defaults` if you want to accept upstream defaults for any
new variables that have been added since your last render. Without
it, copier prompts for each new variable.

## Resolving conflicts on locked governance files

Some files in the scaffold are **template-owned** — they should
match the template release verbatim. Local edits to these files
are an anti-pattern; copier will surface a conflict on update,
and the correct resolution is almost always *take theirs*
(accept the template version) and reapply the local intent
elsewhere.

Locked files (template-owned, accept template version on update):

| Path | Owner | If you have local edits |
| --- | --- | --- |
| `CONSTITUTION.md` | template | Move project-specific addenda to `docs/` |
| `DIRECTIVES.md` | template | Add project-specific directives in a separate `docs/PROJECT_DIRECTIVES.md` |
| `.claude/hooks/pre-tool-use.js` | template | Open an issue against this template; do not patch in place |
| `Makefile.fragments/*.mk` | template | Override targets in your project-local `Makefile`, not the fragments |
| `scripts/check-*.sh` | template | Override behavior via env vars; do not edit |
| `.github/workflows/ci.yml` | template | Add jobs in a sibling workflow file |

Negotiable files (project-owned, merge as you would any conflict):

| Path | Owner | Notes |
| --- | --- | --- |
| `README.md` | project | Template ships a starting point only |
| `pyproject.toml`, `package.json` | project | Add deps; keep the tool config the template ships |
| `docs/ARCHITECTURE.md`, `docs/THREAT_MODEL.md` | project | Template ships scaffolds; project owns content |
| `specs/**` | project | Project-specific |
| `tests/**` | project | Add tests; do not delete the template's hook regression suite |

### Recommended workflow

```sh
git switch -c chore/template-update
copier update --skip-answered
git status                     # review what changed
make validate                  # verify gates still green

# For each .rej file (only on locked files), accept "theirs":
for rej in $(find . -name "*.rej"); do
    target="${rej%.rej}"
    cp "$target.orig" "$target"     # if copier wrote .orig
    rm "$rej"
done

git diff                       # final review
git commit -m "chore: copier update to template vX.Y.Z"
```

Always run `make validate` before committing the merged result.
The validation gate is the same one CI enforces; if it fails after
the merge, the template release introduced a regression OR your
project has drift on a locked file.

## Skipping a release

Copier walks each release in order, applying its `_migrations`. To
skip a release, pass an explicit version:

```sh
copier update --vcs-ref vX.Y.Z
```

This is rarely the right answer — migrations are cumulative.
Prefer to land each release and resolve conflicts as they appear.

## Cookiecutter-rendered projects

If `.copier-answers.yml` is absent, you rendered with cookiecutter
and there is no in-place upgrade path. Two options:

1. **Render fresh and merge.** Render a new project with copier,
   then port your project-owned content (`docs/`, `specs/`,
   `tests/`, project source) across.
2. **Stay on cookiecutter.** No upgrade flow; absorb template
   changes manually by diffing against this repo.

Option 1 is the path the Phase C gate is designed around. Option 2
is the migration cost of having opted in to cookiecutter at the
beginning.

## See also

- [Copier docs — updating a project](https://copier.readthedocs.io/en/stable/updating/)
- `README.md` — template-repo manual; lists `copier copy` and
  `copier update` as supported flows.
- `docs/BRIEFING.md` — locked-file inventory and the rationale for
  template ownership.
