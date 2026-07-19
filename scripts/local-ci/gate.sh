#!/usr/bin/env bash
# gate.sh — TIER 1 local CI: the fast deterministic gate, run on the host.
#
# Blocking (exit 0 iff every step passes). This is the pre-push gate and the
# quick inner-loop check. It reproduces the cheapest, highest-signal slice of
# cloud CI: the repo-root hook test suite and a default cookiecutter render
# smoke. The heavy cross-variant matrix lives in orb-ci.sh (Tier 2); LLM review
# lives in review.sh (Tier 3).
#
# Usage:  make local-ci   (or: bash scripts/local-ci/gate.sh)
# Env:    LOCAL_CI_PYTHON (default 3.12), UV (default uv)
# Evidence: ci_logs/<run_id>.gate.log + a line in ci_logs/local_ci.jsonl.
set -uo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=scripts/local-ci/lib.sh
. "$here/lib.sh"
repo_root="$(cd "$here/../.." && pwd)"
cd "$repo_root" || exit 1
mkdir -p ci_logs

UV="${UV:-uv}"
PYVER="${LOCAL_CI_PYTHON:-3.12}"
run_id="$(ci_run_id)"
commit="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
branch="$(git branch --show-current 2>/dev/null || echo unknown)"
dirty="$(ci_dirty)"
log="ci_logs/${run_id}.gate.log"
: > "$log"

if ! command -v "$UV" >/dev/null 2>&1; then
  echo "[gate] ERROR: '$UV' not on PATH — install uv (https://docs.astral.sh/uv/) or set UV=" >&2
  exit 2
fi

overall=pass
steps=()

run_step() {
  # run_step <name> <cmd...>
  name="$1"; shift
  start=$(date +%s)
  echo "=== [gate] $name ===" >>"$log"
  if "$@" >>"$log" 2>&1; then st=pass; else st=fail; overall=fail; fi
  dur=$(( $(date +%s) - start ))
  echo "[gate] $name -> $(ci_upper "$st") (${dur}s)"
  steps+=("{\"step\":\"$name\",\"status\":\"$st\",\"duration_s\":$dur}")
}

# Step 1 — repo-root hook tests on Python 3.12 (mirrors the cloud
# hook-pruning-test job: pytest tests/ drives hooks/*.py + the guards).
run_step "pytest" "$UV" run --no-project --python "$PYVER" \
  --with cookiecutter --with pytest --with pytest-cov -- \
  pytest tests/ -q

# Step 2 — default cookiecutter render smoke: it renders and leaves no
# unrendered cookiecutter variables behind.
render_smoke() {
  out="$(mktemp -d)"
  if ! "$UV" run --no-project --python "$PYVER" --with cookiecutter -- \
      cookiecutter . --no-input -f -o "$out"; then
    rm -rf "$out"; return 1
  fi
  if grep -rIn '{{[[:space:]]*cookiecutter\.' "$out" 2>/dev/null; then
    echo "unrendered cookiecutter variables found (above)" >&2
    rm -rf "$out"; return 1
  fi
  rm -rf "$out"
}
run_step "render-smoke" render_smoke

legs_json="$(IFS=,; echo "${steps[*]}")"
record="$(printf '{"event":"gate","run_id":"%s","git_commit":"%s","branch":"%s","dirty":%s,"overall":"%s","steps":[%s]}' \
  "$run_id" "$commit" "$branch" "$dirty" "$overall" "$legs_json")"
ci_emit_jsonl ci_logs/local_ci.jsonl "$record"

echo "[gate] overall: $(ci_upper "$overall")  (full log: $log)"
echo "[gate] evidence record (paste into the PR body):"
echo "$record"
[ "$overall" = pass ]
