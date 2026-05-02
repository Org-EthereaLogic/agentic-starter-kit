# Agents — agentic-starter-kit

Operational guardrails for AI coding agents working in this
cookiecutter template repository.

## Mission

Maintain a project template that scaffolds a five-layer agentic
governance stack from commit zero. The repository owns the template
source, build plan, planning corpus, and post-generation pruning hook;
generated projects own their rendered copies after cookiecutter runs.

## Repository Map

- `README.md` — template-repo manual and public entrypoint.
- `docs/` — planning documents, research, methodology, and SWEBOK gap
  registers for this template repository.
- `cookiecutter.json` — variable surface for generated projects.
- `hooks/post_gen_project.py` — conditional pruning after generation.
- `{{cookiecutter.project_slug}}/` — rendered project template tree.
- `.github/` — repository automation, review ownership, and Copilot
  instructions.

## Pre-Read Order

Before substantive changes, read in this order:

1. `README.md` for repository purpose, usage, and current layout.
2. `docs/BRIEFING.md` for authoring discipline and build governance.
3. `docs/BUILD_PLAN.md` when changing planned template content.
4. `docs/SWEBOK_GAP_REGISTER.md` and
   `docs/SWEBOK_GAP_REGISTER_EXTENSIONS.md` when changing governance
   scope or SWEBOK coverage.
5. The nearest file or directory README for the subtree being changed.

## Boundaries

- Keep root focused on canonical entrypoints, manifests, automation,
  and instruction files.
- Keep planning and research documents under `docs/`.
- Treat `{{cookiecutter.project_slug}}/` as template source, not as an
  already-rendered project.
- Preserve Jinja syntax in template files. Do not replace
  cookiecutter variables with local sample values.
- Do not move generated-project governance files out of the template
  tree unless the cookiecutter contract changes intentionally.

## Workflow

- Plan from the nearest controlling file or spec before editing.
- Make the smallest change that satisfies the task.
- Update path references in the same change when moving files.
- Run focused checks first, then broader template validation when
  available.
- Report verification evidence and any checks that were not run.

## Useful Checks

- `cookiecutter . --no-input -o "$TMPDIR/agentic-starter-kit-smoke"`
  verifies the template renders with defaults.
- `make validate` inside a rendered project verifies the scaffold when
  dependencies are installed.
- `grep -RIn --exclude-dir=.git "<old-path>" .` is the fallback stale
  path check when ripgrep is unavailable.

## Related Guides

- `CLAUDE.md` — Claude Code quick reference for this repository.
- `{{cookiecutter.project_slug}}/AGENTS.md` — guidance shipped into
  generated projects.
- `{{cookiecutter.project_slug}}/CLAUDE.md` — Claude Code guidance
  shipped into generated projects.
