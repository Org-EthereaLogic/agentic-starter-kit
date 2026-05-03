# Makefile.fragments/quality.mk — Optional quality tool targets

{% if cookiecutter.include_sbom == "yes" %}.PHONY: sbom

sbom:
	@bash scripts/generate-sbom.sh

{% endif %}{% if cookiecutter.include_codacy == "yes" %}.PHONY: codacy-local

codacy-local:
	@if command -v codacy-cli >/dev/null 2>&1; then \
		codacy-cli analyze; \
	else \
		echo "WARN: codacy-cli not installed; see https://github.com/codacy/codacy-analysis-cli"; \
	fi

{% endif %}{% if cookiecutter.include_snyk == "yes" %}.PHONY: snyk-local

snyk-local:
	@if command -v snyk >/dev/null 2>&1; then \
		snyk test; \
	else \
		echo "WARN: snyk CLI not installed; install via 'npm install -g snyk'"; \
	fi

{% endif %}