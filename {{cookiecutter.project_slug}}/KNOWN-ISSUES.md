# Known Issues — {{ cookiecutter.project_name }}

Things you will hit on a fresh build that the toolchain does not
mechanically prevent. Read this once at scaffold time and again
the first time `make validate` or your initial CI run surprises
you.

---

## First CI run

### Required repo secrets

The CI workflow includes three token-backed integrations. Configure
the matching secret for each one you opted into, then rerun the
workflow once the secrets are in place.

| Job | Secret | Where to get it |
| --- | --- | --- |
| `codacy` | `CODACY_PROJECT_TOKEN` | Codacy → your repo → *Settings → Integrations → Project API* |
| `snyk` | `SNYK_TOKEN` | <https://app.snyk.io/account> → *Auth Token* |
| `codecov` | `CODECOV_TOKEN` | Codecov → repo settings (still required for **public** repos since 2024) |

Add at **GitHub → Settings → Secrets and variables → Actions →
New repository secret**. Then *Re-run failed jobs* on the affected
workflow run.

Codacy is the hard gate here. `snyk` runs with `continue-on-error:
true` and `codecov` sets `fail_ci_if_error: false`, so those two can
surface warnings without failing the whole workflow.

If you opted any integration off at scaffold time, the matching
job is absent from `ci.yml` and there is nothing to configure.

### Secret scanning uses TruffleHog OSS, not gitleaks

`gitleaks/gitleaks-action@v2` requires a paid `GITLEAKS_LICENSE`
for organization-owned repos. The kit replaces it with TruffleHog
OSS (Apache-2.0, no license required) by default. If your
organization standardizes on gitleaks, swap the secret-scan step
in `.github/workflows/ci.yml` and add a `GITLEAKS_LICENSE` repo
secret — the comment block in that file walks through it.

### CycloneDX SBOM job uses the project venv for Python scaffolds

When `include_sbom=yes` and the rendered project includes Python,
`scripts/generate-sbom.sh` invokes `cyclonedx-py` directly. In CI,
the SBOM job runs `uv sync --no-dev` first so `.venv` exists, then
`make sbom` prefers that environment when generating
`sbom-python.cdx.json`. If you change the script, keep the `.venv`
preference so the SBOM reflects the project environment instead of
an ad hoc shell state. TypeScript-only scaffolds use the npm SBOM
path, and projects rendered with `include_sbom=no` have no SBOM job.

---

## macOS local dev

### Bash 3.2

Apple ships Bash 3.2 (frozen at the GPLv2 line) and never upgrades
it. `scripts/check-doc-drift.sh` uses Bash 4+ associative arrays,
so on macOS Bash 3.2 it prints a WARN and exits 0 while the rest of
the shell-based governance checks should be run under Homebrew bash.

Recommendation: install Homebrew bash and put it on PATH ahead of
`/bin/bash`:

```bash
brew install bash
echo 'export PATH="'$(brew --prefix)'/bin:$PATH"' >> ~/.zshrc
exec zsh
```

After that, `bash --version` should report 5.x and the WARN goes
away.

### `/var` vs `/private/var` symlinks

macOS resolves `/var` as a symlink to `/private/var`. Tests that
compare `tempfile.TemporaryDirectory()` paths to values returned
by `process.cwd()` (Node) will fail because Node realpath-resolves
on macOS while Python `tempfile` does not. The shipped tests
already use `Path(...).resolve()` to normalize; if you add new
hook subprocess tests, follow the same pattern.

### Make targets that shell out to `node`

`make hooks-test` invokes `node` to exercise the runtime hook.
Node 20+ is required. Because the target calls `node --test`
directly, missing or older Node will fail the target as soon as the
JS hook tests are present. `nvm`-managed shells should activate a
compatible Node before running the suite.

---

## Dev container

### Ruff `spawn .venv/bin/python ENOENT` on first attach

Symptom: VS Code attaches to the dev container and the Ruff
extension reports `spawn /workspaces/<project>/.venv/bin/python
ENOENT` even though the container is healthy. Cause: VS Code reads
`python.defaultInterpreterPath` (pinned to `${workspaceFolder}/.venv/bin/python`
in `.devcontainer/devcontainer.json`) and starts the Python and
Ruff extensions before `postCreateCommand` finishes the first
`make sync` that creates the venv.

The shipped `devcontainer.json` declares `"waitFor":
"postCreateCommand"`, which holds the editor attach until the
post-create script exits. If you cloned an older container created
before this setting landed, rebuild once
(`Dev Containers: Rebuild Container`) so the new wait behavior
takes effect.

### Dev container internet access blocked

Symptom: `post-create.sh` prints
`WARN: no outbound HTTPS access to pypi.org from this container`,
or downstream `apt-get update`, `uv sync`, `npm install`, `gh auth`,
or `make sync` fail with `Could not resolve host`,
`Connection refused`, `proxyError`, or similar. The container is
running but cannot reach the package registries it needs.

