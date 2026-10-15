---
name: support
description: Troubleshoot a problem in the homelab (error message, failing LXC, VM, service, workflow or Proxmox host). Investigates with evidence, finds the root cause, proposes a fix and documents it. Use when the user runs /support or pastes an error and asks what is wrong.
argument-hint: "<error message or symptom>"
---

# /support

## Steps
1. **Frame.** Restate the symptom. Identify component, node, VMID and hostname from `docs/architecture/inventory.md`.
2. **Known issues.** Read the component runbook, especially its Troubleshooting section, and the related ADRs.
3. **Evidence.** Prefer read-only commands. Give the user one small batch at a time, most discriminating first,
   and state where to run each one: node shell, inside a guest with `pct exec <vmid> -- <cmd>`, or the guest console.
   Typical commands: `systemctl status <unit>`, `journalctl -u <unit> -n 100 --no-pager`, `pct status <vmid>`,
   `pct config <vmid>`, `qm config <vmid>`, `df -h`, `free -h`, `dmesg -T | tail -50`, `ss -tlnp`,
   `dig @<dns> <name>`, `openssl s_client -connect <host>:443 -servername <name>`.
4. **Root cause.** State the cause, the evidence that supports it and your confidence.
   Never guess: if the evidence is not conclusive, run another batch.
5. **Fix.** Propose the minimal fix with its risks and rollback. Apply it only after explicit approval.
   Disruptive or destructive actions follow the safety rules in `CLAUDE.md`. Verify the fix with the user afterwards.
6. **Document.** Add an entry to the Troubleshooting section of the component runbook: symptom, cause, fix, prevention.
   If the cause shows an architecture assumption was wrong, propose an ADR update (`adr` skill).
   These documentation changes go into the current branch and PR.
