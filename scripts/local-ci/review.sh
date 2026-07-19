#!/usr/bin/env bash
# review.sh — TIER 3 local CI: ADVISORY multi-model LLM review of the branch diff.
#
# Fills the cloud-reviewer vacuum (CodeRabbit / Codacy / Copilot) while GitHub
# Actions is billing-locked. NEVER blocks and is NOT independent confirmation —
# a local model reviewing your own diff is operational, non-citable evidence in
# gitignored ci_logs/. The blocking verdict is Tier 1 (gate.sh) / Tier 2
# (orb-ci.sh); this only adds a second pair of eyes.
#
# Runs each model in REVIEW_MODELS against `git diff <base>...HEAD`.
#   Deep:  gpt-oss:120b   (correctness / security)
#   Fast:  qwen3.5:9b     (quick triage)
#
# Usage:  make review   (or: bash scripts/local-ci/review.sh)
# Env:    REVIEW_MODELS (default "gpt-oss:120b qwen3.5:9b"), OLLAMA_HOST
#         (default http://localhost:11434), REVIEW_BASE (default origin/main),
#         REVIEW_MAX_BYTES (default 100000).
# Exit:   0 always (advisory), except 3 if Ollama is unreachable.
set -uo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=scripts/local-ci/lib.sh
. "$here/lib.sh"
repo_root="$(cd "$here/../.." && pwd)"
cd "$repo_root" || exit 1
mkdir -p ci_logs

OLLAMA="${OLLAMA_HOST:-http://localhost:11434}"
MODELS="${REVIEW_MODELS:-gpt-oss:120b qwen3.5:9b}"
BASE="${REVIEW_BASE:-origin/main}"
MAX_BYTES="${REVIEW_MAX_BYTES:-100000}"
run_id="$(ci_run_id)"
commit="$(git rev-parse HEAD)"
branch="$(git branch --show-current)"

for dep in curl jq; do
  command -v "$dep" >/dev/null 2>&1 || { echo "[review] ERROR: '$dep' required" >&2; exit 2; }
done
if ! ci_ollama_up "$OLLAMA"; then
  echo "[review] ERROR: Ollama not reachable at $OLLAMA (start it with: ollama serve)" >&2
  exit 3
fi

diff="$(git diff "${BASE}...HEAD" 2>/dev/null)"
stat="$(git diff --shortstat "${BASE}...HEAD" 2>/dev/null)"
if [ -z "$diff" ]; then
  echo "[review] empty diff vs $BASE — nothing to review."
  exit 0
fi
note=""
if [ "${#diff}" -gt "$MAX_BYTES" ]; then
  diff="$(printf '%s' "$diff" | head -c "$MAX_BYTES")"
  note=" [DIFF TRUNCATED to ${MAX_BYTES} bytes]"
fi

# Prompt tuned for THIS repo: a cookiecutter/copier project template.
prompt="You are a senior code reviewer for a cookiecutter/copier PROJECT TEMPLATE
repository. The repo root is the template source; files under
{{cookiecutter.project_slug}}/ render into generated projects, so Jinja/
cookiecutter syntax in them is intentional. Review this git diff for:
- correctness bugs and security issues;
- broken Jinja or cookiecutter variables/conditionals, and any unrendered '{{ ... }}';
- cookiecutter<->copier prune PARITY: hooks/post_gen_project.py (prune_language_files,
  _prune_variants) must stay aligned with copier.yml _tasks and hooks/_prune_pyproject.py;
- the copier _envops pitfall: a literal '[#' (e.g. a markdown [#NNN] link) breaks copier
  renders, but ONLY inside {{cookiecutter.project_slug}}/. copier.yml sets _subdirectory to
  that tree, so repo-root files (CHANGELOG.md, docs/**, README.md, AGENTS.md) are never
  rendered and '[#NNN]' links there are correct and expected -- docs/PROJECT_DASHBOARD.md
  alone already carries 65 of them. Do NOT flag '[#' outside the template tree; the guard
  test tests/test_no_copier_comment_collision.py scans only the template tree for this reason;
- governance / CRIT-NNN rules and shell portability (macOS bash 3.2 vs bash 4+).
Be concise and specific, citing file + hunk. If nothing is wrong, say so briefly.
Diff stat:${stat}${note}

${diff}"

results=()
reviewed=0
for MODEL in $MODELS; do
  if ! ci_ollama_has_model "$OLLAMA" "$MODEL"; then
    echo "[review] SKIP '$MODEL' (not pulled; run: ollama pull $MODEL)" >&2
    results+=("$(jq -nc --arg m "$MODEL" '{model:$m, status:"skipped_not_pulled"}')")
    continue
  fi
  echo "[review] querying $MODEL (this can take a while for large models)..."
  content="$(jq -n --arg m "$MODEL" --arg c "$prompt" \
      '{model:$m, stream:false, messages:[{role:"user", content:$c}]}' \
    | curl -sf "$OLLAMA/api/chat" -d @- \
    | jq -r '.message.content // "[review] (no content returned)"')"
  safe_model="$(printf '%s' "$MODEL" | tr '/:' '__')"
  log="ci_logs/${run_id}.${safe_model}.review.log"
  { echo "run_id: $run_id"; echo "commit: $commit"; echo "branch: $branch"
    echo "base:   $BASE"; echo "model:  $MODEL"; echo "diffstat:${stat}${note}"
    echo; echo "$content"; } | tee "$log"
  results+=("$(jq -nc --arg m "$MODEL" --arg l "$log" '{model:$m, status:"reviewed", log:$l}')")
  reviewed=$(( reviewed + 1 ))
done

models_json="[$(IFS=,; echo "${results[*]}")]"
record="$(jq -nc \
  --arg run_id "$run_id" --arg commit "$commit" --arg branch "$branch" \
  --arg base "$BASE" --arg diff_stat "${stat}${note}" \
  --argjson reviewed "$reviewed" --argjson models "$models_json" \
  '{event:"review", run_id:$run_id, git_commit:$commit, branch:$branch,
    base:$base, diff_stat:$diff_stat, reviewed:$reviewed, models:$models}')"
ci_emit_jsonl ci_logs/review.jsonl "$record"

echo "[review] recorded $reviewed model review(s) — advisory only, never blocks."
exit 0
