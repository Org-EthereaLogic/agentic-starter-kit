"""Integration test for the cookiecutter post-gen pruning hook.

Renders the template into temp directories across the
``primary_language`` and ``include_*`` flag matrix and asserts that
``hooks/post_gen_project.py`` keeps the right files and removes the
rest. Lives at the repo root so it is excluded from the rendered
project tree.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

TEMPLATE_ROOT = Path(__file__).resolve().parent.parent


def _default_rendered_slug() -> str:
    """Derive the rendered project directory name from cookiecutter defaults.

    Mirrors the Jinja expression in ``cookiecutter.json``'s
    ``project_slug``: ``project_name|lower|replace(' ', '-')|replace('_', '-')``.
    Reading it from the JSON keeps the test resilient to future renames of
    the default ``project_name``.
    """
    config = json.loads((TEMPLATE_ROOT / "cookiecutter.json").read_text())
    project_name = config["project_name"]
    return project_name.lower().replace(" ", "-").replace("_", "-")


RENDERED_SLUG = _default_rendered_slug()

LANGUAGE_MATRIX: dict[str, dict[str, tuple[str, ...]]] = {
    "python": {
        "present": (
            "pyproject.toml",
            "tests/test_pre_tool_use_hook.py",
            "tests/test_audit_hooks.py",
            "tests/test_governance_review.py",
            "tests/test_governance_loader.py",
            ".claude/agents/python-pro.md",
            "QUICKSTART-PYTHON.md",
        ),
        "absent": (
            "package.json",
            "tsconfig.json",
            "tests/test_pre_tool_use_hook.js",
            "tests/test_audit_hooks.cjs",
            ".claude/agents/typescript-pro.md",
            "QUICKSTART-TYPESCRIPT.md",
        ),
    },
    "typescript": {
        "present": (
            "package.json",
            "tsconfig.json",
            "tests/test_pre_tool_use_hook.js",
            "tests/test_audit_hooks.cjs",
            ".claude/agents/typescript-pro.md",
            "QUICKSTART-TYPESCRIPT.md",
        ),
        "absent": (
            "pyproject.toml",
            "tests/test_pre_tool_use_hook.py",
            "tests/test_audit_hooks.py",
            "tests/test_governance_review.py",
            "tests/test_governance_loader.py",
            ".claude/agents/python-pro.md",
            "QUICKSTART-PYTHON.md",
        ),
    },
    "polyglot": {
        "present": (
            "pyproject.toml",
            "package.json",
            "tsconfig.json",
            "tests/test_pre_tool_use_hook.py",
            "tests/test_pre_tool_use_hook.js",
            "tests/test_audit_hooks.py",
            "tests/test_audit_hooks.cjs",
            "tests/test_governance_review.py",
            "tests/test_governance_loader.py",
            ".claude/agents/python-pro.md",
            ".claude/agents/typescript-pro.md",
            "QUICKSTART-PYTHON.md",
            "QUICKSTART-TYPESCRIPT.md",
        ),
        "absent": (),
    },
}

# Flag → paths the post-gen hook removes when the flag is "no".
# When the flag is "yes" the same paths must remain in the rendered tree.
INCLUDE_FLAG_PATHS: dict[str, tuple[str, ...]] = {
    "include_codacy": (".codacy.yml",),
    "include_codecov": ("codecov.yaml",),
    "include_snyk": (".snyk",),
    "include_sbom": ("scripts/generate-sbom.sh", "docs/sbom-policy.md"),
    "include_devcontainer": (".devcontainer", "Dockerfile", ".dockerignore"),
    "include_docs_site": (
        "mkdocs.yml",
        "docs/index.md",
        ".github/workflows/docs.yml",
    ),
    "include_release_automation": (
        ".cz.toml",
        "release-please-config.json",
        "release-please-manifest.json",
        ".github/workflows/release-please.yml",
    ),
    "include_promptfoo": (
        "prompts",
        "evals",
        "docs/prompt-versioning-policy.md",
        "Makefile.fragments/evals.mk",
    ),
}


def _render(output_dir: Path, **overrides: str) -> Path:
    """Render the template via cookiecutter and return the project dir.

    Uses ``-f`` so a stale rendered directory at the same path is
    overwritten, mirroring how the smoke-test workflow invokes
    cookiecutter.
    """
    cmd = [
        sys.executable,
        "-m",
        "cookiecutter",
        str(TEMPLATE_ROOT),
        "--no-input",
        "-f",
        "--output-dir",
        str(output_dir),
        *(f"{k}={v}" for k, v in overrides.items()),
    ]
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        pytest.fail(
            "cookiecutter render failed\n"
            f"command: {' '.join(cmd)}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
    return output_dir / RENDERED_SLUG


@pytest.mark.parametrize("language", sorted(LANGUAGE_MATRIX))
def test_language_pruning(tmp_path: Path, language: str) -> None:
    """Each ``primary_language`` keeps its toolchain and prunes the others."""
    project = _render(tmp_path, primary_language=language)
    matrix = LANGUAGE_MATRIX[language]
    missing = [p for p in matrix["present"] if not (project / p).exists()]
    leftover = [p for p in matrix["absent"] if (project / p).exists()]
    assert not missing, f"{language}: expected present but missing: {missing}"
    assert not leftover, f"{language}: expected absent but present: {leftover}"


@pytest.mark.parametrize("flag,paths", sorted(INCLUDE_FLAG_PATHS.items()))
def test_flag_no_prunes(
    tmp_path: Path, flag: str, paths: tuple[str, ...]
) -> None:
    """``include_<x>=no`` removes every file the hook lists for that flag."""
    project = _render(tmp_path, primary_language="polyglot", **{flag: "no"})
    leftover = [p for p in paths if (project / p).exists()]
    assert not leftover, f"{flag}=no left files behind: {leftover}"


@pytest.mark.parametrize("flag,paths", sorted(INCLUDE_FLAG_PATHS.items()))
def test_flag_yes_keeps(
    tmp_path: Path, flag: str, paths: tuple[str, ...]
) -> None:
    """``include_<x>=yes`` retains every file the hook would otherwise prune."""
    project = _render(tmp_path, primary_language="polyglot", **{flag: "yes"})
    missing = [p for p in paths if not (project / p).exists()]
    assert not missing, f"{flag}=yes dropped files: {missing}"


def test_default_render_smoke(tmp_path: Path) -> None:
    """Defaults render a project tree with the canonical entry points."""
    project = _render(tmp_path)
    assert project.is_dir()
    for path in ("Makefile", "AGENTS.md", "CLAUDE.md", "README.md"):
        assert (project / path).exists(), f"default render missing {path}"


def test_copier_only_artifact_removed(tmp_path: Path) -> None:
    """The cookiecutter hook strips ``.copier-answers.yml``."""
    project = _render(tmp_path)
    assert not (project / ".copier-answers.yml").exists()


@pytest.mark.parametrize("typechecker", ["ty", "mypy"])
def test_pyproject_typechecker_variant(tmp_path: Path, typechecker: str) -> None:
    """The chosen ``python_typechecker`` is the only one left in pyproject.toml."""
    project = _render(tmp_path, primary_language="python", python_typechecker=typechecker)
    contents = (project / "pyproject.toml").read_text()
    parsed = tomllib.loads(contents)

    tool = parsed.get("tool", {})
    if typechecker == "ty":
        assert "ty" in tool, "ty config section missing"
        assert "mypy" not in tool, "mypy config section should be pruned"
        assert any(d.startswith("ty>=") for d in parsed["dependency-groups"]["dev"])
        assert not any(d.startswith("mypy>=") for d in parsed["dependency-groups"]["dev"])
    else:
        assert "mypy" in tool, "mypy config section missing"
        assert "ty" not in tool, "ty config section should be pruned"
        assert any(d.startswith("mypy>=") for d in parsed["dependency-groups"]["dev"])
        assert not any(d.startswith("ty>=") for d in parsed["dependency-groups"]["dev"])

    assert "# variant:" not in contents, "variant sentinels should be stripped"
    assert "{%" not in contents and "{# " not in contents, "no Jinja control flow should remain"


@pytest.mark.parametrize("include_sbom", ["yes", "no"])
def test_pyproject_sbom_variant(tmp_path: Path, include_sbom: str) -> None:
    """``include_sbom`` controls the cyclonedx-bom dev dependency."""
    project = _render(tmp_path, primary_language="python", include_sbom=include_sbom)
    parsed = tomllib.loads((project / "pyproject.toml").read_text())
    has_cyclonedx = any(d.startswith("cyclonedx-bom") for d in parsed["dependency-groups"]["dev"])
    assert has_cyclonedx == (include_sbom == "yes")


def test_render_is_idempotent(tmp_path: Path) -> None:
    """Re-rendering on top of a prior render succeeds (``-f`` overwrite)."""
    first = _render(tmp_path)
    assert first.is_dir()
    # Second render with different flags must succeed against the same dir.
    second = _render(tmp_path, include_codacy="no", include_snyk="no")
    assert second.is_dir()
    assert not (second / ".codacy.yml").exists()
    assert not (second / ".snyk").exists()
    shutil.rmtree(second)
