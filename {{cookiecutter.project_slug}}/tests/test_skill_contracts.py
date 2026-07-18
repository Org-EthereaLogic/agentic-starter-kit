"""Regression checks for the Layer-3 skill contracts."""

from __future__ import annotations

import os
import re
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = REPO_ROOT / ".claude" / "agents"
SKILLS_DIR = REPO_ROOT / ".claude" / "skills"
GOVERNANCE_CHECK = REPO_ROOT / "scripts" / "check-governance.sh"
GOVERNANCE_LIB = REPO_ROOT / "scripts" / "lib"
GOVERNANCE_RULES = REPO_ROOT / "governance-rules.yaml"
GIT_HOOKS = REPO_ROOT / ".githooks"
HOOKS_MAKEFILE = REPO_ROOT / "Makefile.fragments" / "hooks.mk"

EXPECTED_SKILLS = {
    "audit-trail-tail.md",
    "run-validate.md",
    "traceability-update.md",
}

REQUIRED_FRONTMATTER_KEYS = ("name:", "description:", "paths:")

EXPECTED_PHRASES = {
    ".claude/skills/run-validate.md": (
        "`Makefile` is authoritative",
        "Coverage is separate.",
        "eight validate gates",
        "does not invoke coverage",
        "`npm install`",
    ),
    ".claude/skills/audit-trail-tail.md": (
        "tail -n 20 report/audit.jsonl | jq .",
    ),
    ".claude/skills/traceability-update.md": (
        "`check-traceability` failure waiting to happen.",
    ),
    "AGENTS.md": (
        "`make validate` aggregates every check above except",
        "`make coverage` — language-specific coverage evidence",
    ),
}

FORBIDDEN_PHRASES = {
    ".claude/skills/run-validate.md": (
        "`Makefile.fragments/checks.mk` is authoritative",
        "six gates above",
        "package-lock'd deps",
    ),
    ".claude/skills/traceability-update.md": (
        "`check-doc-drift` failure waiting to happen.",
    ),
}

FRONTMATTER_RE = re.compile(r"\A---\n(?P<body>.+?)\n---\n", re.DOTALL)


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def _create_fake_node(bin_dir: Path) -> None:
    node_path = bin_dir / "node"
    node_path.write_text("#!/bin/sh\nexit 0\n")
    node_path.chmod(
        node_path.stat().st_mode
        | stat.S_IXUSR
        | stat.S_IXGRP
        | stat.S_IXOTH
    )


def _create_minimal_project(root: Path) -> None:
    for name in (
        "CONSTITUTION.md",
        "DIRECTIVES.md",
        "SECURITY.md",
        "README.md",
        "CLAUDE.md",
        "AGENTS.md",
        "GEMINI.md",
    ):
        _write_text(root / name, f"# {name}\n")

    _write_text(
        root / ".claude" / "settings.json",
        '{"hooks": {"PreToolUse": ["pre-tool-use.js"]}}\n',
    )
    _write_text(
        root / ".claude" / "hooks" / "pre-tool-use.js",
        "console.log('hook');\n",
    )
    _write_text(root / ".mcp.json", '{"mcpServers": {}}\n')
    _write_text(root / "docs" / "MCP_POLICY.md", "# MCP policy\n")
    _write_text(root / "specs" / "deep_specs" / "README.md", "# Spec\n")
    (root / "specs" / "security-requirements").mkdir(
        parents=True,
        exist_ok=True,
    )
    (root / "report").mkdir(parents=True, exist_ok=True)

    shutil.copytree(AGENTS_DIR, root / ".claude" / "agents")
    shutil.copytree(SKILLS_DIR, root / ".claude" / "skills")

    # check-governance.sh now reads its required-file/agent/skill
    # lists from governance-rules.yaml via scripts/lib/governance.py.
    # Copy both into the minimal project so the script can resolve
    # them at run time.
    shutil.copy2(GOVERNANCE_RULES, root / "governance-rules.yaml")
    shutil.copytree(GOVERNANCE_LIB, root / "scripts" / "lib")
    shutil.copytree(GIT_HOOKS, root / ".githooks")
    _write_text(
        root / "Makefile.fragments" / "hooks.mk",
        HOOKS_MAKEFILE.read_text(),
    )


def _run_governance_check(project_root: Path) -> subprocess.CompletedProcess[str]:
    bin_dir = project_root / ".test-bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    _create_fake_node(bin_dir)
    env = {
        **os.environ,
        "PATH": f"{bin_dir}:{os.environ.get('PATH', '')}",
    }
    return subprocess.run(
        ["bash", str(GOVERNANCE_CHECK)],
        cwd=project_root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


class SkillContractTests(unittest.TestCase):
    def test_expected_skill_inventory_exists(self) -> None:
        actual = {
            path.name for path in SKILLS_DIR.glob("*.md") if path.name != "README.md"
        }
        self.assertEqual(actual, EXPECTED_SKILLS)

    def test_each_skill_has_required_frontmatter_keys(self) -> None:
        for path in sorted(SKILLS_DIR.glob("*.md")):
            if path.name == "README.md":
                continue
            match = FRONTMATTER_RE.match(path.read_text())
            self.assertIsNotNone(match, f"{path.name} is missing frontmatter")
            if match is None:
                self.fail(f"{path.name} is missing frontmatter")
            body = match.group("body")
            for key in REQUIRED_FRONTMATTER_KEYS:
                self.assertIn(key, body, f"{path.name} is missing {key}")

    def test_reviewed_regressions_stay_fixed(self) -> None:
        for relative_path, phrases in EXPECTED_PHRASES.items():
            text = (REPO_ROOT / relative_path).read_text()
            for phrase in phrases:
                self.assertIn(
                    phrase,
                    text,
                    f"{relative_path} is missing {phrase!r}",
                )

        for relative_path, phrases in FORBIDDEN_PHRASES.items():
            text = (REPO_ROOT / relative_path).read_text()
            for phrase in phrases:
                self.assertNotIn(
                    phrase,
                    text,
                    f"{relative_path} still contains {phrase!r}",
                )

    def test_governance_check_accepts_indented_skill_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _create_minimal_project(tmp_path)
            skill = tmp_path / ".claude" / "skills" / "run-validate.md"
            text = skill.read_text()
            text = text.replace("\nname:", "\n  name:", 1)
            text = text.replace("\ndescription:", "\n  description:", 1)
            text = text.replace("\npaths:", "\n  paths:", 1)
            skill.write_text(text)
            result = _run_governance_check(tmp_path)

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_governance_check_rejects_missing_skill_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _create_minimal_project(tmp_path)
            skill = tmp_path / ".claude" / "skills" / "run-validate.md"
            text = skill.read_text()
            text = re.sub(
                r"^description:.*\n",
                "",
                text,
                count=1,
                flags=re.MULTILINE,
            )
            skill.write_text(text)
            result = _run_governance_check(tmp_path)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing required frontmatter", result.stderr)

    def test_governance_check_rejects_skill_name_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _create_minimal_project(tmp_path)
            skill = tmp_path / ".claude" / "skills" / "run-validate.md"
            text = skill.read_text().replace(
                "name: run-validate",
                "name: not-run-validate",
                1,
            )
            skill.write_text(text)
            result = _run_governance_check(tmp_path)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not match filename", result.stderr)


if __name__ == "__main__":
    unittest.main()
