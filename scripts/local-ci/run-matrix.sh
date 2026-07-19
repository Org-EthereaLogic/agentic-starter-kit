#!/usr/bin/env bash
# run-matrix.sh — runs INSIDE Dockerfile.ci (Linux, bash 5). Reproduces the
# deterministic core of .github/workflows/template-smoke-test.yml: the repo-root
# hook tests, the cookiecutter + copier render matrix (7 variants), and the
# render-equivalence diff. Invoked by orb-ci.sh; prints a JSONL summary.
#
# Env:
#   TOOLS_OVERRIDE     subset of "cookiecutter copier" (default both)
#   VARIANTS_OVERRIDE  space-separated variant-name substrings (default all 7)
#   RUN_VALIDATE       0 (default) = the reliable deterministic core: render +
#                      no-unrendered + shell-identity + YAML + equivalence.
#                      1 = also run `make sync`/`npm install` + `make validate` +
#                      governance.py inside each render (the rendered project's
#                      own full test suite). Opt-in because it currently surfaces
#                      pre-existing rendered-test failures that billing-locked
#                      cloud CI never caught (tracked separately).
#
# The matrix renders from a CLEAN CLONE of HEAD (matching cloud CI's fresh
# checkout): the bind-mounted working tree carries an untracked, gitignored
# artifacts/ directory full of nested render repos that trips copier's
# dirty-tree git handling. `git clone` takes only tracked files + history, so
# copier --vcs-ref HEAD works and the matrix reflects the committed HEAD.
#
# Offline note: every leg renders with include_promptfoo=no so `make validate`'s
# `eval` step (which calls an external LLM provider) is skipped.
set -uo pipefail

bind_root="/repo"
[ -d "$bind_root/.git" ] || bind_root="$(cd "$(dirname "$0")/../.." && pwd)"
git config --global --add safe.directory '*' 2>/dev/null || true

# Evidence persists to the bind-mounted repo so the host keeps it.
CI_LOGS="$bind_root/ci_logs"; mkdir -p "$CI_LOGS"
run_id="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
commit="$(git -C "$bind_root" rev-parse HEAD 2>/dev/null || echo unknown)"
TOOLS="${TOOLS_OVERRIDE:-cookiecutter copier}"
RUN_VALIDATE="${RUN_VALIDATE:-0}"
TEMPLATE_SUBDIR="{{cookiecutter.project_slug}}"

# Clean clone of HEAD (no untracked artifacts/, no dirty-tree path).
SRC="$(mktemp -d)/src"
git clone --quiet --depth 1 "$bind_root" "$SRC" || { echo "[matrix] ERROR: clone failed" >&2; exit 1; }
cd "$SRC" || exit 1

# name|render vars (include_promptfoo=no => offline; see header).
VARIANTS=(
"python-mit-ty|primary_language=python python_typechecker=ty license=MIT include_sbom=no include_codacy=no include_snyk=no include_promptfoo=no"
"python-mit-mypy|primary_language=python python_typechecker=mypy license=MIT include_sbom=no include_promptfoo=no"
"python-apache-sbom-ty|primary_language=python python_typechecker=ty license=Apache-2.0 include_sbom=yes include_promptfoo=no"
"typescript-mit|primary_language=typescript license=MIT include_sbom=no include_promptfoo=no"
"typescript-apache-tools|primary_language=typescript license=Apache-2.0 include_sbom=yes include_codacy=yes include_snyk=yes include_promptfoo=no"
"polyglot-mit-all-ty|primary_language=polyglot python_typechecker=ty license=MIT include_sbom=yes include_codacy=yes include_snyk=yes include_promptfoo=no"
"polyglot-mit-all-macaron-mypy|primary_language=polyglot python_typechecker=mypy license=MIT include_sbom=yes include_codacy=yes include_snyk=yes include_macaron=yes include_promptfoo=no"
)

overall=pass
results=()
log="$CI_LOGS/${run_id}.matrix.log"
: > "$log"

selected() {
  [ -z "${VARIANTS_OVERRIDE:-}" ] && return 0
  local n
  for n in $VARIANTS_OVERRIDE; do case "$1" in *"$n"*) return 0;; esac; done
  return 1
}

check_no_unrendered() {
  local dir="$1"
  if grep -rIn '{{[[:space:]]*cookiecutter\.' "$dir" 2>/dev/null; then return 1; fi
  if grep -rIn '{{[[:space:]]*_copier' "$dir" --exclude='.copier-answers.yml' 2>/dev/null; then return 1; fi
  return 0
}

check_shell_identity() {
  # Rendered scripts/*.sh must be byte-identical to the template source.
  local dir="$1" script rel
  while IFS= read -r script; do
    rel="${script#"$dir"/}"
    diff -u "$SRC/$TEMPLATE_SUBDIR/$rel" "$script" || return 1
  done < <(find "$dir/scripts" -type f -name '*.sh' 2>/dev/null | sort)
  return 0
}

check_workflow_yaml() {
  local dir="$1" wf
  for wf in scorecards release supply-chain; do
    [ -f "$dir/.github/workflows/$wf.yml" ] || continue
    python3 -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]))" \
      "$dir/.github/workflows/$wf.yml" || return 1
  done
  return 0
}

