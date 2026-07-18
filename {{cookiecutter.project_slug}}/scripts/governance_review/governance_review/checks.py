"""Check implementations.

Each `check_<id>` function ports the equivalent bash validator. They
all take a `Path` to the project root and return a list of `Finding`
objects. They never raise on user-input issues — those are reported as
findings — but they may raise on internal bugs (KeyError, etc.).
"""

from __future__ import annotations

import json
import re
import shlex
import shutil
import subprocess
from collections.abc import Callable, Iterator
from pathlib import Path

from .finding import Finding, Severity
from .governance import GovernanceRules, GovernanceRulesError
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
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
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


def check_gov_001(root: Path, rules: GovernanceRules | None = None) -> list[Finding]:
    rules = rules or GovernanceRules.load(root)
    marker_re = re.compile(
        r"\b(" + "|".join(re.escape(marker) for marker in rules.markers) + r")\b"
    )
    findings: list[Finding] = []
    for surface in rules.marker_surfaces:
        target = root / surface
        if not target.exists():
            continue
        for file in _walk_text_files(target):
            text = _read_text(file)
            if not text:
                continue
            for lineno, line in enumerate(text.splitlines(), start=1):
                match = marker_re.search(line)
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


def check_gov_002(root: Path, rules: GovernanceRules | None = None) -> list[Finding]:
    rules = rules or GovernanceRules.load(root)
    findings: list[Finding] = []
    for rel in rules.required_files:
        if not (root / rel).is_file():
            findings.append(
                _make("GOV-002", f"required file missing: {rel}", location=rel)
            )

    for rel in rules.optional_dirs:
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


def _invokes_pre_tool_hook(command: str) -> bool:
    """Return whether a simple command actually invokes the shipped hook."""
    try:
        tokens = shlex.split(command, comments=True, posix=True)
    except ValueError:
        return False
    while tokens and "=" in tokens[0] and not tokens[0].startswith(("=", "-")):
        name, _, _value = tokens[0].partition("=")
        if not name.replace("_", "a").isalnum() or name[0].isdigit():
            break
        tokens.pop(0)
    if len(tokens) < 2:
        return False
    runtime = Path(tokens[0]).name
    return runtime in {"node", "nodejs"} and tokens[1] == ".claude/hooks/pre-tool-use.js"


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
        try:
            data = json.loads(_read_text(settings))
        except json.JSONDecodeError as exc:
            findings.append(
                _make(
                    "GOV-004",
                    f".claude/settings.json is not valid JSON: {exc.msg}",
                    location=".claude/settings.json",
                    line=exc.lineno,
                )
            )
            return findings
        hooks = data.get("hooks") if isinstance(data, dict) else None
        pre_tool_use = hooks.get("PreToolUse") if isinstance(hooks, dict) else None
        commands: list[str] = []
        if isinstance(pre_tool_use, list):
            for registration in pre_tool_use:
                if not isinstance(registration, dict) or registration.get("matcher") != "Bash":
                    continue
                hooks = registration.get("hooks")
                if not isinstance(hooks, list):
                    continue
                for nested in hooks:
                    if (
                        isinstance(nested, dict)
                        and nested.get("type") == "command"
                        and isinstance(nested.get("command"), str)
                    ):
                        commands.append(nested["command"])
        if not any(_invokes_pre_tool_hook(command) for command in commands):
            findings.append(
                _make(
                    "GOV-004",
                    ".claude/settings.json does not structurally register "
                    "pre-tool-use.js under hooks.PreToolUse",
                    location=".claude/settings.json",
                )
            )
    return findings


# --- GOV-005 / GOV-006 / GOV-007 — agents --------------------------


_AGENT_KEYS = ("name", "description", "model", "memory")


def _iter_frontmatter_files(base: Path) -> Iterator[tuple[Path, dict[str, str]]]:
    if not base.is_dir():
        return
    for path in sorted(base.glob("*.md")):
        if path.name == "README.md":
            continue
        yield path, _frontmatter(_read_text(path))


