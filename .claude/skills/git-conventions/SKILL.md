---
name: git-conventions
description: Branch naming, Conventional Commits with emojis, PR title and body template, and git change-safety rules for this repo. Use for any branch, commit or pull request work.
---

# Git conventions

## Branches
Short, descriptive, English, kebab-case: `feature/<name>`, `bugfix/<name>`, `hotfix/<name>`, `refactor/<name>`, `docs/<name>`.
One session = one branch = one PR, branched from an up-to-date `main`.

## Commits
Format: `<type>(<optional scope>): <emoji> <imperative subject>`, English, subject of 72 characters or less.
Example: `docs(adr): 📝 add naming and ID conventions`.

| Type | Emoji | Use |
|---|---|---|
| `feat` | ✨ | New capability or service |
| `fix` | 🐛 | Bug fix |
| `docs` | 📝 | Documentation only |
| `refactor` | ♻️ | Restructuring without behavior change |
| `chore` | 🔧 | Tooling, config, maintenance |
| `ci` | 👷 | Workflows and runners |
| `revert` | ⏪ | Revert a commit |

- Scopes are component names, such as `proxmox`, `dns`, `terraform`, `claude`, `adr`.
- One logical change per commit. The body explains why.
- Breaking change: `!` after the type and a `BREAKING CHANGE:` footer.
- Release Please is not configured. When it is, check its configuration before adding types or scopes.

## Pull requests
Title: same format as a commit subject. Body:

```markdown
## 📋 Summary
## 🔧 Changes
## 🏛️ Architecture decisions
ADR links, or "None".
## ✅ Validation
| Check | Result |
|---|---|
## ⚠️ Risks and rollback
## 📌 Follow-ups
```

## Change safety
- Inspect `git status` and `git diff` before modifying or committing.
- Never overwrite, discard, reset or revert user changes without explicit permission.
- If unrelated or untracked changes could be affected, ask the user before committing.
- Review `git diff --cached` before committing.
- Never commit secrets, private keys, tokens, Terraform state, plans or local context files.
- Never commit, push or open a PR without an explicit request. Never force push. Never use `--no-verify`.
