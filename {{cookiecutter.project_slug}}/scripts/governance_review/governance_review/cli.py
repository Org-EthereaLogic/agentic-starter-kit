"""governance-review command-line entry point."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .checks import run_all
from .finding import Severity
from .formatters import format_json, format_sarif, format_text
from .registry import CHECKS


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="governance-review",
        description=(
            "Validate the agentic-starter-kit five-layer governance "
            "scaffold. Each finding has a stable GOV-NNN ID linking "
            "to docs/STANDARDS.md."
        ),
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Project root to scan (default: current working directory).",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json", "sarif"),
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--select",
        action="append",
        metavar="GOV-NNN",
        help="Run only the listed check IDs. Repeatable.",
    )
    parser.add_argument(
        "--list-checks",
        action="store_true",
        help="List all GOV-NNN check IDs with anchors and exit.",
    )
    parser.add_argument(
        "--warnings-as-errors",
        action="store_true",
        help="Treat warnings as exit-code-failing findings.",
    )
    parser.add_argument(
        "--no-warnings",
        action="store_true",
        help="Suppress warning findings entirely.",
    )
    return parser


def _print_check_inventory() -> int:
    for spec in CHECKS:
        print(f"{spec.id}  [{spec.severity.value:7}]  {spec.title}")
        print(f"          {spec.standards_link}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.list_checks:
        return _print_check_inventory()

    root = args.root.resolve()
    if not root.is_dir():
        print(f"governance-review: --root is not a directory: {root}", file=sys.stderr)
        return 2

    selected = set(args.select) if args.select else None
    if selected:
        known = {spec.id for spec in CHECKS}
        unknown = selected - known
        if unknown:
            print(
                "governance-review: unknown check id(s): " + ", ".join(sorted(unknown)),
                file=sys.stderr,
            )
            return 2

    findings = run_all(root, only=selected)

    if args.no_warnings:
        findings = [f for f in findings if f.severity is not Severity.WARNING]

    if args.format == "text":
        sys.stdout.write(format_text(findings))
    elif args.format == "json":
        sys.stdout.write(format_json(findings))
    elif args.format == "sarif":
        sys.stdout.write(format_sarif(findings))

    has_error = any(f.severity is Severity.ERROR for f in findings)
    has_warning = any(f.severity is Severity.WARNING for f in findings)
    if has_error:
        return 1
    if args.warnings_as_errors and has_warning:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
