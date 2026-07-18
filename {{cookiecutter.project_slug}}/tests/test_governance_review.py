"""Smoke tests for the governance-review CLI validator (issue #20).

The package ships under `scripts/governance_review/` so that it is
installable via `uv tool install ./scripts/governance_review`. These
tests import the package via PYTHONPATH manipulation rather than
requiring the install — they are part of the rendered project's
test suite, not part of the validator's own packaging tests.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_PATH = PROJECT_ROOT / "scripts" / "governance_review"

if str(PACKAGE_PATH) not in sys.path:
    sys.path.insert(0, str(PACKAGE_PATH))

from governance_review import CHECKS  # noqa: E402
from governance_review.checks import (  # noqa: E402
    check_gov_001,
    check_gov_002,
    check_gov_004,
    check_gov_006,
    check_gov_010,
    check_gov_011,
    check_gov_012,
    run_all,
)
from governance_review.cli import main as cli_main  # noqa: E402
from governance_review.finding import Severity  # noqa: E402
from governance_review.formatters import (  # noqa: E402
    format_json,
    format_sarif,
    format_text,
)
from governance_review.governance import GovernanceRules  # noqa: E402


def _write_rules(root: Path, **overrides: object) -> None:
    data: dict[str, object] = {
        "required_files": [],
        "optional_dirs": [],
        "required_agents": [],
        "required_skills": [],
        "prohibited_markers": {
            "pattern_pairs": [["BAD", "MARK"]],
            "surfaces": ["docs"],
        },
    }
    data.update(overrides)
    import yaml

    (root / "governance-rules.yaml").write_text(
        yaml.safe_dump(data), encoding="utf-8"
    )


def test_check_inventory_has_stable_ids() -> None:
    ids = [spec.id for spec in CHECKS]
    assert ids == sorted(ids), "GOV-NNN ids must be in monotonic order"
    assert len(set(ids)) == len(ids), "GOV-NNN ids must be unique"
    for spec in CHECKS:
        assert spec.id.startswith("GOV-"), spec.id
        assert spec.anchor.startswith("gov-"), spec.anchor


def test_run_on_self_returns_no_errors() -> None:
    """The rendered project (this tree) must not produce GOV-NNN errors."""
    findings = run_all(PROJECT_ROOT)
    errors = [f for f in findings if f.severity is Severity.ERROR]
    assert errors == [], "\n".join(
        f"{f.id} {f.location}: {f.message}" for f in errors
    )


def test_cli_exits_zero_on_self(capsys: pytest.CaptureFixture[str]) -> None:
    code = cli_main(["--root", str(PROJECT_ROOT)])
    assert code == 0


def test_cli_lists_every_check(capsys: pytest.CaptureFixture[str]) -> None:
    code = cli_main(["--list-checks"])
    out = capsys.readouterr().out
    assert code == 0
    for spec in CHECKS:
        assert spec.id in out


def test_json_output_parses() -> None:
    findings = run_all(PROJECT_ROOT)
    payload = json.loads(format_json(findings))
    assert payload["tool"]["name"] == "governance-review"
    assert isinstance(payload["findings"], list)


def test_sarif_output_is_valid_log() -> None:
    findings = run_all(PROJECT_ROOT)
    log = json.loads(format_sarif(findings))
    assert log["version"] == "2.1.0"
    assert log["runs"][0]["tool"]["driver"]["name"] == "governance-review"
    rules = log["runs"][0]["tool"]["driver"]["rules"]
    assert len(rules) == len(CHECKS)


def test_text_output_summary_present() -> None:
    findings = run_all(PROJECT_ROOT)
    text = format_text(findings)
    assert "governance-review" in text


def test_unknown_check_id_is_a_user_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    code = cli_main(["--select", "GOV-999"])
    err = capsys.readouterr().err
    assert code == 2
    assert "GOV-999" in err


def _write_required_governance_files(root: Path) -> None:
    _write_rules(root)
    files = {
        "CONSTITUTION.md": "ok\n",
        "DIRECTIVES.md": "ok\n",
        "SECURITY.md": "ok\n",
        "README.md": "ok\n",
        "CLAUDE.md": "ok\n",
        "AGENTS.md": "ok\n",
        "GEMINI.md": "ok\n",
        ".claude/settings.json": '{"hooks": ["pre-tool-use.js"]}\n',
        ".claude/hooks/pre-tool-use.js": "console.log('ok')\n",
        ".mcp.json": '{"mcpServers": {}}\n',
        "docs/MCP_POLICY.md": "ok\n",
    }
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def test_gov_001_ignores_skip_markers_only_within_scanned_tree(
    tmp_path: Path,
) -> None:
    root = tmp_path / ".git" / "example-project"
    docs = root / "docs"
    docs.mkdir(parents=True)
    _write_rules(root, prohibited_markers={"pattern_pairs": [["TO", "DO"]], "surfaces": ["docs"]})
    target = docs / "notes.md"
    target.write_text("contains TO" + "DO marker\n", encoding="utf-8")

    findings = check_gov_001(root)

    assert [f.location for f in findings] == ["docs/notes.md"]


def test_gov_002_preserves_optional_governance_warnings(
    tmp_path: Path,
) -> None:
    _write_required_governance_files(tmp_path)
    rules = GovernanceRules.load(PROJECT_ROOT)
    _write_rules(
        tmp_path,
        required_files=list(rules.required_files),
        optional_dirs=list(rules.optional_dirs),
    )
    (tmp_path / "specs" / "deep_specs").mkdir(parents=True)

    findings = check_gov_002(tmp_path)

    warning_messages = {f.message for f in findings if f.severity is Severity.WARNING}
    assert "optional directory not yet present: specs/security-requirements" in warning_messages
    assert "optional directory not yet present: report" in warning_messages
    assert "specs/deep_specs contains no .md files yet" in warning_messages


def test_gov_006_accepts_indented_frontmatter_keys(tmp_path: Path) -> None:
    agent = tmp_path / ".claude" / "agents" / "example.md"
    agent.parent.mkdir(parents=True)
    agent.write_text(
        "---\n"
        "  name: example\n"
        "  description: Example agent\n"
        "  model: gpt-5.4\n"
        "  memory: true\n"
        "---\n",
        encoding="utf-8",
    )

    assert check_gov_006(tmp_path) == []


def test_gov_010_validates_schema_when_ajv_is_available(tmp_path: Path) -> None:
    specs = tmp_path / "specs"
    specs.mkdir()
    (specs / "traceability.json").write_text('{"criteria": []}\n', encoding="utf-8")
    (specs / "traceability.schema.json").write_text('{"type": "object"}\n', encoding="utf-8")

    with (
        patch("governance_review.checks.shutil.which", return_value="ajv"),
        patch(
            "governance_review.checks.subprocess.run",
            return_value=CompletedProcess(args=["ajv"], returncode=1),
        ),
    ):
        findings = check_gov_010(tmp_path)

    assert len(findings) == 1
    assert "does not conform" in findings[0].message


def test_gov_011_tolerates_non_object_traceability_roots(tmp_path: Path) -> None:
    specs = tmp_path / "specs"
    specs.mkdir()
    (specs / "traceability.json").write_text("[]\n", encoding="utf-8")

    assert check_gov_011(tmp_path) == []


def test_configured_enforcement_datasets_control_checks(tmp_path: Path) -> None:
    _write_rules(
        tmp_path,
        required_files=["custom-required.txt"],
        optional_dirs=["custom-optional"],
        required_agents=["custom/agent.md"],
        required_skills=["custom/skill.md"],
        prohibited_markers={
            "pattern_pairs": [["BAD", "MARK"]],
            "surfaces": ["custom-surface"],
        },
    )
    findings = run_all(tmp_path)
    messages = {finding.message for finding in findings}
    assert "required file missing: custom-required.txt" in messages  # nosec B101
    assert "optional directory not yet present: custom-optional" in messages  # nosec B101
    assert "required agent missing: custom/agent.md" in messages  # nosec B101
    assert "required skill missing: custom/skill.md" in messages  # nosec B101


def test_gov_001_scans_around_invalid_utf8(tmp_path: Path) -> None:
    _write_rules(tmp_path)
    target = tmp_path / "docs" / "mixed.md"
    target.parent.mkdir()
    target.write_bytes(b"before\xffBADMARK after\n")
    findings = check_gov_001(tmp_path)
    assert [(finding.location, finding.line) for finding in findings] == [  # nosec B101
        ("docs/mixed.md", 1)
    ]


@pytest.mark.parametrize("content", ["", "# comments only\n", "required_files: [\n"])
def test_bad_rules_yaml_is_a_clean_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], content: str
) -> None:
    (tmp_path / "governance-rules.yaml").write_text(content, encoding="utf-8")
    code = cli_main(["--root", str(tmp_path), "--format", "json"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert code == 1
    assert payload["findings"][0]["location"] == "governance-rules.yaml"  # nosec B101
    assert "Traceback" not in captured.out + captured.err  # nosec B101


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ([], "root must be an object"),
        ({}, "field 'criteria' must be a list"),
        ({"criteria": ["bad"]}, "criteria[0] must be an object"),
    ],
)
def test_gov_010_reports_malformed_criteria(
    tmp_path: Path, payload: object, message: str
) -> None:
    specs = tmp_path / "specs"
    specs.mkdir()
    (specs / "traceability.json").write_text(json.dumps(payload), encoding="utf-8")
    assert message in check_gov_010(tmp_path)[0].message  # nosec B101


def test_gov_011_reports_scalar_collections_without_character_iteration(tmp_path: Path) -> None:
    specs = tmp_path / "specs"
    specs.mkdir()
    payload = {"criteria": [{"id": "AC-1", "source": "missing.py", "tests": "test_x.py", "evidence": "report.txt"}]}
    (specs / "traceability.json").write_text(json.dumps(payload), encoding="utf-8")
    findings = check_gov_011(tmp_path)
    assert [finding.message for finding in findings] == [  # nosec B101
        "criterion AC-1 field 'source' must be a list",
        "criterion AC-1 field 'tests' must be a list",
        "criterion AC-1 field 'evidence' must be a list",
    ]


def _pre_tool_settings(
    command: str, *, matcher: str = "Bash", hook_type: str = "command"
) -> dict[str, object]:
    return {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": matcher,
                    "hooks": [{"type": hook_type, "command": command}],
                }
            ]
        }
    }


@pytest.mark.parametrize(
    ("settings", "passes"),
    [
        (
            {
                "hooks": {
                    "PreToolUse": [
                        {
                            "matcher": "Bash",
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": "node .claude/hooks/pre-tool-use.js",
                                }
                            ],
                        }
                    ]
                }
            },
            True,
        ),
        ({"decoy": "pre-tool-use.js"}, False),
        ({"hooks": {"SessionStart": [{"hooks": [{"command": "node .claude/hooks/pre-tool-use.js"}]}]}}, False),
        ({"hooks": {"PreToolUse": "pre-tool-use.js"}}, False),
        (_pre_tool_settings("node other.js"), False),
        (_pre_tool_settings("echo .claude/hooks/pre-tool-use.js"), False),
        (_pre_tool_settings("node .claude/hooks/pre-tool-use.js.bak"), False),
        (_pre_tool_settings("# node .claude/hooks/pre-tool-use.js"), False),
        (_pre_tool_settings("printf node .claude/hooks/pre-tool-use.js"), False),
        (_pre_tool_settings("node .claude/hooks/pre-tool-use.js", matcher="Read"), False),
        (_pre_tool_settings("node .claude/hooks/pre-tool-use.js", hook_type="prompt"), False),
        (
            {
                "hooks": {
                    "PreToolUse": [
                        {
                            "matcher": "Bash",
                            "hooks": [
                                {"command": "node .claude/hooks/pre-tool-use.js"}
                            ],
                        }
                    ]
                }
            },
            False,
        ),
        (
            {
                "hooks": {
                    "PreToolUse": [
                        {
                            "matcher": "Bash",
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": "HOOK_MODE=strict node "
                                    ".claude/hooks/pre-tool-use.js"
                                }
                            ]
                        }
                    ]
                }
            },
            True,
        ),
    ],
)
def test_gov_004_requires_structural_pre_tool_registration(
    tmp_path: Path, settings: object, passes: bool
) -> None:
    path = tmp_path / ".claude" / "settings.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(settings), encoding="utf-8")
    assert (check_gov_004(tmp_path) == []) is passes  # nosec B101


def test_gov_012_accepts_paths_relative_to_markdown_file(tmp_path: Path) -> None:
    docs = tmp_path / "docs" / "guides"
    docs.mkdir(parents=True)
    (tmp_path / "docs" / "target.md").write_text("target\n", encoding="utf-8")
    (docs / "guide.md").write_text("See `../target.md`.\n", encoding="utf-8")

    assert check_gov_012(tmp_path) == []


def test_cli_select_filters_to_requested_checks(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _write_rules(tmp_path, required_files=["missing.txt"])
    code = cli_main(["--root", str(tmp_path), "--select", "GOV-002", "--format", "json"])
    payload = json.loads(capsys.readouterr().out)

    assert code == 1
    assert {finding["id"] for finding in payload["findings"]} == {"GOV-002"}


def test_cli_warnings_as_errors_changes_exit_code(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _write_rules(tmp_path)
    docs = tmp_path / "docs"
    docs.mkdir(parents=True)
    (docs / "guide.md").write_text("See `missing.md`.\n", encoding="utf-8")

    code = cli_main(
        [
            "--root",
            str(tmp_path),
            "--select",
            "GOV-012",
            "--warnings-as-errors",
            "--format",
            "json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert code == 1
    assert payload["findings"][0]["id"] == "GOV-012"
