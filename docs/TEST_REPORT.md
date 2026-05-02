# Cookiecutter Template Test Report

**Date:** 2026-05-02
**Template:** agentic-starter-kit
**Test Environment:** macOS 25.4.0, Python 3.12.13, Node.js v22.22.2

---

## Executive Summary

The cookiecutter template renders successfully and passes core validation checks for Python projects. However, **critical issues were identified in the TypeScript variant that prevent successful test execution**, and the template's default values create build failures that require user intervention.

**Status:** 🟡 PARTIALLY FUNCTIONAL
- Python variant: ✅ PASS (with caveats)
- TypeScript variant: ❌ FAIL (blocker issue)
- Default template values: ⚠️ PROBLEMATIC

---

## Test Methodology

1. **Template Rendering** — Rendered with both default values and valid user inputs
2. **Git Initialization** — Set up git repo and committed initial state
3. **Dependency Installation** — Ran `make sync` to install dev dependencies
4. **Validation Checks** — Executed all make targets (marker-scan, governance-check, hooks-test, etc.)
5. **Code Quality** — Ran lint, typecheck, and test suites
6. **Multi-language Testing** — Tested both Python and TypeScript variants

---

## Findings

### 1. ❌ CRITICAL: Default Template Values Cause Build Failure

**Issue:** The `cookiecutter.json` provides placeholder values like `<your name>` and `<your email>` that are not valid when used in `pyproject.toml` author metadata.

**Root Cause:** When running with `--no-input`, these placeholders flow into the generated `pyproject.toml`, which then fails hatchling build validation:

```
email.errors.HeaderParseError: Expected 'atom' or 'quoted-string' but found '<your email>'
```

**Impact:** Users running `cookiecutter . --no-input` (or CI/CD systems) will experience immediate failure at `make sync`.

**Recommendation:** Replace placeholder defaults with sensible fallbacks:
```json
{
  "author_name": "Project Author",
  "author_email": "author@example.com",
  "project_description": "An agentic application",
  ...
}
```

**Workaround:** Users must provide explicit values: `cookiecutter . --no-input project_name="My App" author_email="user@domain.com"`

---

### 2. ❌ CRITICAL: TypeScript Test Harness Incompatible with ESM Module Type

**Issue:** The `test_pre_tool_use_hook.js` file uses CommonJS syntax (`require()`) but `package.json` declares `"type": "module"`, causing Node.js to treat it as ES module.

**Error Output:**
```
ReferenceError: require is not defined in ES module scope, you can use import instead
```

**Impact:** The `make hooks-test` target fails entirely for TypeScript projects, breaking CRIT-008 validation (protected-branch hook must be tested).

**Files Affected:**
- `tests/test_pre_tool_use_hook.js` — needs ES module syntax
- Alternatively: rename to `.cjs` and adjust package.json script

**Recommendation:** Convert test file to ES modules:
```javascript
import test from "node:test";
import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
// ... etc
```

---

### 3. ⚠️ ISSUE: Post-Gen Hook Python File Deletion Not Tested

**Issue:** The post-gen hook is supposed to remove `tests/test_pre_tool_use_hook.js` for Python projects, but this wasn't verified through a full lifecycle test.

**Context:** The hook.py file includes logic to delete TypeScript files when `primary_language == "python"`, but wasn't actually triggered during rendering.

**Recommendation:** Add explicit test to verify:
- Python variant has `.py` test file, no `.js` test file
- TypeScript variant has `.js` test file, no `.py` test file
- Both variants have appropriate package.json/pyproject.toml

---

### 4. ✅ PASS: Python Project Rendering and Validation

The Python variant renders correctly and all validation gates pass:

```
✓ marker-scan (4 surfaces scanned)
✓ governance-check (4 warnings about future-phase artifacts — expected)
✓ check-traceability (gracefully skips when specs/ absent)
✓ check-doc-drift (gracefully skips when docs/ absent)
✓ hooks-test (18/18 tests PASS)
✓ lint (via ruff — all checks passed)
✓ test (pytest — 18/18 tests PASS)
✓ validate (aggregate gate — PASS)
```

**Dependency Installation:**
- ✅ `make sync` succeeds with valid author_email
- ✅ Creates `.venv` and installs 58 packages
- ✅ Includes dev dependencies: ruff, mypy, pytest, pytest-cov, pre-commit

**Test Suite:**
- 18 pre-tool-use hook regression tests
- All 18 tests pass (security, branch protection, commit validation)
- No false positives or negatives observed

---

### 5. ⚠️ ISSUE: Conditional File Removal Needs Integration Test

**Issue:** The post-gen hook removes files based on `primary_language` choice:
- Python: removes `package.json`, `tsconfig.json`, and JS test file
- TypeScript: removes `pyproject.toml` and Python test file

**Status:** Hook logic is present, but wasn't tested end-to-end with actual file verification.

**Recommendation:** Add smoke test to template CI that verifies final artifact structure.

---

