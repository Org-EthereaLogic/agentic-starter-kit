"""Regression tests for issue #111 item #5 (dead-code removal).

Three independent cleanups, each verified statically plus, where it
matters most (the Makefile), by actually invoking the affected
targets against this rendered project (self-check, mirroring the
pattern already used by test_governance_review.py's
`test_run_on_self_returns_no_errors` and
test_governance_loader.py's `test_loader_works_against_shipped_rules`):

1. The unused `check_tool`/`check_file` `define` macros are gone from
   Makefile.fragments/defs.mk, and nothing anywhere in the rendered
   tree ever called them (so removing them cannot change any Make
   target's behavior).
2. The `governance-rules.yaml` "RECOMMENDED (N)" section-header
   comment matches the real count of Recommended-class directives.
3. `make governance-check` and `make marker-scan` still pass here —
   proving the defs.mk edit didn't disturb the Makefile as a whole.
"""

from __future__ import annotations

import shutil
import subprocess  # nosec B404 - tests exercise repo-local make targets
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFS_MK = PROJECT_ROOT / "Makefile.fragments" / "defs.mk"
GOVERNANCE_RULES = PROJECT_ROOT / "governance-rules.yaml"
LOADER_DIR = PROJECT_ROOT / "scripts" / "lib"

if str(LOADER_DIR) not in sys.path:
    sys.path.insert(0, str(LOADER_DIR))

from governance import GovernanceRules  # noqa: E402


def test_dead_macros_removed_from_defs_mk() -> None:
    text = DEFS_MK.read_text(encoding="utf-8")
    assert "define check_tool" not in text
    assert "define check_file" not in text


def test_no_call_sites_reference_the_removed_macros() -> None:
    """Confirms removing the macros could not have changed any target's behavior.

    Scans every Makefile / *.mk file in the rendered project (not just
    defs.mk itself) for `$(call check_tool` or `$(call check_file`.
    """
    offenders: list[str] = []
    candidates = [PROJECT_ROOT / "Makefile", *PROJECT_ROOT.glob("Makefile.fragments/*.mk")]
    for path in candidates:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), 1):
            if "call check_tool" in line or "call check_file" in line:
                offenders.append(f"{path.relative_to(PROJECT_ROOT)}:{lineno}: {line.strip()}")

    assert not offenders, "\n".join(offenders)


def test_recommended_comment_matches_actual_directive_count() -> None:
    """governance-rules.yaml's 'RECOMMENDED (N)' header must match reality.

    Regression test for the stale '(4)' comment (actual count: 3
    REC-* directives). Parsed via GovernanceRules rather than a raw
    grep so this can never silently re-diverge from the same count
    ``validate_file()`` itself checks against the ``recommended.count``
    field.
    """
    rules = GovernanceRules(rules_file=GOVERNANCE_RULES)
    actual_count = len(rules.get_all_recommended())
    assert actual_count == 3, (
        f"expected 3 Recommended-class directives, found {actual_count}; "
        "update both the 'RECOMMENDED (N)' header comment and this test "
        "if that count intentionally changed"
    )

    text = GOVERNANCE_RULES.read_text(encoding="utf-8")
    assert f"RECOMMENDED ({actual_count})" in text
    assert "RECOMMENDED (4)" not in text


MAKE = shutil.which("make")


def _makefiles_contain_unrendered_jinja() -> bool:
    """True when the Makefile / *.mk fragments still carry cookiecutter
    Jinja markers — i.e. the suite is running against the raw template
    source rather than a rendered scaffold.

    ``make`` cannot parse Jinja (a fragment such as
    ``Makefile.fragments/sync.mk`` fails with ``*** missing separator``),
    so the make-invoking self-checks below must skip against template
    source and only run inside a rendered project.

    The Jinja delimiters are assembled by concatenation rather than
    written as literals: this test file is itself rendered by
    cookiecutter's Jinja engine (only ``scripts/*.sh`` is exempted via
    ``_copy_without_render``), so a literal open-variable or open-block
    delimiter here would be interpreted at render time and abort
    generation — the same collision class guarded against in
    ``tests/test_common_lib.py``. At runtime the concatenations evaluate
    to the real two-character delimiters.
    """
    jinja_var_open = "{" + "{"
    jinja_block_open = "{" + "%"
    candidates = [PROJECT_ROOT / "Makefile", *PROJECT_ROOT.glob("Makefile.fragments/*.mk")]
    for path in candidates:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if jinja_var_open in text or jinja_block_open in text:
            return True
    return False


_TEMPLATE_SOURCE = _makefiles_contain_unrendered_jinja()


def _run_make(target: str) -> subprocess.CompletedProcess[str]:
    assert MAKE is not None
    return subprocess.run(  # nosec B603 # nosemgrep - fixed argv, repo-local Makefile
        [MAKE, target],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.skipif(MAKE is None, reason="make not installed")
def test_governance_check_target_still_passes_after_defs_mk_cleanup() -> None:
    if _TEMPLATE_SOURCE:
        pytest.skip(reason="requires rendered scaffold; Makefile fragments contain Jinja in template source")
    result = _run_make("governance-check")
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.skipif(MAKE is None, reason="make not installed")
def test_marker_scan_target_still_passes_after_defs_mk_cleanup() -> None:
    if _TEMPLATE_SOURCE:
        pytest.skip(reason="requires rendered scaffold; Makefile fragments contain Jinja in template source")
    result = _run_make("marker-scan")
    assert result.returncode == 0, result.stdout + result.stderr
