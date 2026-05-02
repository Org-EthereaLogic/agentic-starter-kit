# IDE Prompt — Agentic Starter Kit Build

> **How to use this:** open VS Code Insiders, navigate to
> `/Users/etherealogic-2/Dev/agentic-starter-kit`, start a new
> Claude Code session in this directory, and paste the
> `## PROMPT (paste from here)` section below as your first message.
>
> The agent has full filesystem access in this directory and read
> access to the source projects (`govforge`, `sdlc_app`, `ADWS_PRO`)
> for porting commands and agents.

---

## PROMPT (paste from here)

You are building out the `agentic-starter-kit` template, a
cookiecutter-based scaffold that ships a five-layer agentic
governance stack plus a complete bridge to SWEBOK Guide v4.0a
(September 2025). The build's contract is fully specified in four
planning files at the repo root.

### Step 1 — Read the planning files in order

Before authoring anything, read all four in this order:

1. `BRIEFING.md` — mission, the five layers, the eight constitutional
   principles, the eighteen directives, authorial style rules.
2. `SWEBOK_GAP_REGISTER.md` — every gap mapped to its deliverable
   file. Use this as the master checklist. The build is done when
   every row reads `landed`.
3. `BUILD_PLAN.md` — phased build order with file inventory and
   per-phase gates.
4. `COMMAND_AND_AGENT_SPECS.md` — canonical text for new commands
   (`/sync`, `/threat-model`, `/check-traceability`) and the new
   `security-reviewer` agent that cannot be ported from existing
   projects.

After reading, summarize back to me in one paragraph what you
understand the build to be. Do not start authoring until I confirm.

### Step 2 — Execute phases sequentially

Run through Phase 0 through Phase 11 in `BUILD_PLAN.md`. For each
phase:

1. **Author** every file listed in the phase using the rules in
   `BRIEFING.md §6` (declarative prose, no stub markers, no
   fabricated metrics, ~80-column wrap).
2. **Verify** — run the phase gate listed in `BUILD_PLAN.md`. If it
   fails, fix and re-run before moving on.
3. **Commit** with a conventional message:
   `chore(scaffold): land Phase N — <phase name>` on a branch
   `feat/scaffold-phase-<N>`. Never commit to `main`. Never use
   `--no-verify`.
4. **Update the gap register** — change `Status` cells in
   `SWEBOK_GAP_REGISTER.md` from `planned` to `landed` for every
   row delivered by the phase. Commit that update as part of the
   same phase commit.
5. **Wait** for me to merge the phase PR before starting the next
   phase.

### Step 3 — Source projects for porting

These commands and agents are ports — not new authoring. Pull from
the user's existing projects and parameterize per
`COMMAND_AND_AGENT_SPECS.md` "Note on porting":

- Slash commands (Phase 9, 12 of 16):
  port from `/Users/etherealogic-2/Dev/govforge/.claude/commands/`.
- Agents (Phase 10, 5 of 7):
  port from `/Users/etherealogic-2/Dev/govforge/.claude/agents/`.

If `govforge` is missing a command/agent, check `sdlc_app` and
`ADWS_PRO` before falling back to authoring from scratch.

### Step 4 — Hard rules during the build

- **No stub markers** (TODO, FIXME, TBD, PLACEHOLDER) anywhere in
  the template's tracked files. CRIT-001 applies to this repo too.
- **No fabricated metrics, dates, or version pins.** If a number is
  required and not measured, use an angle-bracket placeholder
  (`<TBD: target measured at first benchmark>`), not an invented
  number.
- **No work on `main`.** Use `feat/scaffold-phase-<N>` branches.
  The protected-branch hook is not yet installed in this repo, so
  this rule is on you.
- **No `--no-verify`.** CRIT-007.
- **No skipping a phase gate.** If something blocks, surface it and
  ask me. Do not skip ahead.
- **Stage explicitly.** Never `git add -A` or `git add .`. IMP-004.
- **One phase per PR.** Eleven phases means ~eleven PRs. This is
  the dogfood test — the template's own discipline applies to its
  build.

### Step 5 — When blocked

If you encounter any of the following, stop and ask:

- A SWEBOK chapter reference in `SWEBOK_GAP_REGISTER.md` whose
  content you can't locate confidently.
- A cookiecutter Jinja2 template that you can't make render
  cleanly across all language paths.
