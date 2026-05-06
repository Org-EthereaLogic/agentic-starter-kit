#!/usr/bin/env bash
# scripts/check-action-pins.sh — enforce IMP-006
#
# Walks every workflow file under .github/workflows/ and flags
# `uses:` lines that are not SHA-pinned. A SHA-pinned `uses:` looks
# like:
#
#   uses: owner/repo@<40-char-lowercase-hex> # v<semver>
#
# Anything else — `@v4`, `@main`, `@latest`, a 7-char short SHA — is
# a float pin and counts as supply-chain attack surface per
# DIRECTIVES.md §IMP-006.
#
# Soft-fail by default: prints WARN findings and exits 0 so
# `make validate` stays green. CI surfaces the warnings without
# breaking the gate. Set `STRICT=1` (or `--strict`) to exit non-zero
# on any finding — useful from a pre-merge GitHub check that should
# block until pins are tightened.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"

WORKFLOW_DIR=".github/workflows"
SCRIPT_NAME="check-action-pins"

strict=${STRICT:-0}
for arg in "$@"; do
  case "$arg" in
    --strict) strict=1 ;;
    --soft) strict=0 ;;
    -h|--help)
      cat <<USAGE
Usage: $SCRIPT_NAME [--strict|--soft]

Flags float-pinned GitHub Actions \`uses:\` lines under $WORKFLOW_DIR.
Default mode is soft (exit 0 on findings). Pass --strict (or set
STRICT=1) to exit 1 on any finding.
USAGE
      exit 0
      ;;
  esac
done

if [[ ! -d "$WORKFLOW_DIR" ]]; then
  log_info "no $WORKFLOW_DIR directory; nothing to check"
  exit 0
fi

# Discover workflow files. `.yaml` is rare but valid. `mapfile` is
# Bash 4+ and macOS still ships 3.2, so collect via a portable loop.
workflows=()
while IFS= read -r f; do
  workflows+=("$f")
done < <(find "$WORKFLOW_DIR" -maxdepth 1 -type f \( -name '*.yml' -o -name '*.yaml' \) | sort)

if [[ ${#workflows[@]} -eq 0 ]]; then
  log_info "no workflow files under $WORKFLOW_DIR"
  exit 0
fi

# Match a SHA-pinned uses line:
#   uses: owner/repo[/path]@<40-hex> [# comment]
# The 40-char lowercase hex is the contract. Capture it loosely so
# we can identify the owner/action for reporting; the strict shape
# check is the second regex.
sha_pin='@[0-9a-f]{40}([[:space:]]|$|#)'

# Local actions (`./` or `docker://`) and reusable workflows
# (`.github/workflows/foo.yml`) are not SHA-pinned in the same way
# and are excluded from the check.
skip_prefix='^(./|docker://|/)'

findings=0
for wf in "${workflows[@]}"; do
  # Extract `uses:` lines with their line numbers; trim leading
  # whitespace and the `uses:` keyword to leave just the reference.
  while IFS=: read -r lineno raw; do
    # Strip leading whitespace and "uses:" prefix.
    ref="${raw#"${raw%%[![:space:]]*}"}"
    ref="${ref#uses:}"
    ref="${ref#"${ref%%[![:space:]]*}"}"
    # Drop trailing comment for the shape check (but we still want
    # the user to see the original line in the finding).
    bare="${ref%%#*}"
    bare="${bare%"${bare##*[![:space:]]}"}"

    # Skip local / docker / reusable refs.
    if [[ "$bare" =~ $skip_prefix ]]; then
      continue
    fi

    # If the reference matches the SHA-pinned shape, accept.
    if [[ "$bare" =~ $sha_pin ]]; then
      continue
    fi

    findings=$((findings + 1))
    log_warn "$wf:$lineno  float-pinned action: $bare"
  done < <(grep -nE '^[[:space:]]+uses:[[:space:]]+[^[:space:]]+' "$wf" || true)
done

if [[ $findings -eq 0 ]]; then
  log_ok "$SCRIPT_NAME (${#workflows[@]} workflow file(s) scanned)"
  exit 0
fi

echo
echo "$SCRIPT_NAME: $findings float-pinned reference(s) found." >&2
echo "Per IMP-006, every \`uses:\` line should pin to a 40-char" >&2
echo "commit SHA with a trailing \`# v<x>.<y>\` comment." >&2
echo "Run with --strict (or STRICT=1) to fail the gate on findings." >&2

if [[ "$strict" == "1" ]]; then
  exit 1
fi
exit 0
