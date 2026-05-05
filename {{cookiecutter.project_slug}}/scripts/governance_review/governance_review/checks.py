"""Check implementations.

Each `check_<id>` function ports the equivalent bash validator. They
all take a `Path` to the project root and return a list of `Finding`
objects. They never raise on user-input issues — those are reported as
findings — but they may raise on internal bugs (KeyError, etc.).
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from collections.abc import Callable, Iterator
from pathlib import Path

from .finding import Finding, Severity
from .registry import CheckSpec, find

CheckFn = Callable[[Path], list[Finding]]


# --- shared helpers -------------------------------------------------


def _spec(check_id: str) -> CheckSpec:
    spec = find(check_id)
    if spec is None:
        raise KeyError(f"unknown check id {check_id}")
    return spec


def _make(
    check_id: str,
    message: str,
    *,
    severity: Severity | None = None,
    location: str | None = None,
    line: int | None = None,
) -> Finding:
    spec = _spec(check_id)
    return Finding(
        id=spec.id,
        severity=severity or spec.severity,
        title=spec.title,
        message=message,
        standard_anchor=spec.anchor,
        location=location,
        line=line,
    )


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _frontmatter(text: str) -> dict[str, str]:
    """Return the YAML frontmatter as a flat string-keyed dict.

    Only the leading `---` block is considered. We parse manually to
    avoid a PyYAML dependency: the validator runs before `uv sync`.
    """
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    out: dict[str, str] = {}
    for raw in lines[1:]:
        if raw.strip() == "---":
            break
        match = re.match(r"^\s*([A-Za-z0-9_-]+)\s*:\s*(.*)$", raw)
        if not match:
            continue
        key, value = match.group(1), match.group(2).strip()
        if (
            len(value) >= 2
            and value[0] in ("'", '"')
            and value[-1] == value[0]
        ):
            value = value[1:-1]
        out[key] = value
    return out


# --- GOV-001 — stub markers -----------------------------------------


# Build the marker regex from concatenated halves so this file itself
# can pass a marker scan against its own source tree. The bash version
# uses the same trick.
_M = ["TO" + "DO", "FIX" + "ME", "TB" + "D", "PLACE" + "HOLDER"]
_MARKER_RE = re.compile(r"\b(" + "|".join(_M) + r")\b")

_MARKER_SURFACES = (
    "specs",
    ".claude",
    "CLAUDE.md",
    "AGENTS.md",
    "GEMINI.md",
    "docs",
)

# Skip vendored / build directories that may legitimately contain the
# marker words. Mirrors what `rg` would do via .gitignore.
_MARKER_SKIP_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "build",
    "dist",
    "report",
    "sbom",
}


def _walk_text_files(root: Path) -> Iterator[Path]:
    if root.is_file():
        yield root
        return
    if not root.is_dir():
        return
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in _MARKER_SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        yield path


def check_gov_001(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for surface in _MARKER_SURFACES:
        target = root / surface
        if not target.exists():
            continue
        for file in _walk_text_files(target):
            text = _read_text(file)
            if not text:
                continue
            for lineno, line in enumerate(text.splitlines(), start=1):
                match = _MARKER_RE.search(line)
                if match:
                    findings.append(
                        _make(
                            "GOV-001",
                            f"stub marker '{match.group(0)}' found",
                            location=str(file.relative_to(root)),
                            line=lineno,
                        )
                    )
    return findings


# --- GOV-002 — required files ---------------------------------------


_REQUIRED_FILES = (
    "CONSTITUTION.md",
    "DIRECTIVES.md",
    "SECURITY.md",
    "README.md",
    "CLAUDE.md",
    "AGENTS.md",
    "GEMINI.md",
    ".claude/settings.json",
    ".claude/hooks/pre-tool-use.js",
    ".mcp.json",
    "docs/MCP_POLICY.md",
)

_OPTIONAL_DIRS = (
    "docs",
    "specs/deep_specs",
    "specs/security-requirements",
    "report",
)


def check_gov_002(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for rel in _REQUIRED_FILES:
        if not (root / rel).is_file():
            findings.append(
                _make("GOV-002", f"required file missing: {rel}", location=rel)
            )

    for rel in _OPTIONAL_DIRS:
        if not (root / rel).is_dir():
            findings.append(
                _make(
                    "GOV-002",
                    f"optional directory not yet present: {rel}",
                    severity=Severity.WARNING,
                    location=rel,
                )
            )

    deep_specs = root / "specs" / "deep_specs"
    if deep_specs.is_dir() and not any(
        path.is_file()
        and path.suffix == ".md"
        and len(path.relative_to(deep_specs).parts) <= 2
        for path in deep_specs.rglob("*.md")
    ):
        findings.append(
            _make(
                "GOV-002",
                "specs/deep_specs contains no .md files yet",
                severity=Severity.WARNING,
                location="specs/deep_specs",
            )
        )
    return findings


# --- GOV-003 — .mcp.json structure ----------------------------------


def check_gov_003(root: Path) -> list[Finding]:
    mcp = root / ".mcp.json"
    if not mcp.is_file():
        return []  # GOV-002 already reports the absence
    try:
        data = json.loads(_read_text(mcp))
    except json.JSONDecodeError as exc:
        return [
            _make(
                "GOV-003",
                f".mcp.json is not valid JSON: {exc.msg}",
                location=".mcp.json",
                line=exc.lineno,
            )
        ]
    servers = data.get("mcpServers") if isinstance(data, dict) else None
    if not isinstance(servers, dict):
        return [
            _make(
                "GOV-003",
                ".mcp.json must contain a top-level 'mcpServers' object",
                location=".mcp.json",
            )
        ]
    return []


# --- GOV-004 — pre-tool-use hook -----------------------------------


def check_gov_004(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    hook = root / ".claude" / "hooks" / "pre-tool-use.js"
    settings = root / ".claude" / "settings.json"

    if hook.is_file() and hook.stat().st_size == 0:
        findings.append(
            _make(
                "GOV-004",
                ".claude/hooks/pre-tool-use.js is empty",
                location=".claude/hooks/pre-tool-use.js",
            )
        )
    # Missing hook is already reported by GOV-002.

    if settings.is_file():
        text = _read_text(settings)
        if "pre-tool-use.js" not in text:
            findings.append(
                _make(
                    "GOV-004",
                    ".claude/settings.json does not register pre-tool-use.js",
                    location=".claude/settings.json",
                )
            )
    return findings


# --- GOV-005 / GOV-006 / GOV-007 — agents --------------------------


_REQUIRED_AGENTS = (
    "lead-software-engineer.md",
    "sdlc-technical-writer.md",
    "test-automator.md",
    "ux-delight-specialist.md",
    "security-reviewer.md",
    "governance-auditor.md",
)
_AGENT_KEYS = ("name", "description", "model", "memory")


def _iter_frontmatter_files(base: Path) -> Iterator[tuple[Path, dict[str, str]]]:
    if not base.is_dir():
        return
    for path in sorted(base.glob("*.md")):
        if path.name == "README.md":
            continue
        yield path, _frontmatter(_read_text(path))


def check_gov_005(root: Path) -> list[Finding]:
    base = root / ".claude" / "agents"
    findings: list[Finding] = []
    for name in _REQUIRED_AGENTS:
        if not (base / name).is_file():
            findings.append(
                _make(
                    "GOV-005",
                    f"required agent missing: .claude/agents/{name}",
                    location=f".claude/agents/{name}",
                )
            )
    return findings


def check_gov_006(root: Path) -> list[Finding]:
    base = root / ".claude" / "agents"
    findings: list[Finding] = []
    for path, front in _iter_frontmatter_files(base):
        missing = [k for k in _AGENT_KEYS if k not in front]
        if missing:
            findings.append(
                _make(
                    "GOV-006",
                    f"agent missing frontmatter keys: {', '.join(missing)}",
                    location=str(path.relative_to(root)),
                )
            )
    return findings


def check_gov_007(root: Path) -> list[Finding]:
    base = root / ".claude" / "agents"
    if not base.is_dir():
        return []
    if (base / "python-pro.md").is_file() or (base / "typescript-pro.md").is_file():
        return []
    return [
        _make(
            "GOV-007",
            "no language-specific agent present "
            "(expected python-pro.md or typescript-pro.md)",
            location=".claude/agents/",
        )
    ]


# --- GOV-008 / GOV-009 — skills ------------------------------------


_REQUIRED_SKILLS = (
    "run-validate.md",
    "audit-trail-tail.md",
    "traceability-update.md",
)
_SKILL_KEYS = ("name", "description", "paths")


def check_gov_008(root: Path) -> list[Finding]:
    base = root / ".claude" / "skills"
    findings: list[Finding] = []
    for name in _REQUIRED_SKILLS:
        if not (base / name).is_file():
            findings.append(
                _make(
                    "GOV-008",
                    f"required skill missing: .claude/skills/{name}",
                    location=f".claude/skills/{name}",
                )
            )
    return findings


def check_gov_009(root: Path) -> list[Finding]:
    base = root / ".claude" / "skills"
    findings: list[Finding] = []
    for path, front in _iter_frontmatter_files(base):
        missing = [k for k in _SKILL_KEYS if k not in front]
        if missing:
            findings.append(
                _make(
                    "GOV-009",
                    f"skill missing frontmatter keys: {', '.join(missing)}",
                    location=str(path.relative_to(root)),
                )
            )
            continue
        expected = path.stem
        declared = front.get("name", "")
        if declared != expected:
            findings.append(
                _make(
                    "GOV-009",
                    f"skill frontmatter name '{declared}' does not match "
                    f"filename '{expected}'",
                    location=str(path.relative_to(root)),
                )
            )
    return findings


# --- GOV-010 / GOV-011 — traceability ------------------------------


def check_gov_010(root: Path) -> list[Finding]:
    matrix = root / "specs" / "traceability.json"
    if not matrix.is_file():
        return []
    try:
        json.loads(_read_text(matrix))
    except json.JSONDecodeError as exc:
        return [
            _make(
                "GOV-010",
                f"specs/traceability.json is not valid JSON: {exc.msg}",
                location="specs/traceability.json",
                line=exc.lineno,
            )
        ]

    schema_error = _validate_traceability_schema(root)
    if schema_error is not None:
        return [
            _make(
                "GOV-010",
                schema_error,
                location="specs/traceability.json",
            )
        ]
    return []


def _validate_traceability_schema(root: Path) -> str | None:
    schema = root / "specs" / "traceability.schema.json"
    matrix = root / "specs" / "traceability.json"
    if not schema.is_file():
        return None
    ajv = shutil.which("ajv")
    if ajv is None:
        return None
    try:
        result = subprocess.run(
            [ajv, "validate", "-s", str(schema), "-d", str(matrix), "--quiet"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if result.returncode == 0:
        return None
    return "specs/traceability.json does not conform to specs/traceability.schema.json"


def check_gov_011(root: Path) -> list[Finding]:
    matrix = root / "specs" / "traceability.json"
    if not matrix.is_file():
        return []
    try:
        data = json.loads(_read_text(matrix))
    except json.JSONDecodeError:
        return []  # GOV-010 already reported it
    if not isinstance(data, dict):
        return []

    criteria = data.get("criteria", [])
    if not isinstance(criteria, list):
        return []

    findings: list[Finding] = []
    for criterion in criteria:
        if not isinstance(criterion, dict):
            continue
        cid = criterion.get("id", "<unknown>")
        for glob in criterion.get("source", []):
            if not _glob_resolves(root, glob):
                findings.append(
                    _make(
                        "GOV-011",
                        f"criterion {cid} source glob matches no files: {glob}",
                        location="specs/traceability.json",
                    )
                )
        for glob in criterion.get("tests", []):
            if not _glob_resolves(root, glob):
                findings.append(
                    _make(
                        "GOV-011",
                        f"criterion {cid} tests glob matches no files: {glob}",
                        location="specs/traceability.json",
                    )
                )
        for path in criterion.get("evidence", []):
            if not (root / path).exists():
                findings.append(
                    _make(
                        "GOV-011",
                        f"criterion {cid} evidence file missing: {path}",
                        location="specs/traceability.json",
                    )
                )
    return findings


def _glob_resolves(root: Path, pattern: str) -> bool:
    try:
        return any(True for _ in root.glob(pattern))
    except (OSError, ValueError):
        return False


# --- GOV-012 — doc drift -------------------------------------------


_DOC_PATH_RE = re.compile(
    r"`([A-Za-z0-9_./-]+\.(?:md|json|sh|js|py|ts|yml|yaml|toml|cff))`"
)


def check_gov_012(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    seen: set[tuple[str, str]] = set()
    for sub in ("docs", "specs"):
        base = root / sub
        if not base.is_dir():
            continue
        for md in sorted(base.rglob("*.md")):
            text = _read_text(md)
            for lineno, line in enumerate(text.splitlines(), start=1):
                for match in _DOC_PATH_RE.finditer(line):
                    path = match.group(1)
                    if path in (".", "..") or path.startswith(("/", "http://", "https://")):
                        continue
                    rel = str(md.relative_to(root))
                    key = (rel, path)
                    if key in seen:
                        continue
                    if not (root / path).exists() and not (md.parent / path).exists():
                        seen.add(key)
                        findings.append(
                            _make(
                                "GOV-012",
                                f"referenced path does not exist: {path}",
                                location=rel,
                                line=lineno,
                            )
                        )
    return findings


# --- runner ---------------------------------------------------------

ALL_CHECKS: tuple[tuple[str, CheckFn], ...] = (
    ("GOV-001", check_gov_001),
    ("GOV-002", check_gov_002),
    ("GOV-003", check_gov_003),
    ("GOV-004", check_gov_004),
    ("GOV-005", check_gov_005),
    ("GOV-006", check_gov_006),
    ("GOV-007", check_gov_007),
    ("GOV-008", check_gov_008),
    ("GOV-009", check_gov_009),
    ("GOV-010", check_gov_010),
    ("GOV-011", check_gov_011),
    ("GOV-012", check_gov_012),
)


def run_all(root: Path, *, only: set[str] | None = None) -> list[Finding]:
    out: list[Finding] = []
    for cid, fn in ALL_CHECKS:
        if only is not None and cid not in only:
            continue
        out.extend(fn(root))
    return out
