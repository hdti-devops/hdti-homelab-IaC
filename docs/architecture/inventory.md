# Homelab inventory

Facts verified on 2026-10-15 from command output on each node, unless marked **unverified**.
Values are installed capacity, not free capacity. Check live state before any placement decision.

## Proxmox cluster

| Field | Value |
|---|---|
| Cluster name | `hdti-homelab` |
| Nodes | 2 (`pve`, `pve2`), one vote each, quorum = 2 |
| Quorum device | None, accepted risk ([ADR-0004](../adr/0004-two-node-cluster-without-quorum-device.md)) |
| Shared storage | None |

## Nodes

| Field | `pve` | `pve2` |
|---|---|---|
| IP | `192.168.2.200` | `192.168.2.201` |
| Proxmox VE | 9.2.21, kernel 7.0.14-19-pve | 9.2.21, kernel 7.0.14-20-pve |
| CPU | AMD Ryzen 7 5800H, 8C/16T | Intel Core i7-6700T, 4C/8T, QuickSync HD 530 |
| RAM installed | 32 GB | 8 GB |
| RAM visible to the OS | 28 GiB | 7.5 GiB |
| Disk | 1 TB NVMe SSD, Crucial P3 Plus | 1 TB HDD, 7200 rpm, HGST Travelstar |
| Storage `local` (dir) | 93.9 GiB | 93.9 GiB |
| Storage `local-lvm` (LVM-thin) | 793.8 GiB | 794.8 GiB |
| Network | `nic0` bridged on `vmbr0`, Wi-Fi unused | `nic0` bridged on `vmbr0`, Wi-Fi unused |
| Preferred workloads | Kubernetes VMs, high-RAM, I/O-heavy | Lightweight infrastructure LXCs |

Both storages share the single disk of each node.
Kernels differ: `pve` has only 7.0.14-19 installed, so it has not received the 7.0.14-20 update yet.

## Network

| Field | Value |
|---|---|
| ISP | Virgin, 1 Gbps, ISP modem |
| LAN | `192.168.2.0/24` |
| Gateway | `192.168.2.1` |
| Upstream DNS | `1.1.1.1` |
| Homelab static pool | `192.168.2.200-254`, excluded from the modem DHCP range |
| Public IP | Dynamic (**unverified**). Never recorded here: the repository is public |
| Modem bridge mode | **Unverified**, probably not bridged |
| Domain | `hdti.ca`, DNS on Cloudflare |

## IP allocation

| IP | Hostname | Purpose |
|---|---|---|
| `192.168.2.1` | | Gateway, ISP modem |
| `192.168.2.200` | `pve` | Proxmox node |
| `192.168.2.201` | `pve2` | Proxmox node |
| `192.168.2.202-254` | | Free |

## Guests

VMID ranges and naming follow [ADR-0003](../adr/0003-naming-and-id-conventions.md).

| VMID | Hostname | Node | Type | IP | Resources | Runbook |
|---|---|---|---|---|---|---|
| | | | | | | No guests yet |
