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
    rules = GovernanceRules(rules_file=synthetic_rules)
    assert rules.get_required_files() == ["CONSTITUTION.md", "README.md"]


def test_required_agents_round_trip(synthetic_rules: Path) -> None:
    rules = GovernanceRules(rules_file=synthetic_rules)
    assert rules.get_required_agents() == [
        ".claude/agents/lead-software-engineer.md"
    ]


def test_required_skills_round_trip(synthetic_rules: Path) -> None:
    rules = GovernanceRules(rules_file=synthetic_rules)
    assert rules.get_required_skills() == [".claude/skills/run-validate.md"]


def test_optional_dirs_round_trip(synthetic_rules: Path) -> None:
    rules = GovernanceRules(rules_file=synthetic_rules)
    assert rules.get_optional_dirs() == ["docs", "report"]


def test_marker_surfaces_round_trip(synthetic_rules: Path) -> None:
    rules = GovernanceRules(rules_file=synthetic_rules)
    assert rules.get_marker_surfaces() == ["CLAUDE.md", "docs"]


def test_marker_strings_assembled_from_pairs(synthetic_rules: Path) -> None:
    """The split-pair representation joins back into the literal markers."""
    rules = GovernanceRules(rules_file=synthetic_rules)
    # The forbidden literals are reassembled here only inside an
    # assertion comparing them to the loader output.
    expected_first = "TO" + "DO"
    expected_second = "FIX" + "ME"
    assert rules.get_marker_strings() == [expected_first, expected_second]


def test_marker_regex_word_bounded_alternation(synthetic_rules: Path) -> None:
    """The regex matches each marker on a word boundary, nothing else."""
    import re

    rules = GovernanceRules(rules_file=synthetic_rules)
    pattern = re.compile(rules.get_marker_regex())

    assert pattern.search("TO" + "DO: ship it")
    assert pattern.search("see FIX" + "ME tag")
    assert not pattern.search("TODOIST is a brand name")  # word boundary
    assert not pattern.search("nothing prohibited here")


def test_loader_works_against_shipped_rules() -> None:
    """The real governance-rules.yaml exposes every accessor non-empty."""
    real = PROJECT_ROOT / "governance-rules.yaml"
    assert real.exists(), "governance-rules.yaml must ship in every rendered project"
    rules = GovernanceRules(rules_file=real)
    assert rules.get_required_files()
    assert rules.get_required_agents()
    assert rules.get_required_skills()
    assert rules.get_optional_dirs()
    assert rules.get_marker_surfaces()
    assert rules.get_marker_strings()
    assert rules.get_marker_regex().startswith(r"\b(")


@pytest.fixture
def gate_rules(tmp_path: Path) -> Path:
    """Minimal YAML covering both validation_gates key shapes.

    ``string_gate`` uses the comma-separated ``rule`` string (the
    shape used by marker_scan, governance_check, hooks_test, and
    action_pins). ``list_gate`` uses the ``rules`` YAML list (the
    shape used by audit). Kept separate from ``synthetic_rules`` so
    these additions don't perturb the counts/sections asserted
    elsewhere.
    """
    rules = tmp_path / "governance-rules.yaml"
    rules.write_text(
        textwrap.dedent(
            """\
            critical:
              count: 2
            important:
              count: 1
            recommended:
              count: 0
            directives:
              - id: CRIT-001
                class: Critical
                title: First critical directive
              - id: CRIT-002
                class: Critical
                title: Second critical directive
              - id: IMP-001
                class: Important
                title: First important directive

            validation_gates:
              string_gate:
                rule: "CRIT-001, CRIT-002"
              list_gate:
                rules:
                  - CRIT-001
                  - IMP-001
              scalar_gate:
                rules: CRIT-001
              empty_gate:
                rules:
                  - BOGUS-999
            """
        )
    )
    return rules


def test_get_for_enforcement_gate_rule_string_shape(gate_rules: Path) -> None:
    """A gate whose entry uses the comma-string ``rule`` key resolves in order."""
    rules = GovernanceRules(rules_file=gate_rules)
    directives = rules.get_for_enforcement_gate("string_gate")
    assert [d["id"] for d in directives] == ["CRIT-001", "CRIT-002"]


def test_get_for_enforcement_gate_rules_list_shape(gate_rules: Path) -> None:
    """A gate whose entry uses the YAML-list ``rules`` key also resolves."""
    rules = GovernanceRules(rules_file=gate_rules)
    directives = rules.get_for_enforcement_gate("list_gate")
    assert [d["id"] for d in directives] == ["CRIT-001", "IMP-001"]


def test_get_for_enforcement_gate_scalar_rules_shape(gate_rules: Path) -> None:
    """A mis-authored scalar ``rules`` value is tolerated, not char-split."""
    rules = GovernanceRules(rules_file=gate_rules)
    directives = rules.get_for_enforcement_gate("scalar_gate")
    assert [d["id"] for d in directives] == ["CRIT-001"]


def test_get_for_enforcement_gate_unknown_gate_returns_empty(gate_rules: Path) -> None:
    """A gate name absent from validation_gates still yields an empty list."""
    rules = GovernanceRules(rules_file=gate_rules)
    assert rules.get_for_enforcement_gate("nonexistent") == []


def test_has_enforcement_gate_distinguishes_unknown_from_empty(gate_rules: Path) -> None:
    """A defined-but-empty gate is 'known' even though it resolves to []."""
    rules = GovernanceRules(rules_file=gate_rules)
    # Defined gate whose only id (BOGUS-999) resolves to no directive.
    assert rules.has_enforcement_gate("empty_gate") is True
    assert rules.get_for_enforcement_gate("empty_gate") == []
    # Genuinely absent gate name.
    assert rules.has_enforcement_gate("nonexistent") is False
    # Normal populated gate.
    assert rules.has_enforcement_gate("string_gate") is True


def test_get_for_enforcement_gate_against_shipped_rules() -> None:
    """The real governance-rules.yaml resolves both gate key shapes.

    Regression test for issue #103: the ``audit`` gate uses ``rules:``
    (a YAML list) while ``hooks_test`` uses ``rule:`` (a comma string).
    Both must resolve to their directives.
    """
    real = PROJECT_ROOT / "governance-rules.yaml"
    assert real.exists(), "governance-rules.yaml must ship in every rendered project"
    rules = GovernanceRules(rules_file=real)

    audit_directives = rules.get_for_enforcement_gate("audit")
    assert {d["id"] for d in audit_directives} == {
        "CRIT-004",
        "CRIT-005",
        "IMP-001",
        "IMP-003",
        "IMP-005",
    }

    hooks_test_directives = rules.get_for_enforcement_gate("hooks_test")
    assert [d["id"] for d in hooks_test_directives] == ["CRIT-008"]


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
    rules = GovernanceRules(rules_file=rules_file)
    assert rules.get_required_files() == []
    assert rules.get_marker_strings() == []
    assert rules.get_marker_regex() == ""
