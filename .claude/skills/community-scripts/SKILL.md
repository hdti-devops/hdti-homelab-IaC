---
name: community-scripts
description: Guided installation of an LXC or VM with the Proxmox VE Helper-Scripts from community-scripts.org. Covers resource sizing review, the advanced install walkthrough one prompt at a time, post-install checks and the runbook. Use whenever a service will be installed with a community script.
argument-hint: "<app name or community-scripts.org URL>"
---

# Community scripts installs

Reply to the user in French.

## Rules
- Only use scripts from https://community-scripts.org/, whose source is https://github.com/community-scripts/ProxmoxVE. Never use mirrors or forks.
- Always use the **Advanced** install mode.
- Never assume an answer. Installer prompts change over time: the user pastes each prompt, you answer that prompt only.
- Never store secrets shown by the installer in the repo. Record where the user stored them.

## Steps
1. **Research.** Read the script page and the sources `ct/<app>.sh` and `install/<app>-install.sh`.
   Record the exact install command, default resources (CPU, RAM, disk), OS template and version,
   default privilege mode, ports, post-install notes and the update method.
   Record the commit SHA of `main` used for the install:
   `git ls-remote https://github.com/community-scripts/ProxmoxVE.git refs/heads/main`.
2. **Placement.** Follow the `proxmox` skill: live capacity check, node choice, VMID and hostname (ADR-0003),
   and a free IP from `docs/architecture/inventory.md`.
3. **Sizing.** Show a table of default versus recommended CPU, RAM and disk, with a verdict for each:
   keep, lower or raise, and why. Consider the workload, the node's live free capacity, and that `pve2` uses an HDD.
4. **Approval.** Present node, VMID, hostname, IP, gateway, DNS, resources, unprivileged mode and LXC features.
   Wait for explicit approval.
5. **Walkthrough.** Give the command to run in the target node shell, usually:
   `bash -c "$(curl -fsSL https://raw.githubusercontent.com/community-scripts/ProxmoxVE/main/ct/<app>.sh)"`.
   Tell the user to choose Advanced. For each prompt they paste, give the exact value and a one-line reason.
   Keep a running log of prompt, answer and reason for the runbook.
6. **Result.** The user pastes the final success output. Extract the URL, app version and credential hints.
7. **Verification.** Give read-only checks: service status, listening ports, web UI reachability, DNS resolution if relevant.
   Record the results.
8. **Documentation.** Write the runbook (`runbook` skill), update `docs/architecture/inventory.md` and `docs/roadmap.md`.
   If a choice had real alternatives, such as the tool itself or LXC versus VM, write an ADR (`adr` skill).
