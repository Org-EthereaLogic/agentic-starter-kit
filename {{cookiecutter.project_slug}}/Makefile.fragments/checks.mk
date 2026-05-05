# Makefile.fragments/checks.mk — Governance and validation checks
#
# `governance-review` is the canonical Python validator (Phase C2,
# issue #20). It emits stable GOV-NNN IDs anchored to docs/STANDARDS.md
# and supports text / JSON / SARIF output. The legacy bash scripts run
# alongside it for now so failures are visible in both formats; remove
# them once downstream automation has migrated to the GOV-NNN IDs.

.PHONY: marker-scan governance-check check-traceability check-doc-drift governance-review

# Resolve the validator: prefer an installed `governance-review` (e.g.
# `uv tool install ./scripts/governance_review`); otherwise fall back
# to the in-tree package via `python3 -m governance_review` with
# `PYTHONPATH` pointing at the package source.
GOVERNANCE_REVIEW ?= $(shell command -v governance-review 2>/dev/null)
ifeq ($(GOVERNANCE_REVIEW),)
GOVERNANCE_REVIEW := PYTHONPATH=scripts/governance_review python3 -m governance_review
endif

governance-review:
	@$(GOVERNANCE_REVIEW)

marker-scan:
	@bash scripts/marker-scan.sh

governance-check:
	@bash scripts/check-governance.sh

check-traceability:
	@bash scripts/check-traceability.sh

check-doc-drift:
	@bash scripts/check-doc-drift.sh
