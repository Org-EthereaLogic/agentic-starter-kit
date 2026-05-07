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


def prune_text(text: str, answers: dict[str, str]) -> str:
    """Return ``text`` with non-matching variant blocks/lines removed."""
    out: list[str] = []
    skip_block: tuple[str, str] | None = None
    keep_block: tuple[str, str] | None = None
    trailing_newline = text.endswith("\n")

    for line in text.splitlines():
        begin = BLOCK_BEGIN.match(line)
        if begin:
            tag = (begin["key"], begin["val"])
            if answers.get(begin["key"]) == begin["val"]:
                keep_block = tag
            else:
                skip_block = tag
            continue

        end = BLOCK_END.match(line)
        if end:
            tag = (end["key"], end["val"])
            if skip_block == tag:
                skip_block = None
            elif keep_block == tag:
                keep_block = None
            continue

        if skip_block is not None:
            continue

        single = LINE_SENTINEL.match(line)
        if single:
            if answers.get(single["key"]) == single["val"]:
                out.append(single["content"].rstrip())
            continue

        out.append(line)

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
