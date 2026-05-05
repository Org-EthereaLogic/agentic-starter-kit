# governance-review

Machine-readable validator for the five-layer agentic governance scaffold.
Inspired by [`sp-repo-review`](https://github.com/scientific-python/cookie):
each check has a stable `GOV-NNN` ID anchored to a section of
`docs/STANDARDS.md`, so failures point readers directly at the rule.

## Install

From the rendered project root:

```sh
uv tool install ./scripts/governance_review
```

This makes `governance-review` available on `PATH`. Without installing,
the package can be run from a checkout via `python -m governance_review`
(set `PYTHONPATH=scripts/governance_review`).

## Run

```sh
governance-review                    # text output, exit 1 on errors only
governance-review --warnings-as-errors # promote warnings to exit 1
governance-review --format json      # JSON object with tool metadata + findings
governance-review --format sarif     # SARIF 2.1.0 log for CI/code-scanning
governance-review --list-checks      # show every GOV-NNN, title, anchor
governance-review --root <path>      # scan a different project directory
```

## Check inventory

`governance-review --list-checks` is the source of truth. The IDs map
1:1 to the bash validators they replace:

| ID | Replaces | Subject |
| --- | --- | --- |
| GOV-001 | `marker-scan.sh` | No stub markers in canonical surfaces |
| GOV-002 | `check-governance.sh` | Layer 1 + 2 + 4 required files exist |
| GOV-003 | `check-governance.sh` | `.mcp.json` has top-level `mcpServers` object |
| GOV-004 | `check-governance.sh` | `pre-tool-use.js` registered in `.claude/settings.json` |
| GOV-005 | `check-governance.sh` | Layer 3 required Claude agents exist |
| GOV-006 | `check-governance.sh` | Agent frontmatter has name / description / model / memory |
| GOV-007 | `check-governance.sh` | `python-pro` or `typescript-pro` agent present |
| GOV-008 | `check-governance.sh` | Required Claude skills exist |
| GOV-009 | `check-governance.sh` | Skill frontmatter has name / description / paths and matches filename |
| GOV-010 | `check-traceability.sh` | `specs/traceability.json` is well-formed JSON |
| GOV-011 | `check-traceability.sh` | Each criterion's source / tests / evidence resolves |
| GOV-012 | `check-doc-drift.sh` | Backtick-wrapped path references in docs/specs exist |

Severity is `error` for findings that block the build and `warning`
for soft drift the scaffold tolerates during early phases.
