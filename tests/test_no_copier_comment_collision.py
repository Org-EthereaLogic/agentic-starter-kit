"""Guard against the copier comment-delimiter collision (issue #133).

``copier.yml`` sets a custom Jinja comment-start via
``_envops.comment_start_string`` (currently ``[#``) so that bash length
expansions like ``${#arr[@]}`` in rendered shell scripts are not parsed as
Jinja comments. The cost: that delimiter must then appear *nowhere* as
literal text in the template tree, or copier reads it as the start of a
comment that never closes and aborts the entire render with
``TemplateSyntaxError: Missing end of comment tag``.

Issue #133 was exactly this — a markdown issue-link ``[#102](...)`` in
``DIRECTIVES.md`` (and ``.claude/hooks/README.md``) opened a copier comment
that never closed, so *every* copier render failed while cookiecutter
(default ``{#`` delimiter) rendered fine. This test fails loudly the moment
the delimiter is reintroduced as literal text, so the collision cannot
silently return and re-break copier CI.

No third-party deps (PyYAML is not in the minimal CI test env): the
delimiter is parsed from ``copier.yml`` with a regex.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_ROOT = REPO_ROOT / "{{cookiecutter.project_slug}}"


def _copier_comment_start() -> str:
    """Read ``_envops.comment_start_string`` from copier.yml (regex, no yaml dep)."""
    text = (REPO_ROOT / "copier.yml").read_text(encoding="utf-8")
    match = re.search(r'comment_start_string:\s*"([^"]+)"', text)
    # cookiecutter's default ``{#`` needs no guarding; only a custom copier
    # delimiter can collide with otherwise-valid template content.
    return match.group(1) if match else "{#"


def test_copier_comment_start_absent_from_template() -> None:
    delimiter = _copier_comment_start()
    if delimiter == "{#":
        return  # default Jinja comment; nothing to guard.

    offenders: list[str] = []
    for path in sorted(TEMPLATE_ROOT.rglob("*")):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue  # binary/unreadable — copier does not Jinja-parse it as text
        for lineno, line in enumerate(text.splitlines(), 1):
            if delimiter in line:
                rel = path.relative_to(REPO_ROOT)
                offenders.append(f"{rel}:{lineno}: {line.strip()[:100]}")

    assert not offenders, (
        f"copier comment-start {delimiter!r} found as literal text in the "
        f"template tree; copier will read it as an unclosed comment and abort "
        f"the render (issue #133). Escape it (e.g. a markdown '[#NNN]' link -> "
        f"'[issue #NNN]'):\n" + "\n".join(offenders)
    )
