# SBOM Generation and Review Policy

> **SWEBOK anchor:** Software Security KA (SWEBOK v4 Ch 13 §1, §4.6) —
> supply-chain transparency through a machine-readable inventory of
> every dependency the project ships.
>
> **GAPs closed:** GAP-022 (SBOM policy + generation tooling) and
> GAP-044 (CycloneDX / SPDX standard anchor, alongside
> `docs/STANDARDS.md`).

---

## 1. Scope

A Software Bill of Materials (SBOM) is the authoritative list of the
components — direct and transitive — that the project depends on. This
policy governs how the SBOM is produced, when it is refreshed, where it
is stored, and what a reviewer is expected to check.

The SBOM covers the project's resolved dependency graph:

- the Python environment (from pyproject.toml and its lock), and/or
- the Node dependency tree (from package.json and its lock),

depending on the project's `primary_language`. A polyglot project emits
one SBOM per ecosystem.

This policy exists only when the template was rendered with
`include_sbom == "yes"`. When SBOM support is not selected, the
generator, this document, and the CI job are all pruned together.

---

## 2. Format

SBOMs are emitted in **CycloneDX** JSON. CycloneDX is the format the
`make sbom` job accepts; `docs/STANDARDS.md` records the accepted
standard versions (CycloneDX 1.6 / SPDX 2.3) as the authoritative
register entry.

Output files, one per ecosystem, are written under the `sbom/`
directory at the project root:

```
sbom/sbom-python.cdx.json   ← Python path / polyglot
sbom/sbom-node.cdx.json     ← TypeScript path / polyglot
```

These are build artifacts, not source: `sbom/` is regenerated on demand
and is not committed to version control.

---

## 3. Generation

Regenerate the SBOM locally with:

```sh
make sbom
```

which runs `scripts/generate-sbom.sh`. The script introspects each
ecosystem that is present and skips the one that is not, so it is safe
to run in any of the three language configurations.

Required tooling (installed on demand, not vendored):

| Ecosystem | Tool | Install |
| --- | --- | --- |
| Python | `cyclonedx-py` | `pip install cyclonedx-bom` |
| Node | `cyclonedx-npm` | `npm install -g @cyclonedx/cyclonedx-npm` |

For the Python path the SBOM is generated against the resolved virtual
environment (`.venv`, created by `make sync`) so it reflects the exact
pinned versions, falling back to the active interpreter when no `.venv`
is present. If a required tool is missing the script warns and continues
rather than emitting a partial SBOM under a misleading filename.

---

## 4. Cadence and retention

The `sbom` job in `.github/workflows/ci.yml` regenerates the SBOM on
every push and pull request. For the Python path it syncs
production-only dependencies (`uv sync --no-dev`) so the SBOM describes
what actually ships, not the development toolchain.

Each run uploads the `sbom/` directory as a build artifact named
`sbom-<commit-sha>`, retained for 90 days. Because every commit that
reaches CI produces an archived SBOM, every release tag has a
corresponding, retrievable bill of materials without a separate release
step.

---

## 5. Review

An SBOM is only useful if someone reads it. On any change that alters
the dependency graph, the reviewer checks:

1. **New or upgraded components** — is each addition intentional, and
   does it come from a trusted publisher?
2. **License drift** — does a new or bumped component introduce a
   license incompatible with the project's own `license` choice?
3. **Known-vulnerable versions** — cross-reference the components
   against the project's vulnerability tooling (e.g. the Snyk gate when
   enabled) and reject or pin around advisories with no fix.
4. **Unexpected transitives** — a large jump in transitive count is a
   signal to inspect what pulled them in.

Findings that cannot be resolved in the change itself are recorded as
follow-up security work rather than silently merged.

---

## 6. Constitutional alignment

| Principle | Application |
| --- | --- |
| `P2` — Evidence Traceability | the SBOM is machine-readable evidence of exactly what the project depends on, archived per commit |
| `P4` — Explicit Failure | the generator exits non-zero on a real generation error rather than writing a partial SBOM |
| `P5` — Append-Only Evidence | each CI run's SBOM is retained as a dated artifact, never overwritten in place |

Cross-reference `SECURITY.md` (the security-program entry point) and
`docs/STANDARDS.md` (the standards register that anchors the accepted
SBOM formats).
