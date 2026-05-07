"""Unit tests for ``scripts/lib/governance.py`` enforcement-data accessors.

The loader is the single source of truth for the lists previously
inlined in ``scripts/check-governance.sh`` and
``scripts/marker-scan.sh``. These tests exercise the new accessors
against a synthetic governance YAML so they don't drift if the real
``governance-rules.yaml`` is reorganised.
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOADER_DIR = PROJECT_ROOT / "scripts" / "lib"

# scripts/lib is not on sys.path by default; prepend it so the
# governance module can be imported with normal type-checked syntax
# rather than the importlib.util dance.
sys.path.insert(0, str(LOADER_DIR))

from governance import GovernanceRules  # noqa: E402


@pytest.fixture
def synthetic_rules(tmp_path: Path) -> Path:
    """Minimal YAML covering every accessor under test."""
    rules = tmp_path / "governance-rules.yaml"
    rules.write_text(
        textwrap.dedent(
            """\
            critical:
              count: 0
            important:
              count: 0
            recommended:
              count: 0
            directives: []

            required_files:
              - CONSTITUTION.md
              - README.md
            required_agents:
              - .claude/agents/lead-software-engineer.md
            required_skills:
              - .claude/skills/run-validate.md
            optional_dirs:
              - docs
              - report

            prohibited_markers:
              pattern_pairs:
                - [TO, DO]
                - [FIX, ME]
              surfaces:
                - CLAUDE.md
                - docs
            """
        )
    )
    return rules


def test_required_files_round_trip(synthetic_rules: Path) -> None:
    rules = GovernanceRules(synthetic_rules)
    assert rules.get_required_files() == ["CONSTITUTION.md", "README.md"]


def test_required_agents_round_trip(synthetic_rules: Path) -> None:
    rules = GovernanceRules(synthetic_rules)
    assert rules.get_required_agents() == [
        ".claude/agents/lead-software-engineer.md"
    ]


def test_required_skills_round_trip(synthetic_rules: Path) -> None:
    rules = GovernanceRules(synthetic_rules)
    assert rules.get_required_skills() == [".claude/skills/run-validate.md"]


def test_optional_dirs_round_trip(synthetic_rules: Path) -> None:
    rules = GovernanceRules(synthetic_rules)
    assert rules.get_optional_dirs() == ["docs", "report"]


def test_marker_surfaces_round_trip(synthetic_rules: Path) -> None:
    rules = GovernanceRules(synthetic_rules)
    assert rules.get_marker_surfaces() == ["CLAUDE.md", "docs"]


def test_marker_strings_assembled_from_pairs(synthetic_rules: Path) -> None:
    """The split-pair representation joins back into the literal markers."""
    rules = GovernanceRules(synthetic_rules)
    # The forbidden literals are reassembled here only inside an
    # assertion comparing them to the loader output.
    expected_first = "TO" + "DO"
    expected_second = "FIX" + "ME"
    assert rules.get_marker_strings() == [expected_first, expected_second]


def test_marker_regex_word_bounded_alternation(synthetic_rules: Path) -> None:
    """The regex matches each marker on a word boundary, nothing else."""
    import re

    rules = GovernanceRules(synthetic_rules)
    pattern = re.compile(rules.get_marker_regex())

    assert pattern.search("TO" + "DO: ship it")
    assert pattern.search("see FIX" + "ME tag")
    assert not pattern.search("TODOIST is a brand name")  # word boundary
    assert not pattern.search("nothing prohibited here")


def test_loader_works_against_shipped_rules() -> None:
    """The real governance-rules.yaml exposes every accessor non-empty."""
    real = PROJECT_ROOT / "governance-rules.yaml"
    if not real.exists():
        pytest.skip("governance-rules.yaml not present in this checkout")
    rules = GovernanceRules(real)
    assert rules.get_required_files()
    assert rules.get_required_agents()
    assert rules.get_required_skills()
    assert rules.get_optional_dirs()
    assert rules.get_marker_surfaces()
    assert rules.get_marker_strings()
    assert rules.get_marker_regex().startswith(r"\b(")


def test_missing_sections_return_empty_lists(tmp_path: Path) -> None:
    """Sparse YAML must not crash the loader."""
    rules_file = tmp_path / "sparse.yaml"
    rules_file.write_text(
        textwrap.dedent(
            """\
            critical: {count: 0}
            important: {count: 0}
            recommended: {count: 0}
            directives: []
            """
        )
    )
    rules = GovernanceRules(rules_file)
    assert rules.get_required_files() == []
    assert rules.get_marker_strings() == []
    assert rules.get_marker_regex() == ""
