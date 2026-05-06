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
| `coverage` | `CODECOV_TOKEN` | Codecov → repo settings (still required for **public** repos in 2026) |

Add at **GitHub → Settings → Secrets and variables → Actions →
New repository secret**. Then *Re-run failed jobs* on the affected
workflow run.

Codacy is the hard gate here. `snyk` runs with `continue-on-error:
true` and `coverage` sets `fail_ci_if_error: false`, so those two can
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

### CycloneDX SBOM job runs inside the project venv

`scripts/generate-sbom.sh` invokes `cyclonedx-py` directly. In CI,
the SBOM job runs `uv sync --no-dev` first so `.venv` exists, then
`make sbom` prefers that environment when generating
`sbom-python.cdx.json`. If you change the script, keep the `.venv`
preference so the SBOM reflects the project environment instead of
an ad hoc shell state.

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
