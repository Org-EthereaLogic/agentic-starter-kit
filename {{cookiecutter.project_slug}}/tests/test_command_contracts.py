"""Regression checks for the Layer-3 slash command contracts."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COMMANDS_DIR = REPO_ROOT / ".claude" / "commands"

EXPECTED_GOV_COMMANDS = {
    "gov.audit.md",
    "gov.check-traceability.md",
    "gov.commit.md",
    "gov.implement.md",
    "gov.plan.md",
    "gov.prime.md",
    "gov.pull-request.md",
    "gov.review.md",
    "gov.session-log.md",
    "gov.spec-bump.md",
    "gov.start.md",
    "gov.status.md",
    "gov.sync.md",
    "gov.test.md",
    "gov.threat-model.md",
    "gov.verify.md",
}

REQUIRED_FRONTMATTER_KEYS = ("description:", "allowed-tools:")

EXPECTED_PHRASES = {
    "gov.audit.md": (
        "If present and in scope: `docs/ARCHITECTURE.md`",
        "If present: `specs/traceability.json`",
        "`not scaffolded` rather than PASS",
    ),
    "gov.check-traceability.md": (
        "`NOT SCAFFOLDED`",
        "Do not claim orphaned-file or orphaned-criteria",
    ),
    "gov.plan.md": (
        "ADR/0001-adr-template.md",
        "no dedicated template is",
    ),
    "gov.prime.md": (
        "not from template-only `cookiecutter.json`",
    ),
    "gov.pull-request.md": (
        "Resolve `base_ref` to `target_branch`",
    ),
    "gov.review.md": (
        "when scaffolded, the",
        "Run the validation gates individually",
    ),
    "gov.spec-bump.md": (
        "compute the new version with",
        "`**Decision History:**` section",
        "`new_version` as `null`",
    ),
    "gov.sync.md": (
        "always scans both `docs/`",
        "specs/traceability.json` exists",
    ),
    "gov.test.md": (
        "| 1 | `marker-scan` | `make marker-scan` |",
        "| 8 | `test` | `make test` |",
    ),
    "gov.threat-model.md": (
        "If present: `docs/SECURITY_PROGRAM.md`",
        "create the parent",
    ),
}

FORBIDDEN_PHRASES = {
    "gov.check-traceability.md": (
        "missing/orphaned artifact",
    ),
    "gov.plan.md": (
        "rfc-template.md",
        "design-template.md",
    ),
    "gov.prime.md": (
        "per `cookiecutter.json` selections shipped into this",
    ),
    "gov.review.md": (
        "docs/PRD.md",
    ),
    "gov.spec-bump.md": (
        "frontmatter-style table",
    ),
    "gov.sync.md": (
        "invoked over `specs/`",
    ),
}

FRONTMATTER_RE = re.compile(r"\A---\n(?P<body>.+?)\n---\n", re.DOTALL)


class CommandContractTests(unittest.TestCase):
    def test_expected_gov_command_inventory_exists(self) -> None:
        actual = {path.name for path in COMMANDS_DIR.glob("gov.*.md")}
        self.assertEqual(actual, EXPECTED_GOV_COMMANDS)

    def test_each_command_has_required_frontmatter_keys(self) -> None:
        for path in sorted(COMMANDS_DIR.glob("gov.*.md")):
            match = FRONTMATTER_RE.match(path.read_text())
            self.assertIsNotNone(match, f"{path.name} is missing frontmatter")
            assert match is not None  # type narrow for static analysis
            body = match.group("body")
            for key in REQUIRED_FRONTMATTER_KEYS:
                self.assertIn(key, body, f"{path.name} is missing {key}")

    def test_reviewed_regressions_stay_fixed(self) -> None:
        for filename, phrases in EXPECTED_PHRASES.items():
            text = (COMMANDS_DIR / filename).read_text()
            for phrase in phrases:
                self.assertIn(phrase, text, f"{filename} is missing {phrase!r}")

        for filename, phrases in FORBIDDEN_PHRASES.items():
            text = (COMMANDS_DIR / filename).read_text()
            for phrase in phrases:
                self.assertNotIn(
                    phrase,
                    text,
                    f"{filename} still contains {phrase!r}",
                )


if __name__ == "__main__":
    unittest.main()