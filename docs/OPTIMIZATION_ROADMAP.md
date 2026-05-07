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

**Status:** 📋 Open — tracked in [#69](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/69).

**Problem:** Python and TypeScript test files are 90% identical

**Option A — Template-based generation (preferred):**
- Create `tests/fixtures/test_template.jinja2`
- Post-gen hook renders to `.py` or `.js`
- Single source of truth for test logic

**Option B — Shared test utilities:**
- Extract common test patterns to `tests/lib/`
- Both `.py` and `.js` import/require shared logic
- Separate language-specific parts

**Effort:** 4 hours (Option A) | 2 hours (Option B) | **Impact:** High | **Blocker:** No

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
Makefile.typescript        # typescript-specific (eslint, tsc, vitest)
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
- ✅ All tool inclusion combos (databricks, codacy, codecov, snyk, sbom)
- ✅ Validation gate passes

**Effort:** 2 hours | **Impact:** High | **Blocker:** No

---

### 8. Add Integration Test for Post-Gen Hook

**Status:** 📋 Open — tracked in [#70](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/70).

**Test:** Verify hook correctly removes language-inappropriate files

```bash
# tests/test_post_gen_hook.sh

test_python_variant() {
  render_template primary_language=python
  assert_file_exists pyproject.toml
  assert_file_not_exists package.json
  assert_file_exists tests/test_pre_tool_use_hook.py
  assert_file_not_exists tests/test_pre_tool_use_hook.js
}

test_typescript_variant() {
  render_template primary_language=typescript
  assert_file_exists package.json
  assert_file_not_exists pyproject.toml
  assert_file_exists tests/test_pre_tool_use_hook.js
  assert_file_not_exists tests/test_pre_tool_use_hook.py
}
```

**Effort:** 1 hour | **Impact:** Medium | **Blocker:** No

---

## Architecture Improvements (3-4 weeks)

### 9. Implement Jinja2 Filter Library

**Status:** 📋 Open — tracked in [#71](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/71).

**Problem:** Repetitive filters in templates (e.g., `|lower|replace('-','_')`)

**Solution:** Create custom filters in `hooks/jinja_filters.py`

```python
@filter
def to_python_package_name(s):
    """Convert project name to valid Python package name."""
    return s.lower().replace('-', '_').replace(' ', '_')
```

**Usage in templates:**
```jinja2
python_package_name = "{{ cookiecutter.project_name | to_python_package_name }}"
```

**Benefit:** Reusable, testable, DRY

**Effort:** 2 hours | **Impact:** Low (nice-to-have) | **Blocker:** No

---

### 10. Extract Governance Rules to Data-Driven Config

**Status:** 📋 Open — tracked in [#72](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/72).

**Current:** Hardcoded rules in `scripts/check-governance.sh`

**Proposed:** `governance.yaml`
```yaml
required_files:
  - CONSTITUTION.md
  - DIRECTIVES.md
  - SECURITY.md
  - AGENTS.md
  - CLAUDE.md
  - README.md
  - Makefile

required_directories:
  - .claude
  - tests
  - scripts
  - .github/workflows

prohibited_markers:
  - "TODO:"
  - "FIXME:"
  - "<your name>"
  - "<your email>"
```

**Benefits:**
- Single source of truth
- Easier to audit requirements
- Testable in isolation

**Effort:** 2 hours | **Impact:** Medium | **Blocker:** No

---

## Documentation & UX (1-2 weeks)

### 11. Create Language-Specific Quick Start Guides

**Status:** 📋 Open — tracked in [#73](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/73).

**Files to create:**
- `docs/QUICKSTART-PYTHON.md` — pytest, ruff, mypy workflow
- `docs/QUICKSTART-TYPESCRIPT.md` — vitest, eslint, tsc workflow
- `docs/CONTRIBUTING.md` — Updated with tool-specific guidance

**Content:**
- How to run tests
- How to check types
- How to lint
- How to format code
- IDE setup instructions

**Effort:** 3 hours | **Impact:** Medium (UX) | **Blocker:** No

---

### 12. Enhance README with Comparison Matrix

**Status:** 📋 Open — tracked in [#74](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/74).

**Add:** Language/tool selection guide

```markdown
| Feature | Python | TypeScript |
|---------|--------|------------|
| Build Tool | uv / pip | npm / yarn |
| Test Runner | pytest | vitest |
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