validate_render() {
  # &&-chained (NOT `set -e`): a subshell's `set -e` is suppressed when the
  # subshell is on the left of `|| st=fail` (POSIX), which silently masked a
  # failing `make validate`. An && chain propagates the first failure's exit
  # code regardless, so the leg fails honestly.
  local dir="$1" lang="$2" dep="make sync"
  [ "$lang" = "typescript" ] && dep="npm install --no-audit --no-fund"
  ( cd "$dir" \
    && git init -q && git config user.email ci@local && git config user.name ci \
    && git checkout -q -b feat/initial \
    && $dep \
    && make validate \
    && python3 scripts/lib/governance.py --validate )
}

render_cookiecutter() { local out="$1"; shift; cookiecutter . --no-input -f --output-dir "$out" $@ >/dev/null || return 1; echo "$out/my-agentic-project"; }
render_copier() {
  local out="$1"; shift; local dargs="" kv
  for kv in $@; do dargs="$dargs -d $kv"; done
  # shellcheck disable=SC2086
  copier copy --trust --defaults --vcs-ref HEAD $dargs . "$out" >/dev/null || return 1
  echo "$out"
}

run_leg() {
  local tool="$1" name="$2"; shift 2
  local vars="$*" lang out rendered st start dur
  lang="python"; case "$vars" in *primary_language=typescript*) lang=typescript;; *primary_language=polyglot*) lang=polyglot;; esac
  start=$(date +%s); st=pass
  out="$(mktemp -d)"
  echo "=== [matrix] $tool / $name ($lang) ===" >>"$log"
  {
    if [ "$tool" = cookiecutter ]; then rendered="$(render_cookiecutter "$out" $vars)"; else rendered="$(render_copier "$out" $vars)"; fi
  } >>"$log" 2>&1 || st=fail
  if [ "$st" = pass ]; then
    check_no_unrendered "$rendered" >>"$log" 2>&1 || st=fail
    check_shell_identity "$rendered" >>"$log" 2>&1 || st=fail
    check_workflow_yaml  "$rendered" >>"$log" 2>&1 || st=fail
    if [ "$st" = pass ] && [ "$RUN_VALIDATE" = 1 ]; then
      validate_render "$rendered" "$lang" >>"$log" 2>&1 || st=fail
    fi
  fi
  [ "$st" = fail ] && overall=fail
  dur=$(( $(date +%s) - start ))
  echo "[matrix] $tool / $name -> $(printf '%s' "$st" | tr '[:lower:]' '[:upper:]') (${dur}s)"
  results+=("$(jq -nc --arg tool "$tool" --arg name "$name" --arg lang "$lang" \
    --arg status "$st" --argjson dur "$dur" \
    '{tool:$tool, variant:$name, language:$lang, status:$status, duration_s:$dur}')")
  rm -rf "$out"
}

# --- Step 0: repo-root hook tests (mirrors hook-pruning-test job) -------------
hp_start=$(date +%s); hp=pass
echo "=== [matrix] pytest tests/ ===" >>"$log"
python3 -m pytest tests/ -q >>"$log" 2>&1 || { hp=fail; overall=fail; }
echo "[matrix] pytest tests/ -> $(printf '%s' "$hp" | tr '[:lower:]' '[:upper:]') ($(( $(date +%s) - hp_start ))s)"
results+=("$(jq -nc --arg status "$hp" '{step:"pytest", status:$status}')")

# --- Step 1: render matrix ----------------------------------------------------
for entry in "${VARIANTS[@]}"; do
  name="${entry%%|*}"; vars="${entry#*|}"
  selected "$name" || continue
  for tool in $TOOLS; do
    case " $TOOLS " in *" $tool "*) run_leg "$tool" "$name" $vars;; esac
  done
done

# --- Step 2: render-equivalence (default variant, both tools) -----------------
case "$TOOLS" in *cookiecutter*copier*|*copier*cookiecutter*)
  eq_start=$(date +%s); eq=pass
  cc="$(mktemp -d)"; co="$(mktemp -d)"
  echo "=== [matrix] render-equivalence ===" >>"$log"
  {
    cookiecutter . --no-input -f --output-dir "$cc" >/dev/null &&
    copier copy --trust --defaults --vcs-ref HEAD . "$co" >/dev/null &&
    diff -rq --exclude='.copier-answers.yml' "$cc/my-agentic-project" "$co"
  } >>"$log" 2>&1 || { eq=fail; overall=fail; }
  echo "[matrix] render-equivalence -> $(printf '%s' "$eq" | tr '[:lower:]' '[:upper:]') ($(( $(date +%s) - eq_start ))s)"
  results+=("$(jq -nc --arg status "$eq" '{step:"render-equivalence", status:$status}')")
  rm -rf "$cc" "$co"
;; esac

legs_json="[$(IFS=,; echo "${results[*]}")]"
record="$(jq -nc --arg run_id "$run_id" --arg commit "$commit" \
  --arg overall "$overall" --arg run_validate "$RUN_VALIDATE" \
  --argjson legs "$legs_json" \
  '{event:"orb_matrix", run_id:$run_id, git_commit:$commit, run_validate:$run_validate, overall:$overall, legs:$legs}')"
printf '%s\n' "$record" >> "$CI_LOGS/orb_ci.jsonl"
echo "[matrix] overall: $(printf '%s' "$overall" | tr '[:lower:]' '[:upper:]')  (full log: $log)"
echo "$record"
[ "$overall" = pass ]
