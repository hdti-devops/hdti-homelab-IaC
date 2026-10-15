# hdti-homelab-IaC

Single source of truth for the hdti homelab: infrastructure as code, architecture decisions (ADRs) and runbooks.
Two Proxmox VE nodes (`pve`, `pve2`), LAN `192.168.2.0/24`, domain `hdti.ca` on Cloudflare.
The repository is **public**: never commit public IPs, MAC addresses, serial numbers or secrets.

## Communication
- Always reply to the user in French.
- Write code, identifiers, filenames, comments, docs, commits and PRs in English.
- Use explicit, descriptive names for files, variables and resources.

## Working rules
- When anything is ambiguous, ask before planning. Never assume; ask.
- Present a plan and wait for explicit approval before writing code or changing files.
- One working session = one branch = one pull request.
- Decision first: a new or superseding ADR is delivered and merged in its own `adr/<name>` PR before any implementation
  branch starts. Decision and implementation are two sessions. Details in the `adr` skill.
- Create only what the current task needs: no speculative files or folders. Keep `docs/roadmap.md` in mind so the result stays modular and easy to extend.
- Make the minimal change. Never overwrite or remove previous work without explicit permission; explain why when it is required.
- Never invent infrastructure facts. Verify them against the repo or live systems, or give the user read-only commands to run and ask for the output.
- Keep documentation rigorous, concise and in sync with reality.
- Architecture analysis and decisions use the most capable model available.

## Safety (hard rules)
Never do any of the following without explicit authorization in the current session:
`terraform apply` / `destroy` / state edits, VM/LXC/disk deletion, destructive storage operations,
management network or corosync changes, disruptive firewall changes, commits, pushes, PR creation.
Never use `root@pam` for automation or API integrations.
Never commit secrets, Terraform state or plans, or local context files.
Permission rules in `.claude/settings.json`, the hook `.claude/hooks/guard_dangerous_commands.py`, pre-commit
and CI enforce part of this. The rules apply even where they do not.
When the hook blocks a real command, stop and ask the user; never rephrase the command to get past it.
When it blocks a file edit whose text only quotes such a command, use the file editing tools instead of the shell.

## Where things live
| Path | Content |
|---|---|
| `docs/architecture/inventory.md` | Hosts, network, IP and VMID allocation |
| `docs/roadmap.md` | Phases and status |
| `docs/adr/` | Architecture Decision Records |
| `docs/runbooks/` | One runbook per installed service |
| `.claude/skills/` | Domain conventions, loaded on demand |
| `.claude/session-notes/` | Local session handoffs (git-ignored) |

## Commands
Session cycle: `/pr` -> external review -> `/apply-review` -> merge -> `/retro`.
- `/pr` when a task is done: docs and ADR review, validation, then commit, push and PR after approval.
- `/apply-review <review>` to verify a review of the open PR, plan the fixes and apply them after approval.
- `/retro` at the end of a session: local handoff note and the prompt for the next session.
- `/support <error>` to troubleshoot, find the root cause, propose a fix and document it.
- `/community-scripts <app>` to install a service with a community script. It also triggers automatically.
