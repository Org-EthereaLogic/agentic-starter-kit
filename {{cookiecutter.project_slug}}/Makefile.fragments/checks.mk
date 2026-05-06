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
# uses the in-tree package when Python is available so validation runs
# against the committed rule set.
GOVERNANCE_REVIEW_PYTHON ?= $(shell command -v python3 2>/dev/null || command -v python 2>/dev/null)
ifeq ($(strip $(GOVERNANCE_REVIEW)),)
ifneq ($(strip $(GOVERNANCE_REVIEW_PYTHON)),)
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

# IMP-006 — float-pinned `uses:` references in workflow files. Soft
# by default (warn-only) so this can land without churning every
# workflow at once; pass `STRICT=1` to fail the gate on any finding.
check-action-pins:
	@bash scripts/check-action-pins.sh
