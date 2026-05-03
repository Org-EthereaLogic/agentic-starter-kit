# Makefile.fragments/checks.mk — Governance and validation checks

.PHONY: marker-scan governance-check check-traceability check-doc-drift

marker-scan:
	@bash scripts/marker-scan.sh

governance-check:
	@bash scripts/check-governance.sh

check-traceability:
	@bash scripts/check-traceability.sh

check-doc-drift:
	@bash scripts/check-doc-drift.sh
