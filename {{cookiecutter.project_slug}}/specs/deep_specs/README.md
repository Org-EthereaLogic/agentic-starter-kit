# Deep Specs — {{ cookiecutter.project_name }}

Canonical specifications for system architecture and design decisions.

## Overview

This directory contains the project's deep specifications — authoritative documents that define how the system works, what decisions have been made, and why.

Per `DIRECTIVES.md` (CRIT-004), specifications under `specs/deep_specs/` are the **canonical authority** for the system components they describe. When a spec and narrative documentation (README, design notes, comments) contradict, the spec wins.

## Directory Structure

```
specs/deep_specs/
├── README.md                  # This file
├── ADR/                       # Architecture Decision Records
│   ├── 0001-adr-template.md   # (Template — copy to create new ADRs)
│   ├── 0002-initial-structure.md  # Initial scaffold architecture
│   └── ...                    # One file per decision
├── API/                       # API specifications
├── SCHEMA/                    # Data schemas
└── DESIGN/                    # Detailed design docs
```

## Types of Specs

### 1. Architecture Decision Records (ADRs)

ADRs document significant architectural decisions with context, alternatives, and rationale.

**When to write an ADR:**
- Major architectural change
- Significant technology choice
- API redesign
- Data model evolution
- Framework or dependency decision

**When NOT to write an ADR:**
- Bug fixes
- Performance optimizations
- Internal refactors (not affecting contracts)
- Tactical code changes

**File naming:** `NNNN-decision-title.md` (e.g., `0001-use-postgresql.md`)

**Reference:** See `ADR/0001-adr-template.md` for the template.

### 2. API Specifications

Formal definitions of system APIs (REST, gRPC, async, etc.).

- Endpoint definitions
- Request/response schemas
- Authentication & authorization
- Error handling
- Rate limiting

### 3. Data Schemas

Formal definitions of data structures:
- Database schemas
- Message formats
- File formats
- Configuration schemas

### 4. Design Documents

Detailed design docs that explain *how* a subsystem works:
- Component architecture
- State machines
- Interaction patterns
- Performance characteristics

## Workflow: Adding a New Spec

### Step 1: Create the file
```bash
cp specs/deep_specs/ADR/0001-adr-template.md specs/deep_specs/ADR/0002-my-decision.md
```

### Step 2: Edit the spec
Fill in the template with your decision, context, and rationale.

### Step 3: Record in traceability matrix
If `specs/traceability.json` exists (Phase 8), add an entry:
```json
{
  "id": "SPEC-0002",
  "title": "My Decision",
  "source": ["specs/deep_specs/ADR/0002-my-decision.md"],
  "evidence": ["docs/implementation-details.md"],
  "tests": ["tests/test_feature.py"]
}
```

### Step 4: Link from narrative docs
Add cross-references in README.md, ARCHITECTURE.md, etc.:
```markdown
See [ADR-0002: My Decision](specs/deep_specs/ADR/0002-my-decision.md) for the rationale.
```

### Step 5: Create ADR commit
Use conventional commit format:
```bash
git commit -m "docs(adr): add decision about X"
```

## Maintenance

### Versioning ADRs
When ADRs change materially:
1. Append a new section with the date and change summary
2. Do NOT edit existing sections (append-only evidence)
3. Reference the previous version:
   ```markdown
   **Updated:** 2026-05-15  
   **Reason:** Revised after 3-month pilot; see [0002-v2-follow-up.md](0002-v2-follow-up.md)
   ```

### Deprecating Specs
When a spec is superseded:
1. Add a `[SUPERSEDED]` banner at the top:
   ```markdown
   > [SUPERSEDED] 2026-05-15 by [0003-new-approach.md](0003-new-approach.md)
   ```
2. Keep the old spec unchanged (append-only principle)
3. Create a new spec documenting the transition

### Validation
The `make check-traceability` gate (Phase 8) validates that:
- All specs in traceability.json exist
- Linked source/test files exist
- No orphaned specs

## Examples

**ADR Example:** `ADR/0002-initial-structure.md` documents the initial scaffold architecture.

## Getting Help

- **Decision-making:** Read `CONSTITUTION.md §3` for the decision order
- **Governance:** See `DIRECTIVES.md` (especially CRIT-004)
- **Writing ADRs:** Use the template in `ADR/0001-adr-template.md`

---

*Phase 6+ feature — populated as the project evolves.*
