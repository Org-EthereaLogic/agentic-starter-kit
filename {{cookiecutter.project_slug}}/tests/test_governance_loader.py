"""Unit tests for ``scripts/lib/governance.py`` enforcement-data accessors.

The loader is the single source of truth for the lists previously
inlined in ``scripts/check-governance.sh`` and
``scripts/marker-scan.sh``. These tests exercise the new accessors
against a synthetic governance YAML so they don't drift if the real
``governance-rules.yaml`` is reorganised.
"""

from __future__ import annotations

import shutil
import subprocess  # nosec B404 - tests exercise the repo-local governance.py CLI
import sys
import textwrap
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOADER_DIR = PROJECT_ROOT / "scripts" / "lib"
LOADER_SCRIPT = LOADER_DIR / "governance.py"

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
              both_keys_gate:
                rule: "CRIT-001, CRIT-002"
                rules:
                  - IMP-001
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


def test_get_for_enforcement_gate_rules_wins_over_rule(gate_rules: Path) -> None:
    """When a gate (incorrectly) defines both keys, ``rules`` wins.

    The precedence is deterministic and documented in the loader
    docstring; this test pins it so a refactor cannot silently flip it.
    """
    rules = GovernanceRules(rules_file=gate_rules)
    directives = rules.get_for_enforcement_gate("both_keys_gate")
    assert [d["id"] for d in directives] == ["IMP-001"]


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


# ----------------------------------------------------------------------
# CLI-level tests for the consolidated `--emit` flag (issue #111 #3) and
# the `--list` flag (issue #111 #5). These exercise governance.py as a
# subprocess since --emit/--list are argparse-level concerns in main(),
# not GovernanceRules methods.
#
# Test-gate rewind note: item #5 was originally implemented by *removing*
# the parsed-but-unread `--list` flag. That broke `query-governance.sh
# --list` (usage example #1) — with `--list` gone, argparse treated it as
# an ambiguous prefix of the surviving `--list-*` flags and exited 2. The
# corrective fix re-registers `--list` and wires it to actually drive the
# directive listing (so it is no longer parsed-but-unread), keeping item
# #5 satisfied while restoring the interface.
# ----------------------------------------------------------------------