def check_gov_005(root: Path, rules: GovernanceRules | None = None) -> list[Finding]:
    rules = rules or GovernanceRules.load(root)
    findings: list[Finding] = []
    for rel in rules.required_agents:
        if not (root / rel).is_file():
            findings.append(
                _make(
                    "GOV-005",
                    f"required agent missing: {rel}",
                    location=rel,
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


_SKILL_KEYS = ("name", "description", "paths")


def check_gov_008(root: Path, rules: GovernanceRules | None = None) -> list[Finding]:
    rules = rules or GovernanceRules.load(root)
    findings: list[Finding] = []
    for rel in rules.required_skills:
        if not (root / rel).is_file():
            findings.append(
                _make(
                    "GOV-008",
                    f"required skill missing: {rel}",
                    location=rel,
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
        data = json.loads(_read_text(matrix))
    except json.JSONDecodeError as exc:
        return [
            _make(
                "GOV-010",
                f"specs/traceability.json is not valid JSON: {exc.msg}",
                location="specs/traceability.json",
                line=exc.lineno,
            )
        ]

    if not isinstance(data, dict):
        return [_make("GOV-010", "specs/traceability.json root must be an object", location="specs/traceability.json")]
    criteria = data.get("criteria")
    if not isinstance(criteria, list):
        return [
            _make(
                "GOV-010",
                "specs/traceability.json field 'criteria' must be a list",
                location="specs/traceability.json",
            )
        ]
    for index, criterion in enumerate(criteria):
        if not isinstance(criterion, dict):
            return [
                _make(
                    "GOV-010",
                    f"specs/traceability.json criteria[{index}] must be an object",
                    location="specs/traceability.json",
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
        collections: dict[str, list[object]] = {}
        for field in ("source", "tests", "evidence"):
            value = criterion.get(field, [])
            if not isinstance(value, list):
                findings.append(
                    _make(
                        "GOV-011",
                        f"criterion {cid} field '{field}' must be a list",
                        location="specs/traceability.json",
                    )
                )
                collections[field] = []
            else:
                collections[field] = value
        for glob in collections["source"]:
            if not isinstance(glob, str):
                findings.append(
                    _make(
                        "GOV-011",
                        f"criterion {cid} source entry must be a string",
                        location="specs/traceability.json",
                    )
                )
                continue
            if not _glob_resolves(root, glob):
                findings.append(
                    _make(
                        "GOV-011",
                        f"criterion {cid} source glob matches no files: {glob}",
                        location="specs/traceability.json",
                    )
                )
        for glob in collections["tests"]:
            if not isinstance(glob, str):
                findings.append(
                    _make(
                        "GOV-011",
                        f"criterion {cid} tests entry must be a string",
                        location="specs/traceability.json",
                    )
                )
                continue
            if not _glob_resolves(root, glob):
                findings.append(
                    _make(
                        "GOV-011",
                        f"criterion {cid} tests glob matches no files: {glob}",
                        location="specs/traceability.json",
                    )
                )
        for path in collections["evidence"]:
            if not isinstance(path, str):
                findings.append(
                    _make(
                        "GOV-011",
                        f"criterion {cid} evidence entry must be a string",
                        location="specs/traceability.json",
                    )
                )
                continue
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
    try:
        rules = GovernanceRules.load(root)
    except GovernanceRulesError as exc:
        return [
            _make(
                "GOV-002",
                str(exc),
                severity=Severity.ERROR,
                location="governance-rules.yaml",
            )
        ]
    for cid, fn in ALL_CHECKS:
        if only is not None and cid not in only:
            continue
        if cid == "GOV-001":
            out.extend(check_gov_001(root, rules))
        elif cid == "GOV-002":
            out.extend(check_gov_002(root, rules))
        elif cid == "GOV-005":
            out.extend(check_gov_005(root, rules))
        elif cid == "GOV-008":
            out.extend(check_gov_008(root, rules))
        else:
            out.extend(fn(root))
    return out
