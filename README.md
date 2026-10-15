# hdti-homelab-IaC

Infrastructure as code, architecture decisions and runbooks for the **hdti** homelab.
Everything that exists in the homelab is described, decided or automated here.

## Homelab at a glance

| Component | Summary |
|---|---|
| Hypervisors | 2 Proxmox VE nodes, `pve` and `pve2`, in the cluster `hdti-homelab` |
| Network | `192.168.2.0/24`, static pool `192.168.2.200-254` reserved for the homelab |
| Domain | `hdti.ca` on Cloudflare |

Details are in [docs/architecture/inventory.md](docs/architecture/inventory.md).
Planned services and their status are in [docs/roadmap.md](docs/roadmap.md).

## Repository layout

| Path | Purpose |
|---|---|
| [CLAUDE.md](CLAUDE.md) | Global instructions for Claude Code |
| [.claude/](.claude/) | Claude Code skills, commands, agent, permissions and safety hook |
| [.github/workflows/](.github/workflows/) | CI: repository checks on every PR and push to `main` |
| [docs/adr/](docs/adr/) | Architecture Decision Records |
| [docs/runbooks/](docs/runbooks/) | Reproducible procedures for every installed service |
| [docs/architecture/](docs/architecture/) | Inventory and architecture reference |

Folders such as `terraform/` and `packer/` are added when the first resource needs them.

## Working with Claude Code

| Command | When |
|---|---|
| `/pr` | A task is done: review docs and ADRs, validate, then commit, push and open a PR after approval |
| `/apply-review <review>` | A PR was reviewed: verify each point, plan the fixes and apply them to the same PR |
| `/retro` | A session is done: write a local handoff and get the prompt to resume next time |
| `/support <error>` | Something is broken: investigate, find the root cause, propose a fix and document it |
| `/community-scripts <app>` | Install a service with a community script, with a runbook as output |

Each working session maps to one branch and one pull request:
`/pr` -> external review -> `/apply-review` -> merge -> `/retro`.

## Safety layers

| Layer | Where | What it stops |
|---|---|---|
| Permission rules | [.claude/settings.json](.claude/settings.json) | Known destructive commands; asks before commit, push, PR, ssh. Bypass mode is disabled |
| Command guard hook | [.claude/hooks/](.claude/hooks/) | Parses each command: catches wrapped and nested commands, short flags, absolute paths. Blocks when no Python works |
| pre-commit | [.pre-commit-config.yaml](.pre-commit-config.yaml) | Secrets in staged changes, MAC addresses, public IPv4, MAC-derived IPv6 |
| CI | [.github/workflows/](.github/workflows/) | Hook tests and pre-commit on every PR, plus a full-history secret scan |

Serial numbers cannot be detected automatically: review diffs for them.
A four-part version number such as `7.0.14.20` looks like a public IPv4: add `allow-public-ip` on that line,
for example as an HTML comment in Markdown.

## Terraform execution model

Terraform runs **locally**. HCP Terraform (organization `hdti`, project `homelab`) stores state and handles locking only,
because HCP-hosted runners cannot reach the homelab LAN. Each component has its own root and workspace.
See [.claude/skills/terraform/SKILL.md](.claude/skills/terraform/SKILL.md).

## Local setup

Requirements on each machine that works on this repository:

| Tool | Why |
|---|---|
| Python 3.8+ as `python3`, `python` or `py` | Runs the command guard hook and pre-commit |
| `sh` (Git Bash on Windows) | Runs the hook launcher |
| Claude Code 2.1.295+ | `onFailure: block` also blocks when the launcher itself fails |
| pre-commit | Local secret and public-data checks |

Install the git hooks once per clone:

```bash
pip install pre-commit
pre-commit install
```

On Windows, if `pre-commit` is not on `PATH`, use `python -m pre_commit install` and `python -m pre_commit run --all-files`.

## Conventions

- Branches, commits and PRs: [git conventions](.claude/skills/git-conventions/SKILL.md)
- Decisions: [ADR process](.claude/skills/adr/SKILL.md)
- Procedures: [runbook process](.claude/skills/runbook/SKILL.md)
