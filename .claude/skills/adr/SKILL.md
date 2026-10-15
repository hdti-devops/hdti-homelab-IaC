---
name: adr
description: Create, review and update Architecture Decision Records in docs/adr/. Covers the decision-first workflow (decision PR before implementation), status lifecycle, and the review checklist for decision PRs. Use when a choice has real alternatives, when a change may affect an existing decision, and for the ADR review required before every pull request.
---

# Architecture Decision Records

Use the most capable model available for ADR analysis.

## When an ADR is needed
A choice with real alternatives that is costly to reverse or shapes future work:
tool selection, placement strategy, network, DNS or TLS design, security model, state layout, conventions.
Routine configuration does not need one.

## Decision-first workflow
A **new ADR, or one that supersedes another**, is delivered in its own decision PR, reviewed and merged
before any implementation branch starts. Decision and implementation are two successive sessions.
- Branch `adr/<name>`, commits `docs(adr): ...`, PR body from the decision template in the `git-conventions` skill.
- The decision PR may also carry the conventions derived from the decision: `CLAUDE.md`, skills, templates.
  It carries no implementation: no Terraform, Packer, workflow, script or service installation.
- Not required for corrections or clarifications of an existing ADR, bugfixes, runbooks or documentation.
  These revisions stay in the PR of the work that triggered them.

## Status lifecycle
- `Proposed` while the decision PR is under review.
- When the user approves the decision, `/pr` adds a final commit setting `Accepted` and the acceptance date, then the user merges.
- On `main`, an ADR is always `Accepted`, `Deprecated` or `Superseded`, never `Proposed`.
- Implementation may only rely on an ADR that is `Accepted` on `main`.

## Create
1. Number = highest existing number + 1, four digits. File: `docs/adr/NNNN-kebab-case-title.md`, from [template.md](template.md).
2. List at least two real options with honest pros and cons. Make decision drivers explicit.
   Ask the user for drivers you do not know.
3. Set status `Proposed`. Dates are ISO `YYYY-MM-DD`.
4. Add a row to the index in `docs/adr/README.md`.

## Review checklist for decision PRs
Reviewers, `/pr` and `/apply-review` check each item:
1. The context is factual and verified, with no invented infrastructure facts.
2. At least two realistic options are compared, with honest pros and cons.
3. Decision drivers are explicit, and the chosen option follows from them.
4. Negative consequences and risks are named.
5. Triggers to revisit the decision are stated.
6. Derived conventions (`CLAUDE.md`, skills, templates) are included and consistent with the ADR.
7. The PR contains no implementation.
8. Status is `Proposed` during review and becomes `Accepted` only after approval.

## Review (before every PR)
1. List the ADRs related to the changed components.
2. Decide whether the change contradicts, extends or corrects any of them.
3. Correction or clarification of the same decision: edit in place and add a Revision history row (date, change, reason).
4. New decision replacing an old one: create a new ADR with `Supersedes ADR-NNNN` through a decision PR, and set the old
   status to `Superseded by ADR-MMMM`. Never delete or rewrite the old decision.
5. Never edit an ADR only to mark it as reviewed.
