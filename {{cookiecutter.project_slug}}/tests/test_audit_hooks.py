"""Regression suite for the Layer-4 advisory hooks that build the
session audit trail.

Three hooks are exercised:

- `.claude/hooks/session-start.js`  → emits `type: "session-start"`
- `.claude/hooks/user-prompt-submit.js` → emits `type: "prompt"`
- `.claude/hooks/post-tool-use.js` → emits `type: "tool-result"`

Each hook reads a JSON payload from stdin per the Claude Code
hook protocol, appends a JSON line to `report/audit.jsonl`, and
exits 0. The tests verify exit code, file creation, and event
shape. Per `IMP-001` the audit log is append-only — these tests
also confirm that subsequent invocations append rather than
truncate.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOKS_DIR = REPO_ROOT / ".claude" / "hooks"


def _run_hook(hook_filename: str, payload: dict, cwd: Path) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["node", str(HOOKS_DIR / hook_filename)],
        input=json.dumps(payload).encode(),
        capture_output=True,
        cwd=cwd,
    )


def _read_audit_lines(cwd: Path) -> list[dict]:
    audit = cwd / "report" / "audit.jsonl"
    if not audit.exists():
        return []
    return [json.loads(line) for line in audit.read_text().splitlines() if line.strip()]


class SessionStartHookTests(unittest.TestCase):
    def test_emits_session_start_event(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            result = _run_hook(
                "session-start.js",
                {"session_id": "test-session-1"},
                cwd,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            events = _read_audit_lines(cwd)
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]["type"], "session-start")
            self.assertEqual(events[0]["session_id"], "test-session-1")
            self.assertIn("ts", events[0])
            self.assertIn("cwd", events[0])

    def test_handles_missing_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            # No stdin payload — hook must still exit 0 and write a
            # session-start record.
            result = subprocess.run(
                ["node", str(HOOKS_DIR / "session-start.js")],
                input=b"",
                capture_output=True,
                cwd=cwd,
            )
            self.assertEqual(result.returncode, 0)
            events = _read_audit_lines(cwd)
            self.assertEqual(len(events), 1)
            self.assertIsNone(events[0]["session_id"])


class UserPromptSubmitHookTests(unittest.TestCase):
    def test_records_prompt_hash_not_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            secret_prompt = "this should not appear in the audit log"
            result = _run_hook(
                "user-prompt-submit.js",
                {"session_id": "abc", "prompt": secret_prompt},
                cwd,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            events = _read_audit_lines(cwd)
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]["type"], "prompt")
            # Prompt text MUST NOT appear in the audit line.
            audit_raw = (cwd / "report" / "audit.jsonl").read_text()
            self.assertNotIn(secret_prompt, audit_raw)
            # A SHA-256 hash MUST be present.
            self.assertTrue(events[0]["prompt_hash"].startswith("sha256:"))
            self.assertEqual(events[0]["prompt_length"], len(secret_prompt))


class PostToolUseHookTests(unittest.TestCase):
    def test_records_tool_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            result = _run_hook(
                "post-tool-use.js",
                {
                    "session_id": "s1",
                    "tool_name": "Bash",
                    "tool_response": {"success": True},
                },
                cwd,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            events = _read_audit_lines(cwd)
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]["type"], "tool-result")
            self.assertEqual(events[0]["tool_name"], "Bash")
            self.assertTrue(events[0]["success"])

    def test_records_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            result = _run_hook(
                "post-tool-use.js",
                {
                    "tool_name": "Bash",
                    "tool_response": {"success": False, "error": "boom"},
                },
                cwd,
            )
            self.assertEqual(result.returncode, 0)
            events = _read_audit_lines(cwd)
            self.assertEqual(events[0]["success"], False)


class AuditTrailAppendOnlyTests(unittest.TestCase):
    def test_multiple_invocations_append(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            _run_hook("session-start.js", {"session_id": "1"}, cwd)
            _run_hook(
                "user-prompt-submit.js",
                {"session_id": "1", "prompt": "first"},
                cwd,
            )
            _run_hook(
                "post-tool-use.js",
                {"session_id": "1", "tool_name": "Bash"},
                cwd,
            )
            events = _read_audit_lines(cwd)
            self.assertEqual(len(events), 3)
            self.assertEqual(
                [e["type"] for e in events],
                ["session-start", "prompt", "tool-result"],
            )

    def test_write_failure_does_not_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            # Create `report` as a regular file to break the
            # mkdir/append sequence; the hook should still exit 0
            # (advisory) but the audit line is lost — that is the
            # documented behavior for write failures.
            (cwd / "report").write_text("not a directory")
            result = _run_hook("session-start.js", {}, cwd)
            self.assertEqual(result.returncode, 0)
            self.assertIn(b"audit-trail write failed", result.stderr)


if __name__ == "__main__":
    unittest.main()
