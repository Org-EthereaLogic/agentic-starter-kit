"""Regression tests for IMP-006 action pin validation."""

from __future__ import annotations

import shutil
import subprocess  # nosec B404  # nosemgrep
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = PROJECT_ROOT / "scripts" / "check-action-pins.sh"
COMMON = PROJECT_ROOT / "scripts" / "lib" / "common.sh"
BASH = shutil.which("bash") or "/bin/bash"


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def _copy_checker(root: Path) -> None:
    script_path = root / "scripts" / "check-action-pins.sh"
    common_path = root / "scripts" / "lib" / "common.sh"
    script_path.parent.mkdir(parents=True, exist_ok=True)
    common_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SCRIPT, script_path)
    shutil.copy2(COMMON, common_path)


def _run_checker(workflow: str, *args: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _copy_checker(root)
        _write_text(root / ".github" / "workflows" / "ci.yml", workflow)
        return subprocess.run(  # nosec B603  # nosemgrep
            [BASH, "scripts/check-action-pins.sh", *args],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )


class ActionPinCheckTests(unittest.TestCase):
    def test_strict_mode_detects_inline_list_uses(self) -> None:
        result = _run_checker(
            "jobs:\n"
            "  test:\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n",
            "--strict",
        )

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("actions/checkout@v4", result.stdout)

    def test_soft_mode_warns_without_failing(self) -> None:
        result = _run_checker(
            "jobs:\n"
            "  test:\n"
            "    steps:\n"
            "      - uses: actions/setup-node@latest\n",
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("actions/setup-node@latest", result.stdout)

    def test_quoted_uppercase_sha_is_accepted(self) -> None:
        result = _run_checker(
            "jobs:\n"
            "  test:\n"
            "    steps:\n"
            "      - uses: \"actions/checkout@ABCDEFABCDEFABCDEFABCDEFABCDEFABCDEFABCD\"\n",
            "--strict",
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_local_and_docker_refs_are_skipped(self) -> None:
        result = _run_checker(
            "jobs:\n"
            "  test:\n"
            "    steps:\n"
            "      - uses: ./local-action\n"
            "      - uses: docker://alpine:3.20\n",
            "--strict",
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_slsa_generator_tag_pin_is_allowed(self) -> None:
        # The SLSA generator reusable workflow MUST be tag-pinned per
        # upstream policy (the trusted-workflow signature is anchored
        # to the tag, not the commit). The gate's allow-list excepts
        # `slsa-framework/slsa-github-generator` for that reason.
        result = _run_checker(
            "jobs:\n"
            "  provenance:\n"
            "    uses: slsa-framework/slsa-github-generator/.github/workflows/generator_generic_slsa3.yml@v2.0.0\n",
            "--strict",
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_other_repos_do_not_inherit_slsa_exception(self) -> None:
        result = _run_checker(
            "jobs:\n"
            "  test:\n"
            "    steps:\n"
            "      - uses: example/slsa-helper@v1\n",
            "--strict",
        )

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
