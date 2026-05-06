#!/usr/bin/env python3
"""Post-generation hook for the agentic-starter-kit cookiecutter.

Runs after `cookiecutter` renders the templated project.
Conditionally removes language-specific or integration-specific
files that the user did not select in `cookiecutter.json`.

Idempotent: every removal is guarded by an existence check, so the
script can run safely against a partial scaffold.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

PRIMARY_LANGUAGE = "{{ cookiecutter.primary_language }}"
PYTHON_TYPECHECKER = "{{ cookiecutter.python_typechecker }}"
INCLUDE_DATABRICKS = "{{ cookiecutter.include_databricks }}"
INCLUDE_CODACY = "{{ cookiecutter.include_codacy }}"
INCLUDE_CODECOV = "{{ cookiecutter.include_codecov }}"
INCLUDE_SNYK = "{{ cookiecutter.include_snyk }}"
INCLUDE_SBOM = "{{ cookiecutter.include_sbom }}"
INCLUDE_MACARON = "{{ cookiecutter.include_macaron }}"
INCLUDE_DEVCONTAINER = "{{ cookiecutter.include_devcontainer }}"
INCLUDE_DOCS_SITE = "{{ cookiecutter.include_docs_site }}"
INCLUDE_RELEASE_AUTOMATION = "{{ cookiecutter.include_release_automation }}"
INCLUDE_PROMPTFOO = "{{ cookiecutter.include_promptfoo }}"
LICENSE_CHOICE = "{{ cookiecutter.license }}"

PROJECT_ROOT = Path.cwd()


def remove(relative_path: str) -> None:
    """Remove a file or directory if it exists."""
    target = PROJECT_ROOT / relative_path
    if not target.exists():
        return
    if target.is_dir():
        shutil.rmtree(target)
    else:
        target.unlink()
    print(f"  removed {relative_path}")


def remove_gitkeep_files() -> None:
    """Strip placeholder .gitkeep files left from the template scaffold."""
    for keep in PROJECT_ROOT.rglob(".gitkeep"):
        keep.unlink()


def remove_copier_only_files() -> None:
    """Drop copier-only artifacts that only matter for `copier update`.

    cookiecutter has no upgrade flow, so the answers-file template ships
    in the tree (for copier) but is irrelevant once cookiecutter renders.
    """
    remove(".copier-answers.yml")


def prune_language_files() -> None:
    """Remove files belonging to the unselected language path."""
    if PRIMARY_LANGUAGE == "python":
        remove("package.json")
        remove("tsconfig.json")
        remove("tests/test_pre_tool_use_hook.js")
        remove(".claude/agents/typescript-pro.md")
    elif PRIMARY_LANGUAGE == "typescript":
        remove("pyproject.toml")
        remove("tests/test_pre_tool_use_hook.py")
        remove("tests/test_governance_review.py")
        remove(".claude/agents/python-pro.md")


def prune_integration_files() -> None:
    """Remove integration configs the user opted out of."""
    if INCLUDE_CODACY == "no":
        remove(".codacy.yml")
    if INCLUDE_CODECOV == "no":
        remove("codecov.yaml")
    if INCLUDE_SNYK == "no":
        remove(".snyk")
    if INCLUDE_SBOM == "no":
        remove("scripts/generate-sbom.sh")
        remove("docs/sbom-policy.md")
    if INCLUDE_DEVCONTAINER == "no":
        remove(".devcontainer")
        remove("Dockerfile")
        remove(".dockerignore")
    if INCLUDE_DOCS_SITE == "no":
        remove("mkdocs.yml")
        remove("docs/index.md")
        remove(".github/workflows/docs.yml")
    if INCLUDE_RELEASE_AUTOMATION == "no":
        remove(".cz.toml")
        remove("release-please-config.json")
        remove("release-please-manifest.json")
        remove(".github/workflows/release-please.yml")
    if INCLUDE_PROMPTFOO == "no":
        remove("prompts")
        remove("evals")
        remove("docs/prompt-versioning-policy.md")
        remove("Makefile.fragments/evals.mk")


def prune_databricks_files() -> None:
    """Remove Databricks-specific files when the option is off.

    The template ships no Databricks files in the initial release.
    Future Databricks bundle scaffolding lands here when added.
    """
    if INCLUDE_DATABRICKS == "no":
        return


def prune_license_files() -> None:
    """Currently a single LICENSE is templated to the chosen license.

    If the template ships per-license files in the future
    (e.g. LICENSE-MIT, LICENSE-Apache, LICENSE-Proprietary), the
    pruning logic for unused variants lives here.
    """
    return


def write_summary() -> None:
    print()
    print("Project scaffolded successfully.")
    print(f"  primary_language : {PRIMARY_LANGUAGE}")
    if PRIMARY_LANGUAGE in ("python", "polyglot"):
        print(f"  python_typecheck : {PYTHON_TYPECHECKER}")
    print(f"  license          : {LICENSE_CHOICE}")
    print(f"  databricks       : {INCLUDE_DATABRICKS}")
    print(f"  codacy           : {INCLUDE_CODACY}")
    print(f"  codecov          : {INCLUDE_CODECOV}")
    print(f"  snyk             : {INCLUDE_SNYK}")
    print(f"  sbom             : {INCLUDE_SBOM}")
    print(f"  macaron          : {INCLUDE_MACARON}")
    print(f"  devcontainer     : {INCLUDE_DEVCONTAINER}")
    print(f"  docs site        : {INCLUDE_DOCS_SITE}")
    print(f"  release autom.   : {INCLUDE_RELEASE_AUTOMATION}")
    print(f"  promptfoo evals  : {INCLUDE_PROMPTFOO}")
    print()
    print("Next steps:")
    print("  cd <project>")
    print("  git init && git checkout -b feat/initial")
    print("  make sync")
    print("  make validate")
    print("  make hooks-test")
    print()


def main() -> int:
    print("Pruning unselected files…")
    prune_language_files()
    prune_integration_files()
    prune_databricks_files()
    prune_license_files()
    remove_copier_only_files()
    remove_gitkeep_files()
    write_summary()
    return 0


if __name__ == "__main__":
    sys.exit(main())
