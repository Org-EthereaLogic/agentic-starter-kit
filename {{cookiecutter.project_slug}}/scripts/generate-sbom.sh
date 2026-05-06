#!/usr/bin/env bash
# scripts/generate-sbom.sh — produce a CycloneDX SBOM
#
# Conditional on `include_sbom=yes` at template-render time. The
# post-gen hook removes this script (and its CI job) when the
# option is `no`.
#
# Output:
#   sbom/sbom-python.cdx.json   (Python path / polyglot)
#   sbom/sbom-node.cdx.json     (TypeScript path / polyglot)
#
# Tooling:
#   cyclonedx-py   — install via `pip install cyclonedx-bom`
#   @cyclonedx/cyclonedx-npm — install via
#                    `npm install -g @cyclonedx/cyclonedx-npm`
#
# Per `docs/sbom-policy.md` (Phase 7), the SBOM is regenerated on
# every release and uploaded as a CI artifact.

set -euo pipefail

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

mkdir -p sbom

generated=0

if [[ -f pyproject.toml ]]; then
  if command -v cyclonedx-py >/dev/null 2>&1; then
    # `cyclonedx-py environment` introspects an installed Python
    # environment; the positional argument has to be either a venv
    # directory or an interpreter executable. Passing the project
    # root errors with "Failed to find python in directory: .".
    # Prefer `.venv` when present (created by `make sync` / `uv
    # sync`); otherwise fall back to the current interpreter so
    # the script keeps working in environments where deps live
    # in system Python (some CI runners, Dockerfile builds).
    if [[ -d .venv ]]; then
      cyclonedx-py environment .venv > sbom/sbom-python.cdx.json
    else
      log_warn "no .venv at project root; using the current Python interpreter"
      cyclonedx-py environment > sbom/sbom-python.cdx.json
    fi
    log_ok "SBOM generated: sbom/sbom-python.cdx.json"
    generated=$((generated + 1))
  else
    log_warn "cyclonedx-py not installed; install via 'pip install cyclonedx-bom'"
  fi
fi

if [[ -f package.json ]]; then
  if command -v cyclonedx-npm >/dev/null 2>&1; then
    cyclonedx-npm --output-file sbom/sbom-node.cdx.json
    log_ok "SBOM generated: sbom/sbom-node.cdx.json"
    generated=$((generated + 1))
  else
    log_warn "cyclonedx-npm not installed; install via 'npm install -g @cyclonedx/cyclonedx-npm'"
  fi
fi

if [[ $generated -eq 0 ]]; then
  log_warn "generate-sbom: no SBOM produced (no pyproject.toml or package.json found)"
fi

exit 0
