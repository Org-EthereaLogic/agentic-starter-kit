#!/usr/bin/env python3
"""Governance rules loader and query interface.

Provides programmatic access to governance-rules.yaml for agents, CI/CD,
and audit workflows.
"""
# ruff: noqa: E501  Line length relaxed for readability of help text

import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed; run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


class GovernanceRules:
    """Load and query governance rules from YAML."""

    def __init__(self, rules_file: Path = Path("governance-rules.yaml")):
        """Initialize with path to governance-rules.yaml."""
        if not rules_file.exists():
            raise FileNotFoundError(f"Governance rules file not found: {rules_file}")

        with open(rules_file) as f:
            self.data = yaml.safe_load(f)

        self.directives = {d["id"]: d for d in self.data.get("directives", [])}

    def get_directive(self, directive_id: str) -> dict[str, Any] | None:
        """Get a single directive by ID."""
        return self.directives.get(directive_id)

    def get_by_class(self, class_name: str) -> list[dict[str, Any]]:
        """Get all directives in a class (Critical, Important, Recommended)."""
        return [d for d in self.data.get("directives", []) if d["class"] == class_name]

    def get_all_critical(self) -> list[dict[str, Any]]:
        """Get all Critical directives."""
        return self.get_by_class("Critical")

    def get_all_important(self) -> list[dict[str, Any]]:
        """Get all Important directives."""
        return self.get_by_class("Important")

    def get_all_recommended(self) -> list[dict[str, Any]]:
        """Get all Recommended directives."""
        return self.get_by_class("Recommended")

    def get_enabled_directives(self) -> list[dict[str, Any]]:
        """Get all enabled directives."""
        return [d for d in self.data.get("directives", []) if d.get("enabled", True)]

    def get_by_enforcement_type(self, enforcement_type: str) -> list[dict[str, Any]]:
        """Get directives enforced by a specific type (script, hook, reviewer, etc)."""
        enforcement_map = self.data.get("enforcement_by_type", {}).get(enforcement_type, [])
        return [self.directives[item["id"]] for item in enforcement_map if item.get("id") in self.directives]

    def get_automated_directives(self) -> list[dict[str, Any]]:
        """Get directives that are automated (script or hook)."""
        script_based = self.get_by_enforcement_type("script")
        hook_based = self.get_by_enforcement_type("hook")
        return list({d["id"]: d for d in script_based + hook_based}.values())

    def validate_file(self) -> bool:
        """Validate the YAML structure."""
        required_sections = ["directives", "critical", "important", "recommended"]
        for section in required_sections:
            if section not in self.data:
                print(f"ERROR: Missing required section: {section}", file=sys.stderr)
                return False

        # Check that directive counts match
        critical_count = len(self.get_all_critical())
        important_count = len(self.get_all_important())
        recommended_count = len(self.get_all_recommended())

        if critical_count != self.data["critical"]["count"]:
            print(f"ERROR: Critical count mismatch: {critical_count} vs {self.data['critical']['count']}", file=sys.stderr)
            return False

        if important_count != self.data["important"]["count"]:
            print(f"ERROR: Important count mismatch: {important_count} vs {self.data['important']['count']}", file=sys.stderr)
            return False

        if recommended_count != self.data["recommended"]["count"]:
            print(f"ERROR: Recommended count mismatch: {recommended_count} vs {self.data['recommended']['count']}", file=sys.stderr)
            return False

        return True

    def to_json(self) -> str:
        """Export all governance rules as JSON."""
        return json.dumps(self.data, indent=2)

    def summary(self) -> str:
        """Return a human-readable summary of all rules."""
        lines = ["# Governance Rules Summary", ""]

        for class_name in ["Critical", "Important", "Recommended"]:
            directives = self.get_by_class(class_name)
            lines.append(f"## {class_name} ({len(directives)})")
            lines.append("")
            for d in directives:
                lines.append(f"- **{d['id']}**: {d['title']}")
            lines.append("")

        return "\n".join(lines)


def main():
    """CLI for governance rules queries."""
    import argparse

    parser = argparse.ArgumentParser(description="Query governance rules")
    parser.add_argument("--file", default="governance-rules.yaml", help="Path to governance-rules.yaml")
    parser.add_argument("--list", action="store_true", help="List all directives")
    parser.add_argument("--class", dest="class_name", help="Filter by class (Critical, Important, Recommended)")
    parser.add_argument("--enabled", action="store_true", help="Show only enabled directives")
    parser.add_argument("--automated", action="store_true", help="Show only automated directives")
    parser.add_argument("--id", help="Get a specific directive by ID")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--validate", action="store_true", help="Validate the rules file")
    parser.add_argument("--summary", action="store_true", help="Show summary")

    args = parser.parse_args()

    try:
        rules = GovernanceRules(Path(args.file))
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if args.validate:
        if rules.validate_file():
            print("✓ Governance rules file is valid")
            sys.exit(0)
        else:
            sys.exit(1)

    if args.summary:
        print(rules.summary())
        sys.exit(0)

    if args.id:
        directive = rules.get_directive(args.id)
        if directive:
            print(json.dumps(directive, indent=2) if args.json else f"{directive['id']}: {directive['title']}")
            sys.exit(0)
        else:
            print(f"ERROR: Directive not found: {args.id}", file=sys.stderr)
            sys.exit(1)

    directives = rules.get_enabled_directives() if args.enabled else rules.data["directives"]

    if args.class_name:
        directives = [d for d in directives if d["class"] == args.class_name]

    if args.automated:
        automated_ids = {d["id"] for d in rules.get_automated_directives()}
        directives = [d for d in directives if d["id"] in automated_ids]

    if args.json:
        print(json.dumps(directives, indent=2))
    else:
        for d in directives:
            status = "✓" if d.get("enabled", True) else "○"
            print(f"{status} {d['id']:8} [{d['class']:11}] {d['title']}")


if __name__ == "__main__":
    main()