def _run_loader(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # nosec B603 # nosemgrep - fixed argv, repo-local script
        [sys.executable, str(LOADER_SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _parse_emit_lines(stdout: str) -> list[tuple[str, str]]:
    pairs = []
    for line in stdout.splitlines():
        if not line:
            continue
        section, _, value = line.partition("\t")
        pairs.append((section, value))
    return pairs


@pytest.mark.parametrize(
    ("section", "list_flag"),
    [
        ("required_files", "--list-required-files"),
        ("required_agents", "--list-required-agents"),
        ("required_skills", "--list-required-skills"),
        ("optional_dirs", "--list-optional-dirs"),
        ("marker_surfaces", "--list-marker-surfaces"),
    ],
)
def test_emit_list_section_matches_individual_flag(
    synthetic_rules: Path, section: str, list_flag: str
) -> None:
    """A single-section --emit call must reproduce the equivalent --list-* output."""
    emitted = _run_loader("--file", str(synthetic_rules), "--emit", section)
    individual = _run_loader("--file", str(synthetic_rules), list_flag)

    assert emitted.returncode == 0, emitted.stderr
    assert individual.returncode == 0, individual.stderr

    values = [value for emitted_section, value in _parse_emit_lines(emitted.stdout) if emitted_section == section]
    assert values == [line for line in individual.stdout.splitlines() if line]


def test_emit_scalar_marker_regex_matches_individual_flag(synthetic_rules: Path) -> None:
    emitted = _run_loader("--file", str(synthetic_rules), "--emit", "marker_regex")
    individual = _run_loader("--file", str(synthetic_rules), "--marker-regex")

    assert emitted.returncode == 0, emitted.stderr
    assert individual.returncode == 0, individual.stderr

    pairs = _parse_emit_lines(emitted.stdout)
    assert len(pairs) == 1
    section, value = pairs[0]
    assert section == "marker_regex"
    assert value == individual.stdout.strip("\n")


def test_emit_multiple_sections_in_one_call(synthetic_rules: Path) -> None:
    """--emit accepts a comma-separated list and emits every requested section."""
    result = _run_loader(
        "--file",
        str(synthetic_rules),
        "--emit",
        "required_files,required_agents,required_skills,optional_dirs,marker_surfaces,marker_regex",
    )
    assert result.returncode == 0, result.stderr

    sections = {section for section, _ in _parse_emit_lines(result.stdout)}
    assert sections == {
        "required_files",
        "required_agents",
        "required_skills",
        "optional_dirs",
        "marker_surfaces",
        "marker_regex",
    }


def test_emit_unknown_section_is_a_user_error(synthetic_rules: Path) -> None:
    result = _run_loader("--file", str(synthetic_rules), "--emit", "bogus_section")
    assert result.returncode == 1
    assert "bogus_section" in result.stderr


def test_emit_against_shipped_rules() -> None:
    """--emit works end-to-end against the real governance-rules.yaml."""
    real = PROJECT_ROOT / "governance-rules.yaml"
    result = _run_loader(
        "--file",
        str(real),
        "--emit",
        "required_files,optional_dirs",
    )
    assert result.returncode == 0, result.stderr
    sections = {section for section, _ in _parse_emit_lines(result.stdout)}
    assert sections == {"required_files", "optional_dirs"}


def test_list_flag_lists_all_directives() -> None:
    """`--list` is a wired selector for the full directive listing.

    Regression test for the test-gate rewind: item #5's first attempt
    removed the `--list` argparse flag as "dead", which made a bare
    `--list` an ambiguous prefix of the surviving `--list-*` flags
    (argparse exit 2) and broke `scripts/query-governance.sh --list`
    (its documented usage example #1). The flag is re-registered and now
    actually drives the listing output, exiting 0. Because it reuses the
    same code path as the no-flag default, `--list` and a bare
    invocation are byte-identical.
    """
    real = PROJECT_ROOT / "governance-rules.yaml"
    listed = _run_loader("--file", str(real), "--list")
    default = _run_loader("--file", str(real))

    assert listed.returncode == 0, listed.stderr
    assert listed.stdout, "--list must emit the directive listing"
    # The listing is one line per directive (status, id, class, title).
    assert all(line.split()[0] in {"✓", "○"} for line in listed.stdout.splitlines() if line)
    assert listed.stdout == default.stdout


# check-governance.sh / marker-scan.sh / check-traceability.sh all demux
# the tab-separated stream by stripping only the leading `<key><TAB>`
# prefix; this mirrors that exact awk expression so the round-trip test
# below proves the shipped shell demux (not just governance.py) preserves
# an embedded tab.
_AWK = shutil.which("awk")
_DEMUX_AWK_REQUIRED_FILES = r'$1 == "required_files" { sub(/^[^\t]*\t/, ""); print }'


def _minimal_rules_with_required_file(tmp_path: Path, quoted_scalar: str) -> Path:
    """Write a minimal governance YAML whose single required_files entry
    is the given double-quoted YAML scalar (e.g. ``"a\\tb"``)."""
    rules = tmp_path / "governance-rules.yaml"
    rules.write_text(
        "critical: {count: 0}\n"
        "important: {count: 0}\n"
        "recommended: {count: 0}\n"
        "directives: []\n"
        "required_files:\n"
        f"  - {quoted_scalar}\n"
    )
    return rules


@pytest.mark.skipif(_AWK is None, reason="awk not installed")
def test_emit_value_with_embedded_tab_survives_shell_demux(tmp_path: Path) -> None:
    """A list value containing a literal tab survives emit -> awk demux.

    Regression test for the test-gate rewind (DEFECT 2): the tab-
    delimited `section<TAB>value` line protocol combined with a `print
    $2` demux truncated any value at its first embedded tab. The demux
    now strips only the leading `section<TAB>` prefix, so the full value
    — embedded tabs and all — is preserved. Drives a tabbed value
    through `governance.py --emit` and the exact awk expression shipped
    in check-governance.sh.
    """
    assert _AWK is not None
    # YAML `"weird\tname.md"` (a \t escape in a double-quoted scalar)
    # decodes to a value containing one literal tab.
    expected = "weird\tname.md"
    rules = _minimal_rules_with_required_file(tmp_path, r'"weird\tname.md"')

    emitted = _run_loader("--file", str(rules), "--emit", "required_files")
    assert emitted.returncode == 0, emitted.stderr
    # Sanity: the raw emit line carries the section prefix plus the tabbed value.
    assert emitted.stdout.rstrip("\n") == f"required_files\t{expected}"

    demux = subprocess.run(  # nosec B603 # nosemgrep - fixed argv, system awk
        [_AWK, "-F", r"\t", _DEMUX_AWK_REQUIRED_FILES],
        input=emitted.stdout,
        capture_output=True,
        text=True,
        check=True,
    )
    values = [line for line in demux.stdout.split("\n") if line != ""]
    assert values == [expected], (
        "embedded tab was truncated by the demux; expected the full value preserved"
    )


def test_emit_rejects_value_containing_a_newline(tmp_path: Path) -> None:
    """--emit fails loudly on a newline-bearing value (unrepresentable).

    The line protocol frames one item per line, so a literal newline in
    a value cannot be represented. Consistent with the repo's loud-
    failure philosophy, --emit prints an ERROR to stderr and exits 1
    rather than emitting output the demux would silently corrupt.
    """
    # YAML `"line1\nline2"` decodes to a value containing a real newline.
    rules = _minimal_rules_with_required_file(tmp_path, r'"line1\nline2"')

    result = _run_loader("--file", str(rules), "--emit", "required_files")
    assert result.returncode == 1
    assert "ERROR:" in result.stderr
    assert "newline" in result.stderr
