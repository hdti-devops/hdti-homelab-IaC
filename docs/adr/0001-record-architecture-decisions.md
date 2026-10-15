# ADR-0001: Record architecture decisions

- **Status:** Accepted
- **Date:** 2026-10-15
- **Deciders:** Repository owner

## Context and problem statement

The homelab will grow over many sessions with Claude Code. Every architecture decision must keep its reasons,
the alternatives considered and why they were rejected, so that later sessions do not reopen or silently contradict it.

## Decision drivers

- The reasons behind each decision must survive across sessions and be readable by Claude at low token cost.
- Alternatives and trade-offs must be explicit.
- Decision history must be preserved when a decision changes.

## Considered options

1. No formal record: decisions live in READMEs and commit messages.
2. Minimal Nygard ADRs: context, decision, consequences.
3. MADR-based ADRs with an added revision history.

## Decision outcome

Chosen option: **MADR-based ADRs with revision history**, stored in `docs/adr/`,
because MADR makes decision drivers and rejected options explicit, which is exactly what must survive across sessions.

Decision first: a new or superseding ADR is delivered in its own `adr/<name>` pull request, reviewed against a checklist,
and merged before any implementation starts. Its status is `Proposed` during review and set to `Accepted` after approval,
before the merge, so ADRs on `main` are never `Proposed`. Corrections of an existing ADR stay in the PR that triggers them.

### Consequences

- Good: each decision is self-contained, linkable and reviewable in pull requests.
- Good: superseding keeps history instead of rewriting it.
- Good: decisions are reviewed as short texts before any code, and implementation PRs no longer reopen them.
- Bad: writing an ADR takes time, so routine configuration is excluded.
- Bad: a new decision and its implementation take two sessions and two PRs.

### Confirmation

The `/pr` command runs the ADR review procedure of the `adr` skill before every pull request,
and stops when implementation relies on an ADR that is not `Accepted` on `main`.

## Pros and cons of the options

### No formal record

- Good, because there is no overhead.
- Bad, because the reasons and rejected alternatives get lost.

### Minimal Nygard ADRs

- Good, because they are short.
- Bad, because rejected alternatives and drivers are optional and tend to be skipped.

### MADR-based ADRs with revision history

- Good, because drivers, options and pros and cons are mandatory sections.
- Bad, because they are longer to write.

## More information

- Template: [.claude/skills/adr/template.md](../../.claude/skills/adr/template.md)
- MADR: https://adr.github.io/madr/

## Revision history

| Date | Change | Reason |
|---|---|---|
| 2026-10-15 | Created | |
| 2026-10-15 | Added the decision-first workflow, the status lifecycle and the decision PR review checklist | The repository owner reviews every decision and wants decisions settled before anything is implemented |