Common causes in 2026, in rough order of frequency, with the
remediation that actually solves each:

1. **VS Code "Restricted Network Access"** (VS Code 1.96+ / Insiders).
   The IDE shows a one-shot dialog the first time the container
   tries to reach a domain; if it was dismissed, the dialog will
   not reappear automatically. Fix: open the command palette →
   `Dev Containers: Show Container Log` → look for the rejected
   domain → re-allow via *Settings → Application → Restricted
   Network Access*. To pre-allow on every fresh build, add
   `"workbench.experimental.remoteIndicator.showExtensionRecommendations": false`
   and the appropriate trusted-domain settings to your VS Code
   *user* settings (workspace settings cannot grant network trust).

2. **GitHub Codespaces "Restricted internet access"**. The
   Codespaces web UI has a per-codespace allowlist. Until GitHub
   ships a documented declarative schema, configure via the
   Codespaces UI: *Repository → Settings → Codespaces → Network
   policy* (or the org-level equivalent for org-owned repos).
   Per-codespace overrides land under the codespace's own *Settings
   → Advanced* page.

3. **GitHub Copilot Coding Agent firewall**. The cloud-hosted agent
   has a default-deny outbound firewall introduced in early 2026.
   Fix: create `.github/copilot/firewall.yml` with the domains the
   agent needs to reach. At minimum:

   ```yaml
   # .github/copilot/firewall.yml
   allowed_domains:
     - pypi.org
     - files.pythonhosted.org
     - registry.npmjs.org
     - ghcr.io
     - github.com
     - api.github.com
     - objects.githubusercontent.com
   ```

   This file applies only to the cloud Copilot Coding Agent — it
   does **not** affect a local VS Code dev container.

4. **Corporate proxy on the host**. The container bridge network
   inherits the host's resolver but not its proxy. Fix: add
   `containerEnv` entries to `.devcontainer/devcontainer.json`:

   ```jsonc
   "containerEnv": {
     "UV_LINK_MODE": "copy",
     "HTTP_PROXY": "${localEnv:HTTP_PROXY}",
     "HTTPS_PROXY": "${localEnv:HTTPS_PROXY}",
     "NO_PROXY": "${localEnv:NO_PROXY}"
   }
   ```

If the container is up and you only need a one-shot recovery, run
`bash .devcontainer/post-create.sh` after granting access — it is
idempotent.

### Stale `.venv` after a base-image upgrade

Symptom: `make sync` reports success but tools that depend on
`.venv/bin/python` (Ruff, pytest, the Python extension) still fail
with `ENOENT` or report a missing interpreter. Cause: the venv was
created against a Python that is no longer present — for example,
the dev container's base image was rebumped from 3.12.6 to 3.12.13,
or the host's pyenv shims rotated, or the venv was carried over a
device migration. `uv sync` writes lock and metadata files but does
not detect that `.venv/bin/python` itself is a dangling symlink.

`sync-python` now self-heals: if `.venv` exists but
`.venv/bin/python --version` fails, the target removes the venv
before re-syncing, so the next interpreter resolves cleanly. If you
hit the symptom on an older clone of the template, run `make sync`
once and the recovery is automatic.

---

## Tooling defaults

### Python ≥ 3.11

`pyproject.toml` declares `requires-python = ">=3.11"`. CI matrices
target 3.11 and 3.12. If you need 3.10 support, override the
constraint in your fork — but note the kit's strict-mode
type-checker config and several dev-deps assume 3.11+.

### ruff line-length is 120

The kit's `[tool.ruff] line-length = 120` matches the live
EthereaLogic product baseline (DriftSentinel, AetheriaForge,
govforge). Black-style 88 is intentionally not the default. If
your team prefers 88, change the value in `pyproject.toml` and
rerun `ruff format`.

### `ty` is the default type-checker, not mypy

The template defaults to `ty`. Choose `python_typechecker=mypy` at
scaffold time if you need an established stub-heavy ecosystem
(e.g. SQLAlchemy with mypy plugins). The mypy variant ships a
commented `[[tool.mypy.overrides]]` block for scientific deps
(matplotlib, scipy, seaborn, sklearn, statsmodels) — uncomment what
your project actually imports. pandas and numpy intentionally are
not in that list because both ship usable stubs in 2026.

### `make validate` is the canonical pre-merge gate

Linting, type-checking, and tests are aggregated under `validate`
along with the governance gates. Run it before pushing; CI runs
the same target.

---

## Where to file new issues

Open a ticket against
<https://github.com/Org-EthereaLogic/agentic-starter-kit> when
you find new first-run friction. The kit treats first-run breakers
as build-quality issues, not user error — every previously-fixed
class of failure has a labelled issue showing the root cause and
the patch. See closed issues #41–#44 for the recent history.

Items that do **not** belong in this document: project-specific
runbooks, library-version churn, your team's local conventions.
Those go in `docs/` or your team wiki.
