# MCP Server Policy — {{ cookiecutter.project_name }}

> **Authority.** This document governs the use of Model Context
> Protocol (MCP) servers in this project. It is **tier 2** in the
> decision order (sits below `SECURITY.md` and `CONSTITUTION.md`,
> above `DIRECTIVES.md`-relative material). When this policy
> conflicts with `SECURITY.md` on disclosure or scope, `SECURITY.md`
> wins per `CONSTITUTION.md §3`.
>
> **Scope.** Every MCP server entry in `.mcp.json` (project-level)
> and any MCP server an operator runs against this project from a
> user-level config (`~/.claude.json`).

---

## §1 — Trust model

MCP servers are **untrusted boundaries**, regardless of source.
This is not a comment about quality; it is a structural fact:

- An MCP server runs in the same process trust boundary as the
  operator's agent runtime. Any tool the server exposes can be
  invoked by the agent on the operator's behalf.
- The agent is the most-privileged caller; the MCP server is the
  least-trusted dependency. This inversion is the source of the
  risk class.
- Tool output from an MCP server is **content**, not **command**
  — it can carry prompt-injection payloads that the agent's
  reasoning loop will treat as instructions if not bounded
  (per `THREAT_MODEL.md §2 ASI-02`).

The default `.mcp.json` shipped with this project is empty. Every
addition is a deliberate trust extension and follows §3.

## §2 — What the project does and does not ship

Shipped on default branch:

- `.mcp.json` with an empty `"mcpServers": {}` map.
- This policy document (`docs/MCP_POLICY.md`).

Not shipped, by design:

- No third-party MCP server entries.
- No operator-specific tokens, credentials, or paths.
- No secret material of any kind.

The empty map is intentional. Operators add MCP servers explicitly
following §3, with each addition reviewed under §4.

## §3 — Adding an MCP server

To add an MCP server to `.mcp.json` for this project:

1. **Justify the addition.** Open an ADR under
   `specs/deep_specs/ADR/` documenting:
   - The capability the MCP server provides.
   - The smallest scope of access that satisfies the need.
   - The alternative options considered (including "do not add").
   - The reviewer who audited the server's source.
2. **Audit the server.** Run through the §4 checklist before
   editing `.mcp.json`. Record the audit outcome in the ADR.
3. **Configure least privilege.**
   - Set credentials to read-only when the workflow allows.
   - Bound filesystem access to the project root, never to `$HOME`
     or `/`.
   - Use ephemeral or scoped tokens; never long-lived static
     credentials.
4. **Update `.mcp.json`** with the configured entry. Run
   `scripts/check-governance.sh` to verify the file remains
   well-formed JSON with the required `mcpServers` key.
5. **Commit explicitly.** Stage `.mcp.json` and the ADR together;
   do not stage other files (per `IMP-004`).

## §4 — Audit checklist

Run through every item before adding an MCP server. A `no` on any
required item blocks the addition.

| Item | Required | What to check |
|---|---|---|
| 1. Source identity | yes | Who maintains the server? Is the maintainer reachable for security disclosure? |
| 2. Source repository | yes | Public source URL; review the last 5 commits for anything unexpected; verify the published binary's source is the repo. |
| 3. Permission scope | yes | What does the server let the agent do? List the tools it exposes. The fewer, the better. |
| 4. Authentication mode | yes | Does the server require credentials? Are scoped tokens supported? Can read-only credentials be used? |
| 5. Network egress | yes | Does the server make outbound network calls? Where to? Logged? |
| 6. Filesystem access | yes | Does the server read or write the local filesystem? Bounded to the project root, or wider? |
| 7. Update cadence | yes | How does the server receive updates? Automatic or operator-controlled? Pinned to a known version? |
| 8. Disclosure channel | yes | Does the server have a SECURITY.md or equivalent? |
| 9. Recent advisories | yes | Has the server had a CVE or security advisory in the last 12 months? If so, is it patched? |
| 10. Operational fit | recommended | Does the project actually need this capability, or is it convenience? Convenience is not a justification per `CONSTITUTION.md §P6` (smallest sufficient change). |

## §5 — Curated candidate list

The following MCP servers have been evaluated as common starting
points. **Listing here is not endorsement** — every operator runs
the §4 audit independently before adding any of these to
`.mcp.json`.

| Candidate | Source | Typical use | First-look caveat |
|---|---|---|---|
| `@modelcontextprotocol/server-filesystem` | Anthropic reference | Read project files | Always pin to a project-relative path; never `$HOME` |
| `@modelcontextprotocol/server-git` | Anthropic reference | Read git history | Read-only by configuration; do not enable write access |
| `@modelcontextprotocol/server-github` | Anthropic reference | Read GitHub repo metadata | Use a fine-scoped PAT; set token to `read:public_repo`, never `repo` |
| `@modelcontextprotocol/server-puppeteer` | Anthropic reference | Browser automation | High-privilege; consider whether a static fixture would suffice |
| `@modelcontextprotocol/server-slack` | Anthropic reference | Read Slack messages | Bot-token scope only; review what channels the bot joins |

Anthropic-authored servers carry the same trust profile as any
third-party server in this policy. They are not a free pass.

## §6 — Removing an MCP server

To remove an entry from `.mcp.json`:

1. Open an ADR documenting the removal reason (deprecated, unused,
   security advisory, scope reduction).
2. Edit `.mcp.json` to drop the entry.
3. Rotate any credentials the server held — operator action,
   recorded in the ADR.
4. Verify the agent's behavior on the next session does not
   silently retry the removed server (Claude Code surfaces
   missing-server errors in this case; treat them as expected).

## §7 — Periodic review

Every six months (or sooner on advisory), run §4 against every
entry in `.mcp.json` and record results under
`report/<UTC-timestamp>-mcp-audit.md`. Discrepancies between the
recorded audit and current configuration are findings.

## §8 — Disclosure

Vulnerabilities affecting any MCP server in this project's config
are reported through the channel in `SECURITY.md` and treated as
agent-tooling supply-chain issues per `SECURITY.md §Scope`.

---

## References

- Model Context Protocol — <https://modelcontextprotocol.io>
- MCP server registry — <https://github.com/modelcontextprotocol/servers>
- `THREAT_MODEL.md` §2 ASI-02 (Tool Misuse) and ASI-04 (Agentic
  Supply Chain).
- `CONSTITUTION.md §P3` (Hard Policy Boundaries) and `§P6`
  (Smallest Sufficient Change).

---

*Authoritative since first commit. Amended via ADR.*
