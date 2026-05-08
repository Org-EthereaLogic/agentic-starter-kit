# Makefile.fragments/checks.mk — Governance and validation checks
#
# `governance-review` is the canonical Python validator (Phase C2,
# issue #20). It emits stable GOV-NNN IDs anchored to docs/STANDARDS.md
# and supports text / JSON / SARIF output. The legacy bash scripts run
# alongside it for now so failures are visible in both formats; remove
# them once downstream automation has migrated to the GOV-NNN IDs.

.PHONY: marker-scan governance-check check-traceability check-doc-drift check-action-pins governance-review

# Resolve the validator deterministically from the checked-in source.
# A caller may still override `GOVERNANCE_REVIEW=...`, but the default
# routes through `uv run` when uv is available so the validator picks
# up the project's pinned Python (the validator requires 3.11+) rather
# than whatever `python3` happens to resolve to on the system PATH.
GOVERNANCE_REVIEW_PYTHON ?= $(shell command -v python3 2>/dev/null || command -v python 2>/dev/null)
ifeq ($(strip $(GOVERNANCE_REVIEW)),)
ifeq ($(HAS_UV),yes)
GOVERNANCE_REVIEW := PYTHONPATH=scripts/governance_review uv run --quiet python -m governance_review
else ifneq ($(strip $(GOVERNANCE_REVIEW_PYTHON)),)
GOVERNANCE_REVIEW := PYTHONPATH=scripts/governance_review $(GOVERNANCE_REVIEW_PYTHON) -m governance_review
endif
endif

governance-review:

ifeq ($(strip $(GOVERNANCE_REVIEW)),)
	@echo "governance-review: skipped (no Python interpreter found; legacy bash checks still run)"
else
	@$(GOVERNANCE_REVIEW)
endif

marker-scan:
	@bash scripts/marker-scan.sh

governance-check:
	@bash scripts/check-governance.sh

check-traceability:
	@bash scripts/check-traceability.sh

check-doc-drift:
	@bash scripts/check-doc-drift.sh

# IMP-006 — float-pinned `uses:` references in workflow files. Now
# strict by default — every shipped workflow is SHA-pinned and the
# template enforces that any new `uses:` line follows suit. Pass
# `STRICT=0` (or run the script with `--soft`) to opt into a
# warn-only mode while iterating on a new workflow.
check-action-pins:
	@bash scripts/check-action-pins.sh --strict
