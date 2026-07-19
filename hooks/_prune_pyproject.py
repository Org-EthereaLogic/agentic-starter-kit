#!/usr/bin/env python3
"""Strip variant-tagged content from a rendered ``pyproject.toml``.

The template ships a single, valid-TOML ``pyproject.toml`` with all
type-checker sections and dev dependencies present, tagged by
sentinel comments. This script removes the lines and blocks that
don't match the answers chosen at render time.

Sentinels:
  Line:  ``... # variant:KEY=VAL``
         Drop the line if ``answers[KEY] != VAL``; otherwise keep
         the content and strip the trailing sentinel comment.
  Block: ``# variant:KEY=VAL:begin`` ... ``# variant:KEY=VAL:end``
         Drop the entire range (including markers) if
         ``answers[KEY] != VAL``; otherwise keep the contents and
         strip the marker lines.

Copier invokes this script directly via a ``_tasks`` entry in
``copier.yml``. Cookiecutter cannot import sibling files from its
post-gen hook (the hook is copied into a temp dir without access
to ``hooks/``), so ``hooks/post_gen_project.py`` ships a duplicate
of the parsing logic; keep both in sync. The script is a no-op on
files without sentinels, so it's safe to run repeatedly.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Variant values may contain dots and hyphens (e.g. version numbers
# or slugified names) in addition to word characters.
LINE_SENTINEL = re.compile(r"^(?P<content>.*?)\s*#\s*variant:(?P<key>\w+)=(?P<val>[\w.-]+)\s*$")
BLOCK_BEGIN = re.compile(r"^\s*#\s*variant:(?P<key>\w+)=(?P<val>[\w.-]+):begin\s*$")
BLOCK_END = re.compile(r"^\s*#\s*variant:(?P<key>\w+)=(?P<val>[\w.-]+):end\s*$")


class VariantError(ValueError):
    """A variant sentinel is malformed (unknown key, nested/unbalanced block)."""


def _require_known(key: str, answers: dict[str, str], lineno: int) -> None:
    """Raise ``VariantError`` if ``key`` is not a recognised answer key.

    A sentinel naming an unknown key (a future variant not yet wired in,
    or a typo like ``typecheker``) would otherwise silently drop content
    from *every* render; failing loudly turns that into a caught bug.
    """
    if key not in answers:
        raise VariantError(
            f"line {lineno}: unknown variant key '{key}' "
            f"(known: {sorted(answers)})"
        )


def prune_text(text: str, answers: dict[str, str]) -> str:
    """Return ``text`` with non-matching variant blocks/lines removed.

    Raises ``VariantError`` on a malformed sentinel: an unknown key, a
    nested block (nesting is not part of the contract), or an unbalanced
    ``:begin``/``:end`` marker. Structural markers are validated even
    inside a dropped block, so imbalance/nesting is always caught; an
    inline sentinel inside a dropped block is unreachable (the whole
    block is discarded) and needs no validation.
    """
    out: list[str] = []
    active: tuple[str, str, bool] | None = None  # (key, val, keep)
    trailing_newline = text.endswith("\n")

    for lineno, line in enumerate(text.splitlines(), 1):
        begin = BLOCK_BEGIN.match(line)
        if begin:
            key, val = begin["key"], begin["val"]
            _require_known(key, answers, lineno)
            if active is not None:
                raise VariantError(
                    f"line {lineno}: nested variant block '{key}={val}' "
                    f"inside open '{active[0]}={active[1]}'"
                )
            active = (key, val, answers[key] == val)
            continue

        end = BLOCK_END.match(line)
        if end:
            key, val = end["key"], end["val"]
            _require_known(key, answers, lineno)
            if active is None or (active[0], active[1]) != (key, val):
                raise VariantError(
                    f"line {lineno}: unbalanced :end for '{key}={val}'"
                )
            active = None
            continue

        if active is not None and not active[2]:  # inside a dropped block
            continue

        single = LINE_SENTINEL.match(line)
        if single:
            key, val = single["key"], single["val"]
            _require_known(key, answers, lineno)
            if answers[key] == val:
                out.append(single["content"].rstrip())
            continue

        out.append(line)

    if active is not None:
        raise VariantError(
            f"unclosed variant block '{active[0]}={active[1]}:begin'"
        )

    return "\n".join(out) + ("\n" if trailing_newline else "")


def prune_file(path: Path, answers: dict[str, str]) -> bool:
    """Prune ``path`` in place. Returns True when the file was rewritten."""
    if not path.exists():
        return False
    original = path.read_text()
    pruned = prune_text(original, answers)
    if pruned != original:
        path.write_text(pruned)
    return pruned != original


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "target",
        nargs="?",
        default="pyproject.toml",
        help="Path to the pyproject.toml to prune (default: ./pyproject.toml).",
    )
    parser.add_argument("--typechecker", required=True, choices=["ty", "mypy"])
    parser.add_argument("--include-sbom", required=True, choices=["yes", "no"])
    args = parser.parse_args(argv)

    answers = {"typechecker": args.typechecker, "sbom": args.include_sbom}
    target = Path(args.target)
    if not target.exists():
        # The pyproject.toml may have been pruned by the language gate
        # (e.g. typescript-only render). That's a no-op, not an error.
        return 0
    prune_file(target, answers)
    return 0


if __name__ == "__main__":
    sys.exit(main())
