# ADR-0002: Claude Code repository tooling

- **Status:** Accepted
- **Date:** 2026-10-15
- **Deciders:** Repository owner

## Context and problem statement

The repository is managed with Claude Code. It needs global rules, domain conventions (Proxmox, Terraform, Packer,
GitHub Actions, git), custom commands (`/pr`, `/retro`, `/support`) and safety guarantees,
while keeping token usage low on every session.

## Decision drivers

- Low token cost: only load what the current task needs.
- Safety rules must hold even when the model forgets an instruction.
- Mechanical steps should run on a cheaper model; analysis on the most capable one.
- Conventions must be readable by humans too.

## Considered options

1. A single large `CLAUDE.md` holding every rule and convention.
2. A short `CLAUDE.md`, one skill per domain loaded on demand, commands as user-invoked skills,
   a Sonnet subagent for git operations, and permission rules in `.claude/settings.json`.
3. Conventions in `docs/` only, referenced from `CLAUDE.md`.

## Decision outcome

Chosen option: **option 2**, because skills load only when relevant, the subagent runs git operations on a cheaper model,
and permission rules enforce the critical safety rules mechanically.

| Element | Location | Model |
|---|---|---|
| Global rules | `CLAUDE.md` | Session default |
| Domain conventions | `.claude/skills/<domain>/SKILL.md` | Session default |
| `/pr` review phase | `.claude/skills/pr/` | Session default |
| `/pr` git phase | `.claude/agents/git-operator.md` | Sonnet |
| `/retro` | `.claude/skills/retro/` | Sonnet |
| `/support` | `.claude/skills/support/` | Session default |
| `/apply-review` | `.claude/skills/apply-review/` | Session default |
| Safety: permission rules, bypass mode disabled | `.claude/settings.json` | Not applicable |
| Safety: command guard hook (`PreToolUse`) | `.claude/hooks/guard_dangerous_commands.py` | Not applicable |
| Safety: public-data and secret checks | `.pre-commit-config.yaml`, `.gitleaks.toml` | Not applicable |
| Safety: CI on every PR and push to `main` | `.github/workflows/repository-checks.yml` | Not applicable |
| Session handoffs | `.claude/session-notes/`, git-ignored | Not applicable |

There is no separate `/install` command: the `community-scripts` skill triggers automatically when an install is planned,
and can be called as `/community-scripts <app>`.

### Consequences

- Good: `CLAUDE.md` stays small, so each session starts cheap.
- Good: `terraform apply`, `destroy`, force push and similar commands are blocked by configuration, not only by instructions.
  Permission rules and the hook add up: deny rules still apply whatever the hook returns.
- Bad: conventions are spread across several files; `CLAUDE.md` lists where things live.
- Bad: permission rules and the hook match command text. The hook checks each line and chained command,
  which covers wrapped commands, short flags and absolute paths, but not a script written to disk and run later.
  The written rules still apply.
- Bad: the hook also blocks harmless commands that quote a dangerous one on the same line, such as `echo`.
  Documentation edits that contain such text go through the file editing tools.
- Bad: serial numbers cannot be detected automatically; diffs must be reviewed for them.

### Confirmation

`/pr` checks that skills and `CLAUDE.md` are updated when a convention changes.

## Pros and cons of the options

### Single large CLAUDE.md

- Good, because everything is in one place.
- Bad, because every session pays for every rule, relevant or not.
- Bad, because safety relies only on the model following text.

### Short CLAUDE.md, skills, subagent and permissions

- Good, because loading is on demand and models are matched to tasks.
- Bad, because there are more files to maintain.

### Conventions in docs only

- Good, because conventions are human-oriented.
- Bad, because Claude must be told to read them each time, with no automatic loading or model selection.

## More information

- Claude Code skills, subagents and settings: https://docs.claude.com/en/docs/claude-code

## Revision history

| Date | Change | Reason |
|---|---|---|
| 2026-10-15 | Created | |
| 2026-10-15 | Added `/apply-review`, the command guard hook, disabled bypass mode, public-data checks in pre-commit, a Proxmox token rule for gitleaks, and CI | An external review showed that permission rules can be bypassed, that public-data rules had no enforcement, and that pre-commit only ran locally |
