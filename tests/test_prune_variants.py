"""Unit tests for the variant-pruning parser.

The parser is duplicated on purpose (see the module docstrings):
``hooks/_prune_pyproject.py:prune_text`` is invoked by copier, while
``hooks/post_gen_project.py:_prune_variants`` is a byte-equivalent copy
because cookiecutter runs its post-gen hook from a temp dir with no
access to sibling files. These tests run the *same* cases against
*both* copies, so behavioural drift between them fails here — earlier
and more precisely than the render-equivalence smoke job.

Fast and in-process: the parser is a pure function, so no render is
needed. Because the integration test in ``test_post_gen_pruning.py``
subprocesses cookiecutter, this file is what gives ``--cov=hooks`` real
coverage of the branch logic (including the new raise paths).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

HOOKS = Path(__file__).resolve().parents[1] / "hooks"


def _load(filename: str, modname: str) -> ModuleType:
    """Import a hooks module by file path (there is no ``hooks/__init__.py``).

    Both modules are import-safe: module-level Jinja-placeholder strings
    are ordinary Python string literals, and the file-writing ``main()``
    is guarded by ``if __name__ == "__main__"``.
    """
    spec = importlib.util.spec_from_file_location(modname, HOOKS / filename)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_pp = _load("_prune_pyproject.py", "prune_pyproject_mod")
_pg = _load("post_gen_project.py", "post_gen_project_mod")

# Each impl carries its own function + VariantError class; run every case
# against both so the two copies cannot silently diverge.
IMPLS = [
    pytest.param(_pp.prune_text, _pp.VariantError, id="copier"),
    pytest.param(_pg._prune_variants, _pg.VariantError, id="cookiecutter"),
]

A_TY = {"typechecker": "ty", "sbom": "yes"}
A_MY = {"typechecker": "mypy", "sbom": "no"}
A_TY_NOSBOM = {"typechecker": "ty", "sbom": "no"}


def _lines(*rows: str) -> str:
    """Join ``rows`` into a newline-terminated block (mirrors file text)."""
    return "\n".join(rows) + "\n"


# --- Well-formed input: exact output --------------------------------------

VALID_CASES = [
    # name, input, answers, expected
    ("line_keep", "x = 1  # variant:typechecker=ty", A_TY, "x = 1"),
    ("line_drop", "x = 1  # variant:typechecker=mypy", A_TY, ""),
    ("line_sbom_keep", "dep,  # variant:sbom=yes", A_TY, "dep,"),
    ("line_sbom_drop", "dep,  # variant:sbom=yes", A_MY, ""),
    (
        "block_keep",
        _lines("# variant:typechecker=ty:begin", "kept = 1", "# variant:typechecker=ty:end"),
        A_TY,
        "kept = 1\n",
    ),
    (
        # Everything is dropped, but the input's trailing newline is
        # preserved — the same contract the original parser held.
        "block_drop",
        _lines("# variant:typechecker=mypy:begin", "gone = 1", "# variant:typechecker=mypy:end"),
        A_TY,
        "\n",
    ),
    (
        "two_blocks_ty",
        _lines(
            "# variant:typechecker=ty:begin",
            "ty_body = 1",
            "# variant:typechecker=ty:end",
            "# variant:typechecker=mypy:begin",
            "mypy_body = 1",
            "# variant:typechecker=mypy:end",
        ),
        A_TY,
        "ty_body = 1\n",
    ),
    (
        "two_blocks_mypy",
        _lines(
            "# variant:typechecker=ty:begin",
            "ty_body = 1",
            "# variant:typechecker=ty:end",
            "# variant:typechecker=mypy:begin",
            "mypy_body = 1",
            "# variant:typechecker=mypy:end",
        ),
        A_MY,
        "mypy_body = 1\n",
    ),
    (
        "empty_block",
        _lines("# variant:typechecker=ty:begin", "# variant:typechecker=ty:end"),
        A_TY,
        "\n",
    ),
    (
        "line_sentinel_in_kept_block_keep",
        _lines(
            "# variant:typechecker=ty:begin",
            "dep,  # variant:sbom=yes",
            "# variant:typechecker=ty:end",
        ),
        A_TY,
        "dep,\n",
    ),
    (
        "line_sentinel_in_kept_block_drop",
        _lines(
            "# variant:typechecker=ty:begin",
            "dep,  # variant:sbom=yes",
            "# variant:typechecker=ty:end",
        ),
        A_TY_NOSBOM,
        "\n",
    ),
    (
        "typo_in_dropped_block_no_raise",
        _lines(
            "# variant:typechecker=mypy:begin",
            "dep,  # variant:sbmo=yes",
            "# variant:typechecker=mypy:end",
        ),
        A_TY,
        "\n",
    ),
    ("no_sentinels_noop", "[tool.x]\nkey = 1\n", A_TY, "[tool.x]\nkey = 1\n"),
    ("trailing_newline_absent", "plain = 1", A_TY, "plain = 1"),
    ("trailing_newline_present", "plain = 1\n", A_TY, "plain = 1\n"),
    ("empty_input", "", A_TY, ""),
]


@pytest.mark.parametrize("prune,exc", IMPLS)
@pytest.mark.parametrize(
    "text,answers,expected",
    [pytest.param(t, a, e, id=n) for n, t, a, e in VALID_CASES],
)
def test_valid_output(prune, exc, text: str, answers: dict, expected: str) -> None:
    assert prune(text, answers) == expected


# --- Malformed input: raises VariantError ---------------------------------

RAISE_CASES = [
    # name, input, answers, message substring
    (
        "unknown_line_key",
        "x = 1  # variant:typo=ty",
        A_TY,
        "unknown variant key 'typo'",
    ),
    (
        "unknown_block_key",
        _lines("# variant:foo=bar:begin", "x", "# variant:foo=bar:end"),
        A_TY,
        "unknown variant key 'foo'",
    ),
    (
        "typo_in_kept_block",
        _lines(
            "# variant:typechecker=ty:begin",
            "dep,  # variant:sbmo=yes",
            "# variant:typechecker=ty:end",
        ),
        A_TY,
        "unknown variant key 'sbmo'",
    ),
    (
        "nested_in_kept_block",
        _lines(
            "# variant:typechecker=ty:begin",
            "# variant:sbom=yes:begin",
            "x",
            "# variant:sbom=yes:end",
            "# variant:typechecker=ty:end",
        ),
        A_TY,
        "nested variant block",
    ),
    (
        "nested_in_dropped_block",
        _lines(
            "# variant:typechecker=mypy:begin",
            "# variant:sbom=yes:begin",
            "x",
            "# variant:sbom=yes:end",
            "# variant:typechecker=mypy:end",
        ),
        A_TY,
        "nested variant block",
    ),
    (
        "end_without_begin",
        "# variant:typechecker=ty:end",
        A_TY,
        "unbalanced :end",
    ),
    (
        "mismatched_end",
        _lines("# variant:typechecker=ty:begin", "x", "# variant:typechecker=mypy:end"),
        A_TY,
        "unbalanced :end for 'typechecker=mypy'",
    ),
    (
        "unclosed_begin",
        _lines("# variant:typechecker=ty:begin", "x"),
        A_TY,
        "unclosed variant block",
    ),
]


@pytest.mark.parametrize("prune,exc", IMPLS)
@pytest.mark.parametrize(
    "text,answers,match",
    [pytest.param(t, a, m, id=n) for n, t, a, m in RAISE_CASES],
)
def test_malformed_raises(prune, exc, text: str, answers: dict, match: str) -> None:
    with pytest.raises(exc, match=match):
        prune(text, answers)


def test_variant_error_is_value_error() -> None:
    """Callers can catch either copy's error as a plain ``ValueError``."""
    assert issubclass(_pp.VariantError, ValueError)
    assert issubclass(_pg.VariantError, ValueError)


def test_both_impls_agree_on_a_batch() -> None:
    """Belt-and-braces: both copies produce identical output across cases."""
    for _name, text, answers, _expected in VALID_CASES:
        assert _pp.prune_text(text, answers) == _pg._prune_variants(text, answers)
