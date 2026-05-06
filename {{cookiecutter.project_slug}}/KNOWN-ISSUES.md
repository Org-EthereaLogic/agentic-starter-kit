# Known Issues — {{ cookiecutter.project_name }}

Things you will hit on a fresh build that the toolchain does not
mechanically prevent. Read this once at scaffold time and again
the first time `make validate` or your initial CI run surprises
you.

---

## First CI run

### Required repo secrets

The CI workflow ships with three jobs that need tokens you have
not set yet. The jobs fail loudly on the first push; they pass
once the secrets are configured.

| Job | Secret | Where to get it |
| --- | --- | --- |
| `codacy` | `CODACY_PROJECT_TOKEN` | Codacy → your repo → *Settings → Integrations → Project API* |
| `snyk` | `SNYK_TOKEN` | <https://app.snyk.io/account> → *Auth Token* |
| `coverage` | `CODECOV_TOKEN` | Codecov → repo settings (still required for **public** repos in 2026) |

Add at **GitHub → Settings → Secrets and variables → Actions →
New repository secret**. Then *Re-run failed jobs* on the affected
workflow run.

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

`scripts/generate-sbom.sh` invokes `cyclonedx-py` via
`uv run --no-sync`, which keeps it inside the venv that
`make sync` already populated. Earlier kit revisions invoked the
tool from a fresh process and tripped on PEP 735 dep-groups; that
is now fixed. If you change the script, keep the `uv run`
prefix — running `cyclonedx-py` from outside the venv may
re-surface the failure on `[dependency-groups]` projects.

---

## macOS local dev

### Bash 3.2

Apple ships Bash 3.2 (frozen at the GPLv2 line) and never upgrades
it. Several governance scripts use Bash 4+ associative arrays.
Each one degrades gracefully — `make validate` will print a
WARN and continue — but the affected check effectively skips on
the system Bash.

Recommendation: install Homebrew bash and put it on PATH ahead of
`/bin/bash`:

```bash
brew install bash
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
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
Node 20+ is required. The target prints a soft WARN if Node is
missing or older — it does not fail the target — so `nvm`-managed
shells that haven't activated yet still produce a useful
diagnostic instead of `node: not found`.

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

Astral's `ty` is the 2026 default. Choose `python_typechecker=mypy`
at scaffold time if you need an established stub-heavy ecosystem
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
