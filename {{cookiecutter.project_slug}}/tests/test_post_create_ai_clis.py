"""Tests for the ensure_ai_clis() function in .devcontainer/post-create.sh.

Covers the five behaviour scenarios:
1. npm-based binaries already on PATH → install skipped.
2. npm not on PATH → npm install block skipped entirely.
3. npm install -g failure → logged and execution continues.
4. gh copilot built-in available → extension install skipped.
5. gh copilot built-in absent, extension not installed → extension installed.
6. gh not on PATH → gh-copilot block skipped entirely.
"""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / ".devcontainer" / "post-create.sh"
# Resolve once so restricting PATH in tests never hides the interpreter.
_BASH = shutil.which("bash") or "/bin/bash"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _stub(directory: str, name: str, *, exits: int = 0, output: str = "") -> Path:
    """Write a minimal bash stub that prints *output* and exits *exits*."""
    p = Path(directory) / name
    p.write_text(
        "#!/usr/bin/env bash\n"
        f'printf "%s\\n" "{output}"\n'
        f"exit {exits}\n"
    )
    p.chmod(p.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return p


def _stub_npm_writable(directory: str) -> Path:
    """npm stub that reports *directory* as its global prefix (always writable)."""
    p = Path(directory) / "npm"
    p.write_text(
        "#!/usr/bin/env bash\n"
        # `npm config get prefix` → return the stub dir so it is always writable.
        f'printf "%s\\n" "{directory}"\n'
        "exit 0\n"
    )
    p.chmod(p.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return p


def _run_ensure_ai_clis(path: str, extra_env: dict | None = None) -> subprocess.CompletedProcess:
    """Source post-create.sh (with main stubbed out) and call ensure_ai_clis()."""
    driver = (
        # Relax strict mode in the test driver to prevent stub failures from
        # terminating the wrapper before we can check the log output.
        "set +eu\n"
        # Override main so sourcing the script is side-effect free.
        "main() { :; }\n"
        f"source {SCRIPT}\n"
        "ensure_ai_clis\n"
    )
    env = {**os.environ, "PATH": path, **(extra_env or {})}
    return subprocess.run([_BASH, "-c", driver], capture_output=True, text=True, env=env)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_skips_npm_installs_when_binaries_already_on_path():
    """All three AI CLI binaries on PATH → no npm install -g calls."""
    with tempfile.TemporaryDirectory() as d:
        _stub_npm_writable(d)
        for binary in ("claude", "codex", "gemini", "gh"):
            _stub(d, binary)
        result = _run_ensure_ai_clis(f"{d}:{os.environ.get('PATH', '')}")

    assert result.returncode == 0, result.stderr
    assert "already installed" in result.stdout
    # npm install should never be invoked when the binary is present.
    assert "npm install" not in result.stdout


def test_skips_npm_install_when_npm_absent():
    """npm not on PATH → entire npm install block is skipped."""
    with tempfile.TemporaryDirectory() as d:
        _stub(d, "gh")
        # PATH contains only the stub dir — no npm there.
        result = _run_ensure_ai_clis(d)

    assert result.returncode == 0, result.stderr
    assert "npm not on PATH" in result.stdout


def test_npm_install_failure_is_non_fatal():
    """npm install -g failure → logs the error and continues; exits 0."""
    with tempfile.TemporaryDirectory() as d:
        # npm exits 1 for every invocation (simulates install failure).
        _stub(d, "npm", exits=1)
        _stub(d, "gh")
        result = _run_ensure_ai_clis(f"{d}:{os.environ.get('PATH', '')}")

    assert result.returncode == 0, result.stderr
    assert "continuing" in result.stdout


def test_skips_copilot_extension_when_gh_builtin_available():
    """gh copilot --help exits 0 (built-in present) → extension install skipped."""
    with tempfile.TemporaryDirectory() as d:
        _stub_npm_writable(d)
        for binary in ("claude", "codex", "gemini"):
            _stub(d, binary)
        # gh exits 0 for every invocation → `gh copilot --help` succeeds.
        _stub(d, "gh", exits=0)
        result = _run_ensure_ai_clis(f"{d}:{os.environ.get('PATH', '')}")

    assert result.returncode == 0, result.stderr
    assert "built-in" in result.stdout
    assert "installing gh extension" not in result.stdout


def test_installs_gh_copilot_extension_when_builtin_absent():
    """gh copilot --help fails, extension not listed → extension install attempted."""
    with tempfile.TemporaryDirectory() as d:
        _stub_npm_writable(d)
        for binary in ("claude", "codex", "gemini"):
            _stub(d, binary)
        # gh script: copilot --help → fail; extension list → empty; install → success.
        gh_script = Path(d) / "gh"
        gh_script.write_text(
            "#!/usr/bin/env bash\n"
            'case "$*" in\n'
            '  "copilot --help") exit 1 ;;\n'
            '  "extension list")  printf "" ; exit 0 ;;\n'
            '  "extension install github/gh-copilot") exit 0 ;;\n'
            "esac\n"
            "exit 0\n"
        )
        gh_script.chmod(gh_script.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

        result = _run_ensure_ai_clis(f"{d}:{os.environ.get('PATH', '')}")

    assert result.returncode == 0, result.stderr
    assert "installing gh extension" in result.stdout


def test_skips_gh_copilot_when_gh_absent():
    """gh not on PATH → gh-copilot block skipped entirely."""
    with tempfile.TemporaryDirectory() as d:
        _stub_npm_writable(d)
        for binary in ("claude", "codex", "gemini"):
            _stub(d, binary)
        # No gh stub → gh is absent from PATH.
        result = _run_ensure_ai_clis(d)

    assert result.returncode == 0, result.stderr
    assert "gh CLI not found" in result.stdout
