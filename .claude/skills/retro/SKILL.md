---
name: retro
description: End-of-session wrap-up. Checks that durable context is documented, writes a local handoff note and prints the prompt to resume in the next session. Only when the user runs /retro.
disable-model-invocation: true
model: sonnet
---

# /retro

This command does not edit tracked files. Durable changes belong to a PR.

## Steps
1. **State.** Run `git status`, `git branch --show-current`, `git log --oneline -10`,
   and `gh pr view --json url,state` if a PR exists for the branch.
2. **Session review.** From the conversation, list what was done, decisions taken with their ADR,
   pending work, blockers, questions waiting for the user, and gotchas.
3. **Durability check.** List facts and decisions from this session that are not yet in the repo
   (inventory, roadmap, ADRs, runbooks, skills). If any exist, warn the user: they must go through `/pr`
   now, or become the first task of the next session.
4. **Handoff file.** Write `.claude/session-notes/<YYYY-MM-DD>-<branch-slug>.md`:

   ```markdown
   # Session handoff: <date>, <branch>
   ## State
   Branch, PR URL and state, last commit, uncommitted changes.
   ## Done
   ## Decisions
   ## Next steps (ordered)
   ## Open questions for the user
   ## Gotchas
   ```

5. **Output.** Give the user a short summary in French, then a fenced block titled "Prompt pour la prochaine session".
   The prompt, in French, says to read `CLAUDE.md` and the handoff file by path, and states the next task.
6. Tell the user to run `/clear` or open a new session, then paste the prompt. Claude cannot close the session itself.
