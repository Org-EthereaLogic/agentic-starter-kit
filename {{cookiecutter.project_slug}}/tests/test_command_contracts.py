"""Regression checks for the Layer-3 slash command contracts."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COMMANDS_DIR = REPO_ROOT / ".claude" / "commands"

EXPECTED_COMMANDS = {
    "audit.md",
    "check-traceability.md",
    "commit.md",
    "implement.md",
    "plan.md",
    "prime.md",
    "pull-request.md",
    "review.md",
    "session-log.md",
    "spec-bump.md",
    "start.md",
    "status.md",
    "sync.md",
    "test.md",
    "threat-model.md",
    "verify.md",
}

REQUIRED_FRONTMATTER_KEYS = ("description:", "allowed-tools:")

EXPECTED_PHRASES = {
    "audit.md": (
        "If present and in scope: `docs/ARCHITECTURE.md`",
        "If present: `specs/traceability.json`",
        "`not scaffolded` rather than PASS",
    ),
    "check-traceability.md": (
        "`NOT SCAFFOLDED`",
        "Do not claim orphaned-file or orphaned-criteria",
    ),
    "plan.md": (
        "ADR/0001-adr-template.md",
        "no dedicated template is",
    ),
    "prime.md": (
        "not from template-only `cookiecutter.json`",
    ),
    "pull-request.md": (
        "Resolve `base_ref` to `target_branch`",
    ),
    "review.md": (
        "when scaffolded, the",
        "Run the validation gates individually",
    ),
    "spec-bump.md": (
        "compute the new version with",
        "`**Decision History:**` section",
        "`new_version` as `null`",
    ),
    "sync.md": (
        "always scans both `docs/`",
        "specs/traceability.json` exists",
    ),
    "test.md": (
        "| 1 | `marker-scan` | `make marker-scan` |",
        "| 8 | `test` | `make test` |",
    ),
    "threat-model.md": (
        "If present: `docs/SECURITY_PROGRAM.md`",
        "create the parent",
    ),
}

FORBIDDEN_PHRASES = {
    "check-traceability.md": (
        "missing/orphaned artifact",
    ),
    "plan.md": (
        "rfc-template.md",
        "design-template.md",
    ),
    "prime.md": (
        "per `cookiecutter.json` selections shipped into this",
    ),
    "review.md": (
        "docs/PRD.md",
    ),
    "spec-bump.md": (
        "frontmatter-style table",
    ),
    "sync.md": (
        "invoked over `specs/`",
    ),
}

FRONTMATTER_RE = re.compile(r"\A---\n(?P<body>.+?)\n---\n", re.DOTALL)


class CommandContractTests(unittest.TestCase):
    def test_expected_command_inventory_exists(self) -> None:
        actual = {path.name for path in COMMANDS_DIR.glob("*.md")}
        self.assertEqual(actual, EXPECTED_COMMANDS)

    def test_each_command_has_required_frontmatter_keys(self) -> None:
        for path in sorted(COMMANDS_DIR.glob("*.md")):
            match = FRONTMATTER_RE.match(path.read_text())
            self.assertIsNotNone(match, f"{path.name} is missing frontmatter")
            if match is None:
                self.fail(f"{path.name} is missing frontmatter")
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
