# Cookiecutter Template: Optimization & Refactoring Roadmap

> **Status (2026-05-06):** items #1, #2, #3, #4, #6, and #7 shipped
> with v0.2 / v0.3 / v0.4. The remaining six items (#5, #8, #9,
> #10, #11, #12) were filed as GitHub issues #69–#74 against
> [Project #6](https://github.com/orgs/Org-EthereaLogic/projects/6)
> in the Backlog. See *Status* notes inline.

---

## Quick Wins (Immediate)

### 1. Fix cookiecutter.json Defaults

**Status:** ✅ Shipped (Phase A). Defaults are now `Author Name` /
`author@example.com` / `An agentic application`.

**Current State:**
```json
{
  "author_name": "<your name>",
  "author_email": "<your email>",
  "project_description": "<one-line project description>"
}
```

**Issue:** Breaks `make sync` and build validation.

**Proposed Change:**
```json
{
  "author_name": "Author Name",
  "author_email": "author@example.com",
  "project_description": "Your agentic application"
}
```

**Effort:** 5 minutes | **Impact:** High | **Blocker:** Yes

---

### 2. Convert TypeScript Test File to ES Modules

**Status:** ✅ Shipped. `tests/test_pre_tool_use_hook.js` now uses
ES module `import` syntax throughout.

**Current:** `tests/test_pre_tool_use_hook.js` uses `require()`
**Issue:** Incompatible with `"type": "module"` in package.json

**Convert all require() to import:**
```javascript
// Before
const test = require("node:test");
const assert = require("node:assert/strict");

// After
import test from "node:test";
import assert from "node:assert/strict";
```

**Effort:** 10 minutes | **Impact:** Critical | **Blocker:** Yes

---

### 3. Document make sync Requirement

**Status:** ✅ Shipped. `README.md` documents `make sync` as the
prerequisite for `make validate`.

Add to `README.md`:
```markdown
## Getting Started

1. Clone this repository
2. Run `make sync` to install dependencies (required before validation)
3. Run `make validate` to check the project
```

**Effort:** 5 minutes | **Impact:** Medium | **Blocker:** No

---

## Code Quality Improvements (1-2 weeks)

### 4. DRY Up Validation Scripts

**Status:** ✅ Shipped. `scripts/lib/common.sh` and
`scripts/lib/governance.py` are now sourced by `marker-scan.sh`,
`check-governance.sh`, and friends.

**Current:** `scripts/marker-scan.sh`, `scripts/check-governance.sh` share 40+ lines

**Refactor:**
```bash
# scripts/lib/common.sh — shared utilities
check_marker_in_file() { ... }
scan_surface_files() { ... }
report_scan_result() { ... }

# scripts/marker-scan.sh — simplified
source scripts/lib/common.sh
scan_surface_files "$CANONICAL_SURFACES"
report_scan_result
```

**Effort:** 2 hours | **Impact:** Medium | **Blocker:** No

**Before:** 4 scripts × 60 lines = 240 LOC
**After:** 1 library + 4 scripts × 20 lines = ~100 LOC

---

### 5. Consolidate Test Suite Maintenance

**Status:** ✅ Shipped — closed via [#69](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/69).

**Problem:** Python and TypeScript hook test files were ~90% identical
regression suites for `pre-tool-use.js`. Logic drifted independently
when only one was touched.

**Decision — data-driven Option A (JSON spec):**

- `tests/hook_test_spec.json` is the single source of truth for every
  bypass-class scenario and fixture-driven case.
- `tests/test_pre_tool_use_hook.py` and `tests/test_pre_tool_use_hook.js`
  iterate the spec at import time and dispatch one test per scenario.
- Cookiecutter renders `{{ cookiecutter.default_branch_name }}` inside
  the JSON at generation time, so no two-pass rendering is required.

**Why JSON over the originally-scoped `tests/fixtures/test_template.jinja2`:**

- JSON is parsed by both languages with the standard library — no
  PyYAML or `js-yaml` dependency, no custom Jinja2 environment in the
  post-gen hook, no nested-template escaping concerns.
- The drivers stay short and idiomatic for their language (`unittest`
  on Python, `node:test` on Node) rather than being machine-generated,
  which keeps stack traces and selectors easy to read.
- Adding a regression now means editing one JSON file — both languages
  pick the new case up automatically on the next `make hooks-test`.

**Why not Option B (shared `tests/lib/` utilities):**

- Would still leave two parallel scenario lists (one per driver),
  re-introducing the drift the issue was filed to eliminate.
- The shared-helper extraction is small enough that JSON-driven
  scenarios subsume it without the extra import surface.

**Effort:** 3 hours actual | **Impact:** High | **Blocker:** No

---

### 6. Create Makefile Fragment System

**Status:** ✅ Shipped. The rendered project's `Makefile` now
`include`s fragments under `Makefile.fragments/` (`defs.mk`,
`sync.mk`, `checks.mk`, `python.mk`, `typescript.mk`, `hooks.mk`,
`quality.mk`, `evals.mk`, `clean.mk`).

**Current:** Monolithic Makefile with conditionals
**Issue:** Hard to reason about; language-specific logic mixed

**Proposed:**
```
Makefile                    # base rules
Makefile.python            # python-specific (lint, typecheck, test)
Makefile.typescript        # typescript-specific (eslint, tsc, node --test)
Makefile.common            # shared (marker-scan, governance-check)
```

**Post-gen hook assembles:**
```bash
cat Makefile.common Makefile.${language} > Makefile
rm Makefile.python Makefile.typescript
```

**Effort:** 3 hours | **Impact:** Medium | **Blocker:** No

---

## Testing & Validation (2-3 weeks)

### 7. Add Automated Template Smoke Tests

**Status:** ✅ Shipped as `.github/workflows/template-smoke-test.yml`
(supplemented by `smoke-test.yml`). Renders the template across a
matrix of variants and runs `make validate` against each.

**Create:** `.github/workflows/smoke-test.yml`

```yaml
jobs:
  smoke-test-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Render template (Python)
        run: |
          cookiecutter . --no-input primary_language=python \
            author_email=test@example.com -o /tmp/test-python
      - name: Validate Python project
        run: |
          cd /tmp/test-python/my-agentic-project
          make validate
  
  smoke-test-typescript:
    # Similar for TypeScript
```

**Coverage:**
- ✅ Both language variants
- ✅ All license types
- ✅ All tool inclusion combos (codacy, codecov, snyk, sbom)
- ✅ Validation gate passes

**Effort:** 2 hours | **Impact:** High | **Blocker:** No

---

### 8. Add Integration Test for Post-Gen Hook

**Status:** ✅ Done — implemented as `tests/test_post_gen_pruning.py`
(pytest harness covering language × `include_*` flag matrix), wired
through `make template-test` and the `hook-pruning-test` job in
`.github/workflows/template-smoke-test.yml`. Tracked #70.

**Test:** Verify hook correctly removes language-inappropriate files.
The implementation is a pytest harness that renders the template into
a `tmp_path` per test and asserts presence/absence of files for each
`primary_language` and each `include_*` flag at both `yes` and `no`.
Run locally with `make template-test`; CI runs the same suite via the
`hook-pruning-test` job.

**Effort:** 1 hour | **Impact:** Medium | **Blocker:** No

---

## Architecture Improvements (3-4 weeks)

### 9. Implement Jinja2 Filter Library

**Status:** ❌ Won't do — closed [#71](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/71)
as **not planned**. Scope review found chained filters at only 4
sites in 2 config files (`cookiecutter.json`, `copier.yml`) and zero
in the rendered template tree. Net code would *grow*: cookiecutter
needs an `_extensions` registration plus a `jinja2.ext.Extension`
subclass, and copier has no equivalent native filter-extension API,
so dual-tool parity costs more than the 4 lines saved. Revisit if
chained filters ever appear in `{{cookiecutter.project_slug}}/**` or
if a third render tool is added. See #71 for the full rationale.

**Effort:** 2 hours | **Impact:** Low (nice-to-have) | **Blocker:** No

---

### 10. Extract Governance Rules to Data-Driven Config

**Status:** ✅ Done — closed [#72](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/72).
The required-file, required-agent, required-skill, optional-dir,
and prohibited-marker lists now live as top-level keys in
`{{cookiecutter.project_slug}}/governance-rules.yaml`. The existing
`scripts/lib/governance.py` loader gained accessors and CLI flags
(`--list-required-files`, `--list-required-agents`,
`--list-required-skills`, `--list-optional-dirs`,
`--list-marker-surfaces`, `--marker-regex`); `check-governance.sh`
and `marker-scan.sh` consume those instead of inlining bash arrays.
Marker strings are stored as split `[prefix, suffix]` pairs so the
YAML itself never carries the literal forbidden token. CRIT-001 and
CRIT-002 in `DIRECTIVES.md` now name `governance-rules.yaml` as the
single source of truth, and a new `tests/test_governance_loader.py`
exercises every accessor against a synthetic fixture.

**Effort:** 2 hours | **Impact:** Medium | **Blocker:** No

---

## Documentation & UX (1-2 weeks)

### 11. Create Language-Specific Quick Start Guides

**Status:** ✅ Done — closed [#73](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/73).
The substantive `QUICKSTART-PYTHON.md` (292 lines) and
`QUICKSTART-TYPESCRIPT.md` (243 lines) already shipped at the
rendered project root alongside the `QUICKSTART.md` hub. The
remaining gap was conditional pruning: every variant shipped both
guides regardless of `primary_language`. The hook now drops the
inappropriate guide for `python`-only and `typescript`-only renders;
the root pruning matrix asserts presence/absence per variant; and
`README.md` gained a Quickstart-guides section that links the
language-appropriate file via Jinja conditionals (both shown in the
polyglot variant). Files stayed at the project root (not `docs/`)
to preserve the existing hub layout — the `QUICKSTART.md` hub on
its own already directs newcomers to the right guide.

**Effort:** 3 hours | **Impact:** Medium (UX) | **Blocker:** No

---

### 12. Enhance README with Comparison Matrix

**Status:** 📋 Open — tracked in [#74](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/74).

**Add:** Language/tool selection guide

```markdown
| Feature | Python | TypeScript |
|---------|--------|------------|
| Build Tool | uv / pip | npm / yarn |
| Test Runner | pytest | node --test |
| Linter | ruff | eslint |
| Type Checker | mypy | tsc |
| Formatter | ruff | prettier |
| Package Manager | uv (recommended) | npm |
```

**Effort:** 1 hour | **Impact:** Low (UX) | **Blocker:** No

---

## Implementation Timeline

### Week 1: Critical Fixes
- [ ] Fix cookiecutter.json defaults (P0)
- [ ] Convert TypeScript test to ES modules (P0)
- [ ] Add make sync documentation (P0)
- [ ] Fix: **Total time 20 minutes**

### Week 2-3: Code Quality
- [ ] Extract common shell script patterns (P1)
- [ ] Consolidate test suite (P1)
- [ ] Create Makefile fragments (P1)
- [ ] Add smoke test workflow (P1)
- [ ] Subtotal: **~11 hours**

### Week 4: Architecture & Documentation
- [ ] Implement governance YAML (P2)
- [ ] Create quickstart guides (P2)
- [ ] Add Jinja2 filters library (P2)
- [ ] Enhance README (P2)
- [ ] Subtotal: **~9 hours**

**Total effort:** ~20 hours | **Recommended pairing:** Senior engineer + junior

---

## Success Criteria

### Automated
- ✅ Both language variants pass `make validate`
- ✅ Template smoke test workflow succeeds for all combinations
- ✅ Post-gen hook integration test passes
- ✅ No unrendered `{{ cookiecutter.* }}` in generated projects

### Manual
- ✅ New contributor can follow quickstart and pass all checks
- ✅ First-time user complaint rate decreases (measure via GitHub issues)
- ✅ CI/CD can provision projects hands-off (`--no-input` mode)

---

## Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Jinja2 filter library breaks existing templates | Low | High | Add comprehensive tests, version the hooks |
| Makefile fragment system introduces edge cases | Medium | Medium | Smoke test all combinations, CI validation |
| Post-gen hook changes affect TypeScript build | Medium | High | Thorough testing, rollback plan |

---

## Appendix: Code Samples

### ES Module Conversion (test_pre_tool_use_hook.js)

**Pattern:**
```javascript
// CommonJS
const module = require('node:path');
const { fn } = require('node:fs');

// ES Module
import module from 'node:path';
import { fn } from 'node:fs';
```

**Global replacements:**
```sed
s/const test = require.*$/import test from "node:test";/
s/const assert = require.*$/import assert from "node:assert\/strict";/
s/const { \(.*\) } = require.*$/import { \1 } from "node:child_process";/
```

### Shared Shell Library Example

**scripts/lib/common.sh:**
```bash
#!/bin/bash
set -eu

# Shared utilities for validation scripts

log_info() { echo "ℹ️  $*" >&2; }
log_warn() { echo "⚠️  $*" >&2; }
log_error() { echo "❌ $*" >&2; }
log_ok() { echo "✅ $*" >&2; }

find_files_with_pattern() {
  local pattern="$1"
  local paths="${@:2}"
  grep -r -l "$pattern" $paths || true
}

check_no_markers() {
  local markers=("$@")
  local found=0
  for marker in "${markers[@]}"; do
    local matches=$(find_files_with_pattern "$marker" .)
    if [ -n "$matches" ]; then
      log_warn "Found marker: $marker"
      found=$((found + 1))
    fi
  done
  [ $found -eq 0 ]
}
```

---

*Last updated: 2026-05-06 (status reconciled; open items filed as #69–#74)*
*Prepared by: Template Validation Team*