- A conflict between `BRIEFING.md` and content ported from
  `govforge` that would require a substantive policy choice.
- A test failure in `tests/test_pre_tool_use_hook.py` that suggests
  a real hook bypass rather than a test bug.
- Any moment where you would otherwise need to make up a number,
  date, or business-specific detail.

When asking, propose 2–3 specific options with the tradeoffs of
each. I'll pick.

### Step 6 — Validation at the end

Before declaring the build done, run Phase 11's full validation:

1. `pipx run cookiecutter . --no-input -o /tmp/test-python/`
   (Python path with all integrations on)
2. `pipx run cookiecutter . --no-input -o /tmp/test-typescript/
   --extra-context primary_language=typescript`
3. `pipx run cookiecutter . --no-input -o /tmp/test-minimum/
   --extra-context include_codacy=no include_codecov=no
   include_snyk=no include_sbom=no`

For each instantiated project:

```bash
cd <slug>
git init
git checkout -b feat/initial
make sync
make validate
make hooks-test
make check-traceability
```

All gates pass. Then verify the hook actually blocks:

```bash
git checkout main 2>/dev/null || git checkout -b main
echo "test" > scratch.txt
git add scratch.txt
# Attempt commit; expect Layer 4 hook to block
git commit -m "test: should fail"
```

(The block is enforced via Claude Code at runtime, not raw `git`,
so this test runs through Claude Code's tool surface or by piping
the matching JSON payload to the hook directly per `.claude/hooks/README.md`.)

When all three test instantiations pass, write the success
artifact:

`{{cookiecutter.project_slug}}/report/<UTC-timestamp>-validate-pass.md`

…then commit and open the final PR titled
`chore(scaffold): land Phase 11 — validation pass`.

### Step 7 — Definition of done

The build is complete when all of the following hold:

- [ ] Every row in `SWEBOK_GAP_REGISTER.md` reads `landed`.
- [ ] All three test instantiations (Python, TypeScript, minimum)
      pass `make validate`, `make hooks-test`, and
      `make check-traceability`.
- [ ] Eleven phase PRs are merged to `main` of this template repo.
- [ ] The success artifact exists in the most recent test
      instantiation's `report/` directory.
- [ ] No commit in this template's history used `--no-verify` or
      committed to `main` directly.
- [ ] `METHODOLOGY.md` reads cleanly as a standalone essay (it
      should make sense to a reader who never sees the template).

When all six conditions hold, post a summary in the chat with:
- The total file count authored
- The total commit count
- The list of `landed` GAP IDs
- Any deferred-with-justification items (and which ADR records
  the deferral)

---

## END PROMPT

---

## Notes for the human (you)

A few things to keep in mind once the agent is running:

1. **You are the merge gatekeeper.** The agent will open PRs but
   not merge them. Review each phase PR before approving — this is
   the dogfood-test version of the methodology and your eyes are
   load-bearing.

2. **Eleven phases is roughly right, but the agent may split.**
   If a phase grows beyond ~15 files or ~2000 lines of authored
   content, the agent should split it into sub-phases. That's fine.
   The gap register is what defines done, not the phase count.

3. **The `METHODOLOGY.md` essay is the deliverable that survives
   without the template.** If you ever rewrite the template,
   `METHODOLOGY.md` is what you keep. Treat its review with the
   same care as `CONSTITUTION.md`.

4. **Compute estimate.** Full build is ~80–100 files, ~30k–50k
   words of authored content, plus ~10 validation runs. Plan on
   2–4 hours of agent time depending on how often you stop to
   adjust. Phase boundaries are natural break points.

5. **If the agent drifts from the briefing**, the simplest
   correction is: "Re-read `BRIEFING.md §6` and apply." Most
   drift shows up as hedging language, fabricated metrics, or
   stub markers — all explicitly forbidden in §6.

6. **The `/sync` discussion from our last conversation turn is
   now part of the build.** It's CMD-013 in the gap register, with
   full canonical text in `COMMAND_AND_AGENT_SPECS.md`. The agent
   doesn't need to recreate that conversation.

7. **After Phase 11, run `/sync` on the template repo itself.**
   It's the right shakedown for the discipline the template is
   teaching.

That's the full handoff. Open VS Code Insiders, paste the prompt,
and the build runs from there.
