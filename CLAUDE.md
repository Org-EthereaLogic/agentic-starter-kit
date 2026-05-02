# CLAUDE.md — Quick reference for Claude Code in agentic-starter-kit

Claude Code reads this file at session start. The operational source
of truth is `AGENTS.md`; this file is a concise companion.

## Start Here

1. Read `README.md` for the public contract and repository layout.
2. Read `AGENTS.md` for workflow, boundaries, and validation rules.
3. Read `docs/BRIEFING.md` before changing template governance prose.
4. Read `docs/BUILD_PLAN.md` and the relevant gap register before
   changing planned template content.

## Important Boundaries

- The root repository is the cookiecutter template source.
- `{{cookiecutter.project_slug}}/` is not a normal checked-out app; it
  is the source tree rendered into generated projects.
- Preserve cookiecutter variables and Jinja conditionals unless the
  template contract is intentionally changing.
- Keep planning documents in `docs/` and update references whenever a
  file moves.

## Common Checks

```sh
cookiecutter . --no-input -o "$TMPDIR/agentic-starter-kit-smoke"
grep -RIn --exclude-dir=.git "old/path/or/name" .
```

After rendering, run scaffold checks from the generated project when
dependencies are available:

```sh
make validate
make hooks-test
```

## File Map

| Path | Purpose |
| --- | --- |
| `README.md` | Public manual for the template repository |
| `AGENTS.md` | Agent operating rules for this repository |
| `docs/` | Planning corpus, methodology, research, and gap registers |
| `cookiecutter.json` | Template variable schema |
| `hooks/post_gen_project.py` | Conditional file pruning after render |
| `{{cookiecutter.project_slug}}/` | Template source rendered into projects |
| `.github/` | Automation, instructions, and ownership routing |

## See Also

- `{{cookiecutter.project_slug}}/CLAUDE.md` — Claude guidance shipped
  into generated projects.
- `{{cookiecutter.project_slug}}/AGENTS.md` — full generated-project
  agent guide.
