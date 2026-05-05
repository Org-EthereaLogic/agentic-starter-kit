"""Output formatters: text, JSON, SARIF 2.1.0."""

from __future__ import annotations

import json
import sys
from collections.abc import Iterable
from typing import Any

from .finding import Finding, Severity
from .registry import CHECKS

SARIF_VERSION = "2.1.0"
SARIF_SCHEMA = (
    "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/Schemata/sarif-schema-2.1.0.json"
)
TOOL_INFO_URI = "docs/STANDARDS.md"


def _isatty() -> bool:
    return sys.stdout.isatty()


def _color(code: str, text: str) -> str:
    if not _isatty():
        return text
    return f"\033[{code}m{text}\033[0m"


def _severity_badge(sev: Severity) -> str:
    if sev is Severity.ERROR:
        return _color("31", "ERROR")
    if sev is Severity.WARNING:
        return _color("33", "WARN ")
    return _color("36", "NOTE ")


def format_text(findings: Iterable[Finding]) -> str:
    findings = list(findings)
    if not findings:
        return _color("32", "governance-review: OK") + " (no findings)\n"

    lines: list[str] = []
    for f in findings:
        loc = f.location or "."
        if f.line is not None:
            loc = f"{loc}:{f.line}"
        lines.append(
            f"{_severity_badge(f.severity)}  {f.id}  {loc}\n"
            f"          {f.message}\n"
            f"          see {f.standard_anchor} (docs/STANDARDS.md)"
        )

    summary = _summarize(findings)
    return "\n".join(lines) + f"\n\n{summary}\n"


def format_json(findings: Iterable[Finding]) -> str:
    payload = {
        "tool": {"name": "governance-review", "version": _tool_version()},
        "findings": [f.to_dict() for f in findings],
    }
    return json.dumps(payload, indent=2, sort_keys=False) + "\n"


def format_sarif(findings: Iterable[Finding]) -> str:
    findings = list(findings)
    rules = [
        {
            "id": spec.id,
            "name": _camel(spec.id),
            "shortDescription": {"text": spec.title},
            "fullDescription": {"text": spec.description},
            "defaultConfiguration": {"level": _sarif_level(spec.severity)},
            "helpUri": f"{TOOL_INFO_URI}#{spec.anchor}",
        }
        for spec in CHECKS
    ]
    rule_index = {spec.id: i for i, spec in enumerate(CHECKS)}

    results = []
    for f in findings:
        result: dict[str, Any] = {
            "ruleId": f.id,
            "ruleIndex": rule_index.get(f.id, 0),
            "level": _sarif_level(f.severity),
            "message": {"text": f.message},
        }
        if f.location:
            region: dict[str, Any] = {}
            if f.line is not None:
                region["startLine"] = f.line
            location: dict[str, Any] = {
                "physicalLocation": {
                    "artifactLocation": {"uri": f.location},
                }
            }
            if region:
                location["physicalLocation"]["region"] = region
            result["locations"] = [location]
        results.append(result)

    log = {
        "version": SARIF_VERSION,
        "$schema": SARIF_SCHEMA,
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "governance-review",
                        "version": _tool_version(),
                        "informationUri": TOOL_INFO_URI,
                        "rules": rules,
                    }
                },
                "results": results,
            }
        ],
    }
    return json.dumps(log, indent=2) + "\n"


def _summarize(findings: list[Finding]) -> str:
    errors = sum(1 for f in findings if f.severity is Severity.ERROR)
    warnings = sum(1 for f in findings if f.severity is Severity.WARNING)
    notes = sum(1 for f in findings if f.severity is Severity.NOTE)
    parts = [f"{errors} error(s)", f"{warnings} warning(s)"]
    if notes:
        parts.append(f"{notes} note(s)")
    label = _color("31", "FAILED") if errors else _color("33", "WARN")
    return f"governance-review {label} — " + ", ".join(parts)


def _sarif_level(sev: Severity) -> str:
    return {
        Severity.ERROR: "error",
        Severity.WARNING: "warning",
        Severity.NOTE: "note",
    }[sev]


def _camel(check_id: str) -> str:
    parts = check_id.replace("_", "-").split("-")
    return parts[0].lower() + "".join(p.capitalize() for p in parts[1:])


def _tool_version() -> str:
    from . import __version__

    return __version__
