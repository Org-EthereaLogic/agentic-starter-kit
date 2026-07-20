"""Unit tests for scripts/lib/common.sh's read_lines_into_array helper.

Issue #111 item #4 extracted the `while IFS= read -r line; do [[ -n
"$line" ]] && arr+=("$line"); done <<< "$raw"` pattern — duplicated
across check-governance.sh, marker-scan.sh, check-doc-drift.sh,
check-action-pins.sh, and check-traceability.sh — into a single
`read_lines_into_array` helper in common.sh. No existing test file
exercises common.sh directly; this one does, via a tiny bash harness
run as a subprocess (matching the subprocess-testing style already
used in test_validation_scripts.py and test_action_pin_check.py).
"""

from __future__ import annotations

import shutil
import subprocess  # nosec B404 - test exercises a repo-local shell helper
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
COMMON = PROJECT_ROOT / "scripts" / "lib" / "common.sh"
BASH = shutil.which("bash") or "/bin/bash"

# Sources common.sh, calls read_lines_into_array with $1, then prints
# each element of the resulting READ_LINES_RESULT array on its own
# line so the Python side can split on "\n" to recover the array.
#
# Deliberately NOT using a bash array-length expansion (an open-brace
# immediately followed by a hash, e.g. as used for counting elements
# elsewhere in this repo's shell scripts) anywhere in the harness
# below: this file is rendered by cookiecutter's default Jinja engine
# (only scripts/*.sh is exempted, via cookiecutter.json's
# `_copy_without_render`; a .py file under tests/ is not), whose
# comment-start token is that same open-brace-hash sequence. Writing
# it literally here would be read as an unclosed Jinja comment and
# abort the entire render — the cookiecutter-side twin of the
# copier-side collision guarded against in
# tests/test_no_copier_comment_collision.py (issue #133).
_HARNESS = (
    f'source "{COMMON}"; '
    'read_lines_into_array "$1"; '
    'printf "%s\\n" ${READ_LINES_RESULT[@]+"${READ_LINES_RESULT[@]}"}'
)


def _read_lines_into_array(raw: str) -> list[str]:
    result = subprocess.run(  # nosec B603 # nosemgrep - fixed argv, repo-local script
        [BASH, "-c", _HARNESS, "--", raw],
        capture_output=True,
        text=True,
        check=True,
    )
    stdout = result.stdout
    if stdout in ("", "\n"):
        # Zero elements: `printf "%s\n"` with no arguments still applies
        # the format once with an empty-string default, emitting a
        # single blank line. Safe to treat that as "empty array" here
        # because read_lines_into_array never stores an empty-string
        # element (its own `[[ -n "$line" ]]` guard filters those out),
        # so a genuine single-element result is never just "\n".
        return []
    return stdout.split("\n")[:-1]


def test_empty_raw_string_yields_empty_array() -> None:
    assert _read_lines_into_array("") == []


def test_blank_lines_are_filtered() -> None:
    raw = "a\n\nb\n\n\nc"
    assert _read_lines_into_array(raw) == ["a", "b", "c"]


def test_only_blank_lines_yields_empty_array() -> None:
    assert _read_lines_into_array("\n\n\n") == []


def test_multi_line_raw_string_preserves_order() -> None:
    raw = "first\nsecond\nthird"
    assert _read_lines_into_array(raw) == ["first", "second", "third"]


def test_values_containing_spaces_are_preserved_as_single_elements() -> None:
    raw = "source files/*.txt\ntest files/*.txt\nplain"
    assert _read_lines_into_array(raw) == [
        "source files/*.txt",
        "test files/*.txt",
        "plain",
    ]


def test_no_trailing_newline_final_line_is_still_captured() -> None:
    """The classic `<<<` here-string edge case.

    A here-string (`<<< "$raw"`) always appends its own trailing
    newline regardless of whether $raw itself ends in one, so the
    final `read -r` still terminates cleanly and the last line is not
    dropped either way.
    """
    with_trailing = _read_lines_into_array("a\nb\nc\n")
    without_trailing = _read_lines_into_array("a\nb\nc")
    assert with_trailing == ["a", "b", "c"]
    assert without_trailing == ["a", "b", "c"]


def test_single_line_no_newline() -> None:
    assert _read_lines_into_array("solo") == ["solo"]
