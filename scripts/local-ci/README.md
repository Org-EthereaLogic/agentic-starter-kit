# Local CI (`scripts/local-ci/`)

A local stand-in for GitHub Actions, for while the org account is
**billing-locked** (every cloud workflow and reviewer — Actions, CodeQL,
CodeRabbit, Codacy, Copilot — fails at job start). It reproduces the
deterministic gates on the host and in OrbStack/Docker, and replaces the cloud
review bots with locally-hosted LLMs via Ollama. It keeps working offline after
billing is restored, as a fast pre-push gate.

This tooling lives at the **repo root** (it validates the *template*); it does
**not** ship into rendered projects.

## Three tiers

| Tier | Command | What it does | Blocking? |
| --- | --- | --- | --- |
| 1 — fast gate | `make local-ci` | `pytest tests/` (Py 3.12 via `uv`) + default cookiecutter render smoke, on the host | yes (exit code) |
| 2 — full matrix | `make ci-orb` | Builds `Dockerfile.ci` and runs the 7-variant cookiecutter **and** copier render matrix + render-equivalence, in Linux. Add `RUN_VALIDATE=1` to also run `make validate` inside each render (opt-in — see note). | yes |
| 3 — LLM review | `make review` | Advisory two-model review (`gpt-oss:120b` deep + `qwen3.5:9b` fast) of `git diff origin/main...HEAD` via Ollama | no — advisory only |

Extra: `make codacy-local` runs the local Codacy CLI (static analysis).

Evidence is written to the gitignored `ci_logs/` directory as append-only JSONL
(`local_ci.jsonl`, `orb_ci.jsonl`, `review.jsonl`) plus per-run `.log` files.
Each run prints a one-line JSON summary to **paste into the PR body** as CI
evidence while cloud checks can't run.

## Prerequisites

- **uv** — `curl -LsSf https://astral.sh/uv/install.sh | sh` (provides Python 3.12).
- **OrbStack** (or Docker) running — for Tier 2. `docker` must be on `PATH`.
- **Ollama** for Tier 3: `ollama serve`, then pull the models once:
  ```sh
  ollama pull gpt-oss:120b     # ~65 GB — needs substantial unified memory
  ollama pull qwen3.5:9b       # ~6.6 GB
  ```
- `jq` and `curl` (Tier 3 host side).

## Usage

```sh
make local-ci                        # Tier 1 — fast pre-push gate
make review                          # Tier 3 — advisory LLM review
make ci-orb                          # Tier 2 — full matrix (minutes; needs network)

# Tier 2 knobs:
VARIANTS_OVERRIDE=python-mit-ty make ci-orb    # one variant, fast
TOOLS_OVERRIDE=cookiecutter make ci-orb        # skip copier legs
RUN_VALIDATE=1 make ci-orb                      # ALSO run `make validate` in each render (opt-in)
ORB_ARCH=amd64 make ci-orb                      # force x86_64 via Rosetta

# Tier 3 knobs:
REVIEW_MODELS="gpt-oss:120b" make review        # single model
REVIEW_BASE=origin/main make review             # diff base

make install-hooks                   # pre-push hook -> runs Tier 1 before every push
```

## Files

| File | Role |
| --- | --- |
| `lib.sh` | shared helpers (run id, JSONL emit, Ollama preflight) — sourced, not run |
| `gate.sh` | Tier 1 host gate |
| `Dockerfile.ci` | Tier 2 image (Python 3.12 + Node 20 + render toolchain) |
| `run-matrix.sh` | Tier 2 body — runs **inside** the container |
| `orb-ci.sh` | Tier 2 host driver — builds the image, runs the container |
| `review.sh` | Tier 3 advisory LLM review |

## Notes

- **`RUN_VALIDATE` default is 0** (the reliable deterministic core: render +
  no-unrendered + shell-identity + YAML + equivalence, across all 7 variants ×
  both tools). `RUN_VALIDATE=1` additionally runs the rendered project's own
  `make validate` in each render. The deep gate originally found four rendered-
  test failures that billing-locked cloud CI never actually ran. #138 fixed
  three (the `generate-sbom.sh` test not gated on `include_sbom`, plus two
  `post-create.sh` `mktemp` cases). #144 fixes the remaining test harness bug:
  its body-only-agent-key test selected the first `*.md` entry without excluding
  `README.md`, which Linux render order returned first even though
  `check-governance.sh` intentionally skips that file. The test now selects a
  deterministic non-README agent and exercises the intended rejection path.
  The subsequent deep-matrix run exposed #147: root-time promptfoo installation
  created root-owned descendants after `/opt/npm-cache` itself was made
  writable. `Dockerfile.ci` now normalizes permissions recursively within that
  cache after priming it, so the unchanged host-UID container can run npm in
  TypeScript and polyglot legs without broader runtime privileges. The same run
  caught two PR #148 cleanup tests whose direct `pytest.skip` calls `ty`
  rejects in both keyword and positional forms. Their template-source-only
  skips now use `@pytest.mark.skipif(..., reason=...)`, matching the accepted
  decorator pattern already in the file without suppressing type errors or
  changing the deep matrix.
- **Offline matrix**: every Tier-2 leg renders with `include_promptfoo=no` so
  `make validate`'s `eval` step (which calls an external LLM provider) is
  skipped. Everything else mirrors cloud CI.
- **Advisory review is not independent verification**: a local model reviewing
  your own diff does not satisfy any independent-verification bar. Treat its
  output as a helpful extra pass, not a sign-off.
