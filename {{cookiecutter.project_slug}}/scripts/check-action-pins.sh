#!/usr/bin/env bash
# scripts/check-action-pins.sh — enforce IMP-006
#
# Walks every workflow file under .github/workflows/ and flags
# `uses:` lines that are not SHA-pinned. A SHA-pinned `uses:` looks
# like:
#
#   uses: owner/repo@<40-char-hex> # v<version>
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
# shellcheck disable=SC1091
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
workflow_count=0
while IFS= read -r f; do
  workflows+=("$f")
  workflow_count=$((workflow_count + 1))
done < <(find "$WORKFLOW_DIR" -maxdepth 1 -type f \( -name '*.yml' -o -name '*.yaml' \) | sort)

if [[ $workflow_count -eq 0 ]]; then
  log_info "no workflow files under $WORKFLOW_DIR"
  exit 0
fi

# Match a SHA-pinned uses line:
#   uses: owner/repo[/path]@<40-hex> with an optional trailing comment
# The 40-char hex is the contract. Capture it loosely so
# we can identify the owner/action for reporting; the strict shape
# check is the second regex.
sha_pin='@[0-9A-Fa-f]{40}([[:space:]]|$|#)'

# Local actions (`./`), Docker action refs (`docker://`), and absolute
# paths are not third-party GitHub Action refs and are excluded.
skip_prefix='^(./|docker://|/)'

# Tag-pinned exceptions. The SLSA generator reusable workflow MUST
# be referenced by a semver tag and not by a commit SHA: the trusted
# reusable-workflow signature is anchored to the tag, not the
# underlying commit, so a SHA pin would silently break SLSA L3
# attestation.
# See: https://github.com/slsa-framework/slsa-github-generator/blob/main/RUNNERS.md
allow_tag_pin='^slsa-framework/slsa-github-generator(/|@)'

findings=0
for wf in "${workflows[@]}"; do
  # Extract `uses:` lines with their line numbers; trim leading
  # whitespace and the `uses:` keyword to leave just the reference.
  while IFS=: read -r lineno raw; do
    # Strip everything through "uses:" so inline list items such as
    # `- uses:` and mapping entries parse the same way.
    ref="${raw#*uses:}"
    ref="${ref#"${ref%%[![:space:]]*}"}"
    # Drop trailing comment for the shape check (but we still want
    # the user to see the original line in the finding).
    bare="${ref%%#*}"
    bare="${bare%"${bare##*[![:space:]]}"}"
    bare="${bare#"${bare%%[![:space:]]*}"}"

    leading_quote="${bare:0:1}"
    if [[ ( "$leading_quote" == '"' || "$leading_quote" == "'" ) && "${bare: -1}" == "$leading_quote" ]]; then
      bare="${bare#?}"
      bare="${bare%?}"
    fi

    # Skip local, Docker, and absolute-path refs.
    if [[ "$bare" =~ $skip_prefix ]]; then
      continue
    fi

    # Allow upstream-mandated tag pins (SLSA generator).
    if [[ "$bare" =~ $allow_tag_pin ]]; then
      continue
    fi

    # If the reference matches the SHA-pinned shape, accept.
    if [[ "$bare" =~ $sha_pin ]]; then
      continue
    fi

    findings=$((findings + 1))
    log_warn "$wf:$lineno  float-pinned action: $bare"
  done < <(grep -nE '^[[:space:]]*(-[[:space:]]*)?uses:[[:space:]]+[^[:space:]]+' "$wf" || true)
done

if [[ $findings -eq 0 ]]; then
  log_ok "$SCRIPT_NAME ($workflow_count workflow file(s) scanned)"
  exit 0
fi

echo
echo "$SCRIPT_NAME: $findings float-pinned reference(s) found." >&2
echo "Per IMP-006, every third-party \`uses:\` line should pin" >&2
echo "to a 40-char commit SHA." >&2
echo "Run with --strict (or STRICT=1) to fail the gate on findings." >&2

if [[ "$strict" == "1" ]]; then
  exit 1
fi
exit 0
