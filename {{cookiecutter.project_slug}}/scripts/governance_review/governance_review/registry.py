"""Stable GOV-NNN check registry.

Each entry binds an ID to its title, severity, and the anchor in
`docs/STANDARDS.md` that explains the rule. The check function itself
is registered separately in `checks.py` so the registry stays a pure
data table.
"""

from __future__ import annotations

from dataclasses import dataclass

from .finding import Severity


@dataclass(frozen=True)
class CheckSpec:
    id: str
    title: str
    severity: Severity
    anchor: str
    description: str

    @property
    def standards_link(self) -> str:
        return f"docs/STANDARDS.md#{self.anchor}"


CHECKS: list[CheckSpec] = [
    CheckSpec(
        id="GOV-001",
        title="No stub markers in canonical surfaces",
        severity=Severity.ERROR,
        anchor="gov-001-stub-markers",
        description=(
            "Canonical surfaces (specs/, .claude/, CLAUDE.md, AGENTS.md, "
            "GEMINI.md, docs/) must not contain TODO / FIXME / TBD / "
            "PLACEHOLDER. Replaces marker-scan.sh."
        ),
    ),
    CheckSpec(
        id="GOV-002",
        title="Required governance files exist",
        severity=Severity.ERROR,
        anchor="gov-002-required-files",
        description=(
            "Layer 1, 2, and 4 anchor files must be present at canonical "
            "paths on every commit. Replaces the required_files block of "
            "check-governance.sh."
        ),
    ),
    CheckSpec(
        id="GOV-003",
        title=".mcp.json has top-level mcpServers object",
        severity=Severity.ERROR,
        anchor="gov-003-mcp-structure",
        description=(
            "The MCP server registry must parse as JSON and expose an "
            "`mcpServers` object at the top level. See docs/MCP_POLICY.md."
        ),
    ),
    CheckSpec(
        id="GOV-004",
        title="pre-tool-use hook is registered and non-empty",
        severity=Severity.ERROR,
        anchor="gov-004-pretool-hook",
        description=(
            "Layer 4 runtime hook must exist, be non-empty, and be "
            "referenced from .claude/settings.json. Enforces CRIT-008."
        ),
    ),
    CheckSpec(
        id="GOV-005",
        title="Required Claude agents exist",
        severity=Severity.ERROR,
        anchor="gov-005-required-agents",
        description=(
            "The six baseline Claude agents (lead-software-engineer, "
            "sdlc-technical-writer, test-automator, ux-delight-specialist, "
            "security-reviewer, governance-auditor) must ship in "
            ".claude/agents/."
        ),
    ),
    CheckSpec(
        id="GOV-006",
        title="Agent frontmatter is complete",
        severity=Severity.ERROR,
        anchor="gov-006-agent-frontmatter",
        description=(
            "Every .claude/agents/*.md file must declare name, description, "
            "model, and memory in YAML frontmatter."
        ),
    ),
    CheckSpec(
        id="GOV-007",
        title="Language-specific agent is present",
        severity=Severity.ERROR,
        anchor="gov-007-language-agent",
        description=(
            "At least one of python-pro.md or typescript-pro.md must be "
            "present in .claude/agents/."
        ),
    ),
    CheckSpec(
        id="GOV-008",
        title="Required Claude skills exist",
        severity=Severity.ERROR,
        anchor="gov-008-required-skills",
        description=(
            "Starter skills (run-validate, audit-trail-tail, "
            "traceability-update) must ship in .claude/skills/."
        ),
    ),
    CheckSpec(
        id="GOV-009",
        title="Skill frontmatter is complete and matches filename",
        severity=Severity.ERROR,
        anchor="gov-009-skill-frontmatter",
        description=(
            "Every .claude/skills/*.md file must declare name, description, "
            "and paths. The frontmatter `name` must equal the filename stem."
        ),
    ),
    CheckSpec(
        id="GOV-010",
        title="Traceability matrix parses as JSON and matches schema",
        severity=Severity.ERROR,
        anchor="gov-010-traceability-json",
        description=(
            "When specs/traceability.json exists it must be valid JSON. "
            "When specs/traceability.schema.json and ajv are available, "
            "the matrix must also conform to the schema. Skipped before "
            "Phase 8 ships the matrix."
        ),
    ),
    CheckSpec(
        id="GOV-011",
        title="Traceability source / tests / evidence resolve",
        severity=Severity.ERROR,
        anchor="gov-011-traceability-resolve",
        description=(
            "Every criterion in the traceability matrix must have its "
            "source globs, tests globs, and evidence paths resolve to "
            "real files in the working tree."
        ),
    ),
    CheckSpec(
        id="GOV-012",
        title="Documentation references resolve",
        severity=Severity.WARNING,
        anchor="gov-012-doc-drift",
        description=(
            "Backtick-wrapped path-like tokens in docs/ and specs/ must "
            "exist on disk. Reported as warnings until the project opts "
            "into block mode."
        ),
    ),
]


def find(check_id: str) -> CheckSpec | None:
    for spec in CHECKS:
        if spec.id == check_id:
            return spec
    return None
