# ADR-0002: Initial Scaffold Architecture

**Status:** DECIDED  
**Date Proposed:** 2026-04-01  
**Date Decided:** 2026-04-15  
**Decision Maker(s):** Architecture Team  
**Stakeholders:** All developers, DevOps, Tech Lead

## Problem Statement

New projects bootstrapped without governance framework, tooling integration, or architectural guidance:

- No canonical source of truth for governance rules
- Inconsistent code quality and testing practices across projects
- Missing traceability between requirements and implementation
- Manual hook and CI setup required for each project
- Unclear testing strategy (unit vs integration vs e2e)

We need a **template that provides**:
1. Pre-configured governance framework (18 directives)
2. Unified validation gate (make validate)
3. Language-agnostic tooling (Python, TypeScript, polyglot)
4. Hook-based branch protection
5. Documentation structure for architectural decisions
6. Clear testing patterns

## Context

Multiple new projects starting simultaneously; dev teams need quick onboarding without reinventing governance. Phase 5 consolidation work has stabilized the scaffold; ready for production use.

## Decision

**We adopt a five-layer scaffold architecture:**

1. **Layer 1**: Navigation (CLAUDE.md, AGENTS.md, GEMINI.md)
2. **Layer 2**: Constitutional foundation (CONSTITUTION.md, DIRECTIVES.md, SECURITY.md)
3. **Layer 3**: Agent specialization (commands, agents, hooks in `.claude/`)
4. **Layer 4**: Runtime enforcement (`.githooks/` primary boundary;
   `.claude/hooks/pre-tool-use.js` agent-layer defense in depth)
5. **Layer 5**: External validation (Makefile, scripts, CI workflows)

## Rationale

This layered approach provides:

- **Progressive disclosure**: Developers can learn at their own pace (Layer 1 → 2 → 3+)
- **Self-reinforcing**: CI enforces what hooks cannot catch
- **Multi-language support**: Same governance rules for Python and TypeScript
- **Extensible**: New phases add to docs/ and specs/ without breaking existing layers
- **Testable**: Each layer has validation gates (marker-scan, governance-check, hooks-test)

### Architecture Decisions

**Governance Rules in YAML** (not code):
- Single source of truth (governance-rules.yaml)
- Machine-readable for CI/CD integration
- Queryable via Python loader
- Decoupled from implementation

**Makefile Fragments** (not monolithic):
- Reduces maintenance burden (150 → 50 lines)
- Clear separation of concerns
- Easy to extend without conflicts
- Language-specific targets cleanly isolated

**Hook-based Protection** (Layer 4):
- Blocks forbidden patterns before tool execution
- Works with all agents (Claude Code, Gemini, etc.)
- Registered in `.claude/settings.json`
- Tested via regression suite (CRIT-008)

**Test Consolidation** (hook_test_spec.json):
- Single source of truth for all 18 test cases
- Python and TypeScript drivers iterate the spec at import time, so
  the implementations cannot drift
- JSON spec is parsed by both languages with the standard library
  (no PyYAML / `js-yaml` dependency)

## Implementation

### Bootstrap Phase (Completed)
- ✅ Create scaffold with Layer 1-2 files
- ✅ Implement Layer 4 hook and regression suite
- ✅ Establish validation gates (Layer 5)

### Consolidation Phase (Completed — Phase 5)

- ✅ Test consolidation (hook_test_spec.json)
- ✅ Shell script refactoring (common.sh utilities)
- ✅ Makefile fragment system
- ✅ Governance rules in YAML
- ✅ Quickstart guides (language-aware)

### Phase 6+ (Future)
- [ ] Architecture decision record templates
- [ ] Security requirements specifications
- [ ] Traceability matrix (specs/traceability.json)
- [ ] CI automation for smoke tests
- [ ] Observability setup (monitoring, logging)

## Success Criteria

✅ **Achieved:**
- 18 validation gates functional (marker-scan, governance-check, hooks-test, lint, test, etc.)
- All governance directives documented (DIRECTIVES.md)
- Regression suite fully passing (18/18 tests)
- Shell scripts bash 3.2 compatible
- Makefile 67% reduction in duplication
- Zero deprecation warnings during setup

**Ongoing:**
- New projects use this scaffold
- Validation pass rate > 95% in generated projects
- Zero critical issues in Phase 6 security audit

## Consequences

### Positive
- Consistent governance across all projects
- Reduced time-to-deploy for new projects (setup: 2-5 minutes)
- Enforced code quality and testing standards
- Clear decision-making framework (CONSTITUTION.md)
- Language-agnostic: same rules for Python, TypeScript, polyglot

### Negative / Risk
- Scaffold is opinionated; not all projects fit
  (Mitigation: Post-gen hook allows pruning files; see cookiecutter.json)
  
- Governance rules require discipline; not automatically enforced by all tools
  (Mitigation: Layer 4 hook + CI gates catch violations early)

## Related Decisions

- [ADR-0001 Template](0001-adr-template.md) — framework for future ADRs
- DIRECTIVES.md — the 18 governance rules
- CONSTITUTION.md — foundational principles

## References

- `CONSTITUTION.md` — Foundational principles
- `DIRECTIVES.md` — 18 governance directives with enforcement
- `CLAUDE.md` — Claude Code quick reference
- `AGENTS.md` — Full agent operating rules
- `.github/workflows/ci.yml` — CI validation

---

**Decision History:**
- 2026-04-01: Proposed by Architecture Team
- 2026-04-15: Decided and approved
- 2026-05-02: Phase 5 consolidation complete; architecture validated
