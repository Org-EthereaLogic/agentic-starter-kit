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

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_PATH = PROJECT_ROOT / "scripts" / "governance_review"

if str(PACKAGE_PATH) not in sys.path:
    sys.path.insert(0, str(PACKAGE_PATH))

from governance_review import CHECKS  # noqa: E402
from governance_review.checks import run_all  # noqa: E402
from governance_review.cli import main as cli_main  # noqa: E402
from governance_review.finding import Severity  # noqa: E402
from governance_review.formatters import (  # noqa: E402
    format_json,
    format_sarif,
    format_text,
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
