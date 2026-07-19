#!/usr/bin/env bash
# orb-ci.sh — TIER 2 host driver: build Dockerfile.ci and run the render matrix
# (run-matrix.sh) inside an OrbStack/Docker container, with the repo bind-mounted
# at /repo. Running in Linux avoids the macOS bash-3.2 breakage in some rendered
# scripts. Blocking (exit 0 iff every matrix leg passes).
#
# Usage:  make ci-orb   (or: bash scripts/local-ci/orb-ci.sh)
# Env:    ORB_ARCH (default host arch; set amd64 to force Rosetta),
#         RUN_VALIDATE (default 0 = deterministic core; 1 = also run each
#         render's `make validate`), TOOLS_OVERRIDE, VARIANTS_OVERRIDE (passed
#         through to run-matrix.sh).
# Evidence: ci_logs/<run_id>.orb.log + records in ci_logs/orb_ci.jsonl.
set -uo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=scripts/local-ci/lib.sh
. "$here/lib.sh"
repo_root="$(cd "$here/../.." && pwd)"
cd "$repo_root" || exit 1
mkdir -p ci_logs

command -v docker >/dev/null 2>&1 || {
  echo "[orb-ci] ERROR: docker/OrbStack not found on PATH (start OrbStack)" >&2; exit 2; }

run_id="$(ci_run_id)"
commit="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
branch="$(git branch --show-current 2>/dev/null || echo unknown)"
ARCH="${ORB_ARCH:-$(uname -m)}"
case "$ARCH" in
  arm64|aarch64) platform=linux/arm64 ;;
  x86_64|amd64)  platform=linux/amd64 ;;
  *)             platform="linux/$ARCH" ;;
esac
tag="agentic-starter-kit-localci:${ARCH}"
log="ci_logs/${run_id}.orb.log"
: > "$log"

# Build with the tiny scripts/local-ci/ dir as context (Dockerfile.ci has no
# COPY) so the 294 MB gitignored artifacts/ tree isn't uploaded as build context.
echo "[orb-ci] building $tag ($platform)..."
if ! docker build --platform "$platform" -t "$tag" \
      -f scripts/local-ci/Dockerfile.ci scripts/local-ci >>"$log" 2>&1; then
  echo "[orb-ci] ERROR: image build failed (see $log)" >&2
  tail -n 20 "$log" >&2
  exit 1
fi
img="$(docker image inspect -f '{{.Id}}' "$tag" 2>/dev/null)"

echo "[orb-ci] running matrix in container (RUN_VALIDATE=${RUN_VALIDATE:-0})..."
start=$(date +%s); st=pass
docker run --rm --platform "$platform" --user "$(id -u):$(id -g)" \
  -e HOME=/tmp -e USER=orb-ci \
  -e RUN_ID="$run_id" \
  -e RUN_VALIDATE="${RUN_VALIDATE:-0}" \
  -e TOOLS_OVERRIDE="${TOOLS_OVERRIDE:-}" \
  -e VARIANTS_OVERRIDE="${VARIANTS_OVERRIDE:-}" \
  -v "$repo_root":/repo -w /repo \
  "$tag" >>"$log" 2>&1 || st=fail
dur=$(( $(date +%s) - start ))

record="$(printf '{"event":"orb_ci","run_id":"%s","git_commit":"%s","branch":"%s","platform":"%s","image":"%s","image_digest":"%s","duration_s":%d,"overall":"%s","log":"%s"}' \
  "$run_id" "$commit" "$branch" "$platform" "$tag" "$img" "$dur" "$st" "$log")"
ci_emit_jsonl ci_logs/orb_ci.jsonl "$record"

echo "[orb-ci] overall: $(ci_upper "$st")  (${dur}s, log: $log)"
echo "[orb-ci] evidence record (paste into the PR body; matrix legs in ci_logs/orb_ci.jsonl):"
echo "$record"
[ "$st" = pass ]
