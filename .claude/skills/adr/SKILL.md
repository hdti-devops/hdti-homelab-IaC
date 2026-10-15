---
name: adr
description: Create, review and update Architecture Decision Records in docs/adr/. Use when a choice has real alternatives, when a change may affect an existing decision, and for the ADR review required before every pull request.
---

# Architecture Decision Records

Use the most capable model available for ADR analysis.

## When an ADR is needed
A choice with real alternatives that is costly to reverse or shapes future work:
tool selection, placement strategy, network, DNS or TLS design, security model, state layout, conventions.
Routine configuration does not need one.

## Create
1. Number = highest existing number + 1, four digits. File: `docs/adr/NNNN-kebab-case-title.md`, from [template.md](template.md).
2. List at least two real options with honest pros and cons. Make decision drivers explicit.
   Ask the user for drivers you do not know.
3. Status is `Proposed` until the user approves, then `Accepted`. Dates are ISO `YYYY-MM-DD`.
4. Add a row to the index in `docs/adr/README.md`.

## Review (before every PR)
1. List the ADRs related to the changed components.
2. Decide whether the change contradicts, extends or corrects any of them.
3. Correction or clarification of the same decision: edit in place and add a Revision history row (date, change, reason).
4. New decision replacing an old one: create a new ADR with `Supersedes ADR-NNNN`, and set the old status to
   `Superseded by ADR-MMMM`. Never delete or rewrite the old decision.
5. Never edit an ADR only to mark it as reviewed.