### 6. ✅ PASS: Documentation Rendering

All CLAUDE.md, AGENTS.md, CONSTITUTION.md, etc. render with correct variable substitution:
- Project name correctly substituted in titles and headings
- No unrendered `{{ cookiecutter.* }}` variables found
- Jinja conditionals properly evaluated (SBOM inclusion, etc.)

---

### 7. ⚠️ OBSERVATION: Tool Dependencies Not Bundled

**Expectation:** Tools like `ruff`, `mypy`, `pytest` are listed in `pyproject.toml[project.optional-dependencies]` but not installed by default until `make sync`.

**Current Behavior:** Make targets gracefully warn if tools not installed:
```
WARN: ruff not installed (added in Phase 5)
WARN: mypy not installed (added in Phase 5)
```

**Assessment:** This is acceptable for a cookiecutter template (user installs via `make sync`), but could be documented more prominently in README.md.

---

## Test Execution Summary

| Test | Python | TypeScript | Status |
|------|--------|------------|--------|
| Template render | ✅ | ✅ | PASS |
| Default values build | ❌ | ❌ | FAIL — needs valid email |
| Valid values build | ✅ | ✅ | PASS |
| Git init | ✅ | ✅ | PASS |
| make sync | ✅ | ✅ | PASS |
| make marker-scan | ✅ | ✅ | PASS |
| make governance-check | ✅ | ✅ | PASS |
| make hooks-test | ✅ | ❌ | FAIL — ESM module error |
| make lint | ✅ | ⚠️ | WARN — eslint not run |
| make test | ✅ | ❌ | FAIL — hooks-test blocks |
| make validate | ✅ | ❌ | FAIL |

---

## Recommended Fixes (Priority Order)

### P0 — Critical (blocks template usability)

1. **Fix default cookiecutter.json values** (5 min)
   - Replace `<your name>`, `<your email>`, etc. with valid defaults
   - File: `cookiecutter.json`

2. **Fix TypeScript test harness ESM compatibility** (15 min)
   - Convert `tests/test_pre_tool_use_hook.js` to use `import` statements
   - File: `{{cookiecutter.project_slug}}/tests/test_pre_tool_use_hook.js`

### P1 — Important (should be fixed before release)

3. **Add integration test for post-gen hook** (20 min)
   - Verify correct files exist for each language variant
   - Add to CI workflow or Makefile validation
   - Files: `.github/workflows/ci.yml` or scripts/

### P2 — Nice-to-have (documentation/UX)

4. **Enhance README with setup instructions** (10 min)
   - Document: "Run `make sync` first" (required before `make validate`)
   - Clarify: Which `make` targets require tool installation
   - File: `{{cookiecutter.project_slug}}/README.md`

5. **Add language-specific getting-started guides** (20 min)
   - Python: How to run tests, type-check, lint
   - TypeScript: How to run tests, type-check, eslint
   - File: Separate docs or README sections

---

## Refactoring Opportunities

### Short-term (1-2 weeks)

1. **Consolidate duplicate test suites**
   - The Python and TypeScript test files are 90% identical
   - Consider a template-based approach or code generator
   - Reduces maintenance burden for CRIT-008 updates

2. **Normalize make target output**
   - Some targets (lint, typecheck) skip gracefully if tool missing
   - Others (hooks-test) fail if Python/Node tools not ready
   - Standardize: Either all warn or all fail consistently

3. **Extract common shell scripts to `scripts/lib/`**
   - `marker-scan.sh`, `check-governance.sh` share patterns
   - Create shared utilities for path checking, regex matching
   - Reduces duplication in Phase 5 scripts

### Medium-term (1 month)

4. **Add language-specific Makefile fragments**
   - Split Makefile into `Makefile.base`, `Makefile.python`, `Makefile.typescript`
   - Post-gen hook assembles final Makefile
   - Cleaner, easier to maintain per-language targets

5. **Implement per-language CI workflows**
   - `.github/workflows/ci-python.yml` vs `ci-typescript.yml`
   - Reduces conditional logic in workflow YAML
   - Makes language-specific requirements explicit

6. **Add template smoke test suite**
   - Automated rendering + validation in CI
   - Test both Python and TypeScript variants
   - Test all license/tool inclusion combinations
   - Catches regressions early

---

## Environment and Methodology Notes

- **Python:** 3.12.13, uv 0.5.0 package manager
- **Node.js:** v22.22.2
- **Build tools:** hatchling 1.18+, ruff 0.15.12, pytest 9.0.2
- **Test locations:** `/tmp/cookiecutter-test/` (isolated from system)
- **git user configured:** test@example.com

---

## Conclusion

The template is **functionally sound for Python projects** with proper user input. The **TypeScript variant has a blocking issue** that prevents validation. Default values must be fixed to allow hands-off rendering.

**Recommended action:** Fix the two critical issues (P0) before next release; these are high-impact, low-effort fixes that unblock the template for automated provisioning and CI/CD pipelines.

