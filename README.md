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
| [.claude/](.claude/) | Claude Code skills, commands, agent and permissions |
| [docs/adr/](docs/adr/) | Architecture Decision Records |
| [docs/runbooks/](docs/runbooks/) | Reproducible procedures for every installed service |
| [docs/architecture/](docs/architecture/) | Inventory and architecture reference |

Folders such as `terraform/`, `packer/` and `.github/workflows/` are added when the first resource needs them.

## Working with Claude Code

| Command | When |
|---|---|
| `/pr` | A task is done: review docs and ADRs, validate, then commit, push and open a PR after approval |
| `/retro` | A session is done: write a local handoff and get the prompt to resume next time |
| `/support <error>` | Something is broken: investigate, find the root cause, propose a fix and document it |

Each working session maps to one branch and one pull request.

## Terraform execution model

Terraform runs **locally**. HCP Terraform (organization `hdti`, project `homelab`) stores state and handles locking only,
because HCP-hosted runners cannot reach the homelab LAN. Each component has its own root and workspace.
See [.claude/skills/terraform/SKILL.md](.claude/skills/terraform/SKILL.md).

## Local setup

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
