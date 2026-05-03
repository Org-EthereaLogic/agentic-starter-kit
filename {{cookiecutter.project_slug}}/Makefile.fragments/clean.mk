# Makefile.fragments/clean.mk — Build artifact cleanup

.PHONY: clean

clean:
	@rm -rf .pytest_cache .mypy_cache .ty_cache .ruff_cache .coverage htmlcov
	@find . -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null || true
	@find . -name '*.pyc' -delete 2>/dev/null || true
	@rm -rf node_modules dist build
	@rm -rf sbom
	@echo "clean: complete"
