# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}.

This site is generated from the contents of `docs/` by
[MkDocs](https://www.mkdocs.org/) with the
[Material](https://squidfunk.github.io/mkdocs-material/) theme.
The deploy is automated by `.github/workflows/docs.yml` on every
push to `{{ cookiecutter.default_branch_name }}`.

## Where to start

- **Standards register** — see [Standards](STANDARDS.md) for the
  authoritative list of standards this project conforms to.
- **MCP policy** — see [MCP policy](MCP_POLICY.md) for the rules
  that govern Model Context Protocol server registration.
- **Threat model** — see [Threat model](THREAT_MODEL.md) for the
  STRIDE-based assessment of agentic attack surface.

The repository's top-level governance files (`CLAUDE.md`,
`AGENTS.md`, `CONSTITUTION.md`, `DIRECTIVES.md`, `SECURITY.md`)
remain authoritative; this site mirrors documentation under
`docs/` only.

## Editing

- Add a new top-level page: drop the markdown file in `docs/`,
  then add a `nav:` entry in `mkdocs.yml`.
- Preview locally:

  ```sh
  uv tool run --with mkdocs-material mkdocs serve
  ```

- Validate the site builds cleanly (no broken refs):

  ```sh
  uv tool run --with mkdocs-material mkdocs build --strict
  ```

CI runs the `--strict` variant on every pull request that touches
`docs/` or `mkdocs.yml`.
