---
name: pr
description: Finalize the current task into a pull request. Reviews docs, ADRs, runbooks and workflows, runs validations, then delegates branch, commit, push and PR creation to the git-operator agent. Only when the user runs /pr.
disable-model-invocation: true
argument-hint: "[optional notes for the PR]"
---

# /pr

## Phase 1: review (current model)

1. **Scope.** Run `git status`, `git diff`, and `git diff main...HEAD` when on a branch. List the changed components.
   If untracked or modified files look unrelated to the task, stop and ask the user how to handle them.
   **Decision-first check** (`adr` skill):
   - On an `adr/` branch, the diff must contain no implementation. Apply the decision PR review checklist.
   - On any other branch, if the diff adds a new or superseding ADR together with implementation, or implements
     something that relies on an ADR missing from `main` or not `Accepted` there, stop and propose to split:
     the decision PR first, the implementation after it is merged.
2. **Documentation sync.** For each changed component, check and update when facts changed:
   - `docs/architecture/inventory.md`: hosts, IPs, VMIDs, placement, access.
   - `docs/roadmap.md`: status of the items worked on.
   - ADRs: run the review procedure of the `adr` skill.
   - Runbooks: every installed or changed service has an up-to-date runbook (`runbook` skill).
   - READMEs of Terraform modules, Packer templates and workflows when present.
   - `CLAUDE.md` and skills, only when a convention changed. When an ADR that defines a convention changes
     (for example ADR-0003 naming and VMIDs), update every skill that restates it, such as the `proxmox` skill.
3. **Validation.** Run every applicable check and record the result of each:
   - `pre-commit run --all-files`. It only sees tracked files: run `git add -N <new files>` first, then `git reset`.
     Its gitleaks hook scans staged content only; the full-history scan runs in CI.
   - `python -m unittest discover -s .claude/hooks -v` when `.claude/hooks/` changed.
   - The checks listed in the `terraform`, `packer` or `github-actions` skill for the files that changed.
   Never report a check as passed unless it ran and passed. Say why a check could not run.
4. **Final diff review.** Look for unintended changes, hardcoded values, secrets, generated files,
   and data that must not be public (public IP, MAC addresses, serials).
5. **Proposal.** Following the `git-conventions` skill, present to the user:
   summary, validation results table, risks, open issues, branch name, commit message(s), PR title and PR body.
   Wait for explicit approval. Apply requested changes and ask again.

## Phase 2: git operations (delegated)

After approval, launch the `git-operator` agent with the approved branch name, the exact list of files to stage,
the commit message(s), the PR title and the PR body.
If a PR is already open for the branch, for example after `/apply-review`, say so: the agent pushes the new commits
to it instead of creating a PR.
Relay its result to the user: PR URL, or the exact error and what you suggest.

## Accepting a decision PR
When the user approves the decision of an open `adr/` PR, run `/pr` again: set the ADR status to `Accepted`
with the acceptance date and update the ADR index, then delegate one commit `docs(adr): ✅ accept ADR-NNNN`.
The user merges the PR afterwards.
