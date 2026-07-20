"""Focused regression tests for shell validation scripts."""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess  # nosec B404 - tests exercise repo-local scripts
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = PROJECT_ROOT / "scripts"
BASH = shutil.which("bash") or "/bin/bash"


def _copy_scripts(root: Path, *names: str) -> None:
    for name in names:
        destination = root / "scripts" / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SCRIPTS / name, destination)
    common = root / "scripts" / "lib" / "common.sh"
    common.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SCRIPTS / "lib" / "common.sh", common)


def _write_executable(path: Path, content: str) -> None:
    path.write_text(content)
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


class ValidationScriptTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("jq"), "jq is required by check-traceability")
    def test_traceability_globs_with_spaces_are_single_patterns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_scripts(root, "check-traceability.sh")
            (root / "source files").mkdir()
            (root / "test files").mkdir()
            (root / "source files" / "item.txt").write_text("source\n")
            (root / "test files" / "item.txt").write_text("test\n")
            specs = root / "specs"
            specs.mkdir()
            matrix = {
                "criteria": [
                    {
                        "id": "TRACE-1",
                        "source": ["source files/*.txt"],
                        "tests": ["test files/*.txt"],
                        "evidence": [],
                    }
                ]
            }
            (specs / "traceability.json").write_text(json.dumps(matrix))
            passed = subprocess.run(  # nosec B603 # nosemgrep - fixed argv, repo-local scripts
                [BASH, "scripts/check-traceability.sh"],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )
            matrix["criteria"][0]["tests"] = ["missing files/*.txt"]
            (specs / "traceability.json").write_text(json.dumps(matrix))
            failed = subprocess.run(  # nosec B603 # nosemgrep - fixed argv, repo-local scripts
                [BASH, "scripts/check-traceability.sh"],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(passed.returncode, 0, passed.stderr)
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("tests glob matches no files", failed.stderr)

    @unittest.skipUnless(shutil.which("jq"), "jq is required by check-traceability")
    def test_traceability_demux_preserves_tab_and_rejects_newline(self) -> None:
        # Robustness regression for check-traceability.sh's single-jq-pass
        # field demux (the jq->awk multiplexing site that governance.py
        # --emit's newline guard does NOT cover, because this site consumes
        # jq output from traceability.json rather than the --emit protocol).
        # Each source/tests/evidence value is framed as a tab-delimited
        # `field<TAB>value` line, so:
        #   * an embedded TAB inside a value must be PRESERVED end-to-end
        #     (the demux strips only the leading `field<TAB>` prefix), never
        #     truncated at the first embedded tab; and
        #   * an embedded NEWLINE cannot be represented on one line, so it
        #     must cause a LOUD non-zero exit with a stderr diagnostic —
        #     never a silently dropped continuation line.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_scripts(root, "check-traceability.sh")
            specs = root / "specs"
            specs.mkdir()

            # (a) TAB preserved: an evidence path whose name contains a literal
            # tab resolves via `[[ -e ]]` ONLY if the full tabbed value
            # survives the demux. Truncation at the first tab would leave the
            # path "evid", which does not exist -> a drift finding -> exit 1.
            tab_name = "evid\tence.txt"
            (root / tab_name).write_text("x\n")
            self.assertFalse((root / "evid").exists())  # truncation target absent
            tab_matrix = {
                "criteria": [
                    {"id": "C1", "source": [], "tests": [], "evidence": [tab_name]}
                ]
            }
            (specs / "traceability.json").write_text(json.dumps(tab_matrix))
            tab_result = subprocess.run(  # nosec B603 # nosemgrep - fixed argv, repo-local scripts
                [BASH, "scripts/check-traceability.sh"],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )

            # (b) NEWLINE -> loud non-zero exit + stderr diagnostic, no drop.
            newline_matrix = {
                "criteria": [
                    {
                        "id": "C1",
                        "source": ["line1\nline2"],
                        "tests": [],
                        "evidence": [],
                    }
                ]
            }
            (specs / "traceability.json").write_text(json.dumps(newline_matrix))
            newline_result = subprocess.run(  # nosec B603 # nosemgrep - fixed argv, repo-local scripts
                [BASH, "scripts/check-traceability.sh"],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )

            # (c) realistic (tab/newline-free) input still resolves cleanly.
            (root / "real.txt").write_text("y\n")
            ok_matrix = {
                "criteria": [
                    {"id": "C1", "source": [], "tests": [], "evidence": ["real.txt"]}
                ]
            }
            (specs / "traceability.json").write_text(json.dumps(ok_matrix))
            ok_result = subprocess.run(  # nosec B603 # nosemgrep - fixed argv, repo-local scripts
                [BASH, "scripts/check-traceability.sh"],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )

        # (a) tab preserved end-to-end: the tab-named evidence file resolved.
        self.assertEqual(tab_result.returncode, 0, tab_result.stderr)
        self.assertNotIn("evidence file missing", tab_result.stderr)
        # (b) newline -> loud failure with a diagnostic, never a silent drop.
        self.assertNotEqual(newline_result.returncode, 0)
        self.assertIn("newline", newline_result.stderr)
        # (c) realistic input unaffected by the demux hardening.
        self.assertEqual(ok_result.returncode, 0, ok_result.stderr)

    def test_hidden_and_ignored_marker_search_scope_matches_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_scripts(root, "marker-scan.sh")
            lib = root / "scripts" / "lib"
            shutil.copy2(SCRIPTS / "lib" / "governance.py", lib / "governance.py")
            shutil.copy2(PROJECT_ROOT / "governance-rules.yaml", root / "governance-rules.yaml")
            docs = root / "docs"
            docs.mkdir()
            (docs / ".hidden.md").write_text("TODO\n")
            (docs / "ignored.md").write_text("TODO\n")
            (root / ".gitignore").write_text("docs/ignored.md\n")
            subprocess.run(  # nosec B603, B607 # nosemgrep - fixed argv
                ["git", "init", "-q"], cwd=root, check=True
            )
            normal = subprocess.run(  # nosec B603 # nosemgrep - fixed argv, repo-local scripts
                [BASH, "scripts/marker-scan.sh"],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )
            fallback_bin = root / "bin"
            fallback_bin.mkdir()
            for command in ("awk", "basename", "dirname", "grep", "sort"):
                executable = shutil.which(command)
                if executable:
                    os.symlink(executable, fallback_bin / command)
            # Use the interpreter running the tests so its site-packages
            # (e.g. PyYAML for governance.py) stay available under the
            # stripped PATH. A shim script (not a symlink) preserves
            # virtualenv resolution, which depends on the executable path.
            _write_executable(
                fallback_bin / "python3",
                f'#!/bin/sh\nexec "{sys.executable}" "$@"\n',
            )
            fallback = subprocess.run(  # nosec B603 # nosemgrep - fixed argv, repo-local scripts
                [BASH, "scripts/marker-scan.sh"],
                cwd=root,
                env={**os.environ, "PATH": str(fallback_bin)},
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(normal.returncode, fallback.returncode)
        self.assertIn(".hidden.md", normal.stdout + normal.stderr)
        self.assertIn("ignored.md", normal.stdout + normal.stderr)
        self.assertIn(".hidden.md", fallback.stdout + fallback.stderr)
        self.assertIn("ignored.md", fallback.stdout + fallback.stderr)

    def test_marker_scan_fails_loudly_when_surfaces_loader_crashes(self) -> None:
        # Regression test for the CRIT-001 vacuous-scan bug (issue #119): a
        # governance loader that crashes only on --list-marker-surfaces
        # (while the preceding --marker-regex call still succeeds) must not
        # silently leave `surfaces` empty and let the scan proceed against
        # zero surfaces. It must exit non-zero and name the failing loader
        # invocation, mirroring
        # test_skill_contracts.py::test_governance_check_fails_loudly_on_corrupt_rules_file.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_scripts(root, "marker-scan.sh")
            lib = root / "scripts" / "lib"
            shutil.copy2(SCRIPTS / "lib" / "governance.py", lib / "governance.py")
            # Valid prohibited_markers.pattern_pairs (so --marker-regex
            # succeeds) but surfaces explicitly null: the key IS present,
            # so GovernanceRules.get_marker_surfaces()'s
            # `.get("surfaces", [])` default does not apply, and
            # `list(None)` raises, giving --list-marker-surfaces a
            # non-zero exit.
            (root / "governance-rules.yaml").write_text(
                "prohibited_markers:\n"
                "  pattern_pairs:\n"
                "    - [TO, DO]\n"
                "  surfaces: null\n"
            )
            subprocess.run(  # nosec B603, B607 # nosemgrep - fixed argv
                ["git", "init", "-q"], cwd=root, check=True
            )
            result = subprocess.run(  # nosec B603 # nosemgrep - fixed argv, repo-local scripts
                [BASH, "scripts/marker-scan.sh"],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("governance loader failed", result.stderr)

    def test_doc_drift_deduplicates_without_associative_arrays(self) -> None:
        self.assertNotIn("declare -A", (SCRIPTS / "check-doc-drift.sh").read_text())
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_scripts(root, "check-doc-drift.sh")
            docs = root / "docs"
            docs.mkdir()
            (docs / "guide.md").write_text("`missing.md` and `missing.md`\n")
            result = subprocess.run(  # nosec B603 # nosemgrep - fixed argv, repo-local scripts
                [BASH, "scripts/check-doc-drift.sh", "block"],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            (result.stdout + result.stderr).count("referenced path does not exist"),
            1,
        )

    @unittest.skipUnless(
        (SCRIPTS / "generate-sbom.sh").exists(),
        "generate-sbom.sh not present (include_sbom=no render)",
    )
    def test_python_sbom_replaces_only_successful_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _copy_scripts(root, "generate-sbom.sh")
            (root / "pyproject.toml").write_text("[project]\nname = 'demo'\n")
            sbom = root / "sbom"
            sbom.mkdir()
            destination = sbom / "sbom-python.cdx.json"
            destination.write_text("original\n")
            bin_dir = root / "bin"
            bin_dir.mkdir()
            command = bin_dir / "cyclonedx-py"
            _write_executable(command, "#!/bin/sh\nprintf 'replacement\\n'\n")
            success = subprocess.run(  # nosec B603 # nosemgrep - fixed argv, repo-local scripts
                [BASH, "scripts/generate-sbom.sh"],
                cwd=root,
                env={**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"},
                capture_output=True,
                text=True,
                check=False,
            )
            _write_executable(command, "#!/bin/sh\nprintf 'partial\\n'\nexit 1\n")
            failed = subprocess.run(  # nosec B603 # nosemgrep - fixed argv, repo-local scripts
                [BASH, "scripts/generate-sbom.sh"],
                cwd=root,
                env={**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"},
                capture_output=True,
                text=True,
                check=False,
            )

            content = destination.read_text()
            temporary_outputs = list(sbom.glob("*.tmp.*"))

        self.assertEqual(success.returncode, 0, success.stderr)
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual(content, "replacement\n")
        self.assertEqual(temporary_outputs, [])


if __name__ == "__main__":
    unittest.main()
