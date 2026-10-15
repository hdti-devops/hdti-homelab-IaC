---
name: proxmox
description: Proxmox VE conventions for the hdti homelab. Node placement, LXC versus VM, resource sizing, VMID and hostname rules, API access and safety. Use for any task that creates, changes or inspects Proxmox guests, storage, network, users or permissions.
---

# Proxmox VE

## Before any change
- Read `docs/architecture/inventory.md`. Its values are installed capacity, not free capacity.
- Check live state before placement or sizing. Ask the user to run, or run read-only:
  `pvesh get /cluster/resources --output-format json-pretty`, `pvesh get /nodes/<node>/status`, `pvesm status`.
- When Terraform manages the resource, run `terraform plan` and inspect the state first (`terraform` skill).
- Make the minimal change. Never overwrite or remove existing configuration without explicit permission.
- Use `bpg/proxmox` through Terraform when the provider supports the resource and it adds value.

## Node placement
| Node | Prefer for | Constraints |
|---|---|---|
| `pve` | Kubernetes VMs, high-RAM and resource-intensive workloads, I/O-heavy workloads | NVMe SSD |
| `pve2` | Lightweight infrastructure LXCs: DNS, reverse proxy, Cloudflare DDNS, GitHub runner, WireGuard | 7200 rpm HDD: avoid I/O-heavy guests. Intel QuickSync (HD 530) available |

## Cluster
Two-node cluster without a quorum device (ADR-0004). When one node is down, the other loses quorum:
running guests keep running, but starting guests and configuration changes fail.
Never run `pvecm expected 1` or change corosync without explicit authorization.
No shared storage and no HA: never assume live migration. The nodes have different CPU vendors (AMD and Intel).

## LXC versus VM
- Default to **unprivileged LXC** for isolated, single-purpose services.
- Privileged LXC only when technically required. Document the reason in the runbook or an ADR.
- Avoid host bind mounts, device passthrough and extra features (nesting, keyctl, FUSE) unless required. Document why.
- Use a **VM** for stronger isolation, a full OS, custom kernel modules, Kubernetes nodes or untrusted workloads.
- VMs: enable the QEMU guest agent, use VirtIO SCSI single, enable `discard` on thin storage.
  Use CPU type `host` unless the VM must move between nodes, then use `x86-64-v2-AES`.
- Define CPU, memory, disk, network and startup settings declaratively. Set `onboot` and a startup order for dependencies.

## Naming and IDs (ADR-0003)
| VMID range | Role |
|---|---|
| 100-199 | Core network: DNS, reverse proxy, VPN, DDNS |
| 200-299 | Platform and operations: secrets, runners, monitoring, speed tests |
| 300-399 | Kubernetes nodes |
| 400-499 | Applications and media |
| 9000-9099 | Templates |

- Hostname: `<role>-<nn>`, lowercase, by role and not by product. Examples: `dns-01`, `proxy-01`, `vpn-01`, `k8s-cp-01`, `k8s-worker-01`.
- Tags: product name, plus `community-script` or `terraform` for the provisioning method.
- Record every guest in the inventory: VMID, hostname, node, IP, type, resources.

## API access
- Never use `root@pam` for automation or API integrations.
- One user per consumer in the `pve` realm, such as `terraform@pve`, `packer@pve` or `pulse@pve`.
- One API token per consumer with privilege separation, and a custom least-privilege role on the token,
  such as `TerraformProvisioner`, granted on the narrowest path possible.
- Check the required privileges against the current Proxmox and provider documentation at creation time.
- Token secrets never go in the repo. Store them in GitHub Secrets or a local environment variable until Vault exists.
- Document each consumer user, token, role and ACL path in the inventory.

## Requires explicit authorization
Guest or disk deletion, destructive storage operations, changes to `vmbr0`, the management network or corosync,
disruptive firewall changes and cluster membership changes.
