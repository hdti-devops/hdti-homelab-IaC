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
| Safety: command guard hook (`PreToolUse`), fail-closed launcher | `.claude/hooks/guard_dangerous_commands.py`, `.claude/hooks/run_guard.sh` | Not applicable |
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
- Good: the hook parses commands instead of matching text. It finds the real program behind wrappers and paths,
  unwraps nested commands (`sh -c`, `pwsh -Command`, `eval`, `ssh`, `$(...)`, backticks, `find -exec`),
  and reads options the way each tool does. Quoted text such as a PR title is not mistaken for a command.
- Good: the launcher blocks the command (exit code 2) when no Python 3.8+ interpreter works,
  on any Claude Code version. `onFailure: block` also covers launcher crashes and timeouts, from Claude Code 2.1.295.
- Bad: permission rules are text patterns, and the hook does not inspect a script written to disk and run later.
  The written rules still apply.
- Bad: every line of a heredoc is inspected as a command, and backticks are treated as command substitution.
  Documentation edits that contain such text go through the file editing tools.
- Bad: the hook needs `sh` and Python 3.8+. On Windows, Claude Code provides `sh` through Git Bash.
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
| 2026-10-15 | Rewrote the hook to parse commands, added the fail-closed launcher, `pvesh`/`pvesm`/`pvecm` rules, an IPv4 exception marker, and a wider Proxmox token rule | A second review reproduced hook bypasses, false positives that broke `/pr`, a hook that could not start on macOS (`python` missing), and a fail-closed claim that depended on the Claude Code version |
