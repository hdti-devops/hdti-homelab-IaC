# Roadmap

Target vision of the homelab. Order, placement and tools are confirmed through ADRs when each phase starts.
Status values: Planned, In progress, Done.

## Phase 0: foundation

| Item | Status | Notes |
|---|---|---|
| Repository structure, Claude Code tooling, ADR and runbook process | Done | ADR-0001, ADR-0002 |
| Naming and ID conventions | Done | ADR-0003 |
| Safety enforcement (command guard hook, public-data checks) and CI | Done | ADR-0002 revision |

## Phase 1: core network

| Item | Planned method | Status | Notes |
|---|---|---|---|
| Technitium DNS | [Community script](https://community-scripts.org/scripts/technitiumdns), zones via Terraform | Planned | |
| Caddy reverse proxy | [Community script](https://community-scripts.org/scripts/caddy) | Planned | Certificates valid on the LAN and externally, likely DNS-01 through Cloudflare |
| Cloudflare DDNS | [Community script](https://community-scripts.org/scripts/cloudflare-ddns) | Planned | Public IP is dynamic |
| WireGuard | [Community script](https://community-scripts.org/scripts/wireguard) | Planned | Only external entry point |

## Phase 2: platform and operations

| Item | Planned method | Status | Notes |
|---|---|---|---|
| Pulse monitoring | [Community script](https://community-scripts.org/scripts/pulse) | Planned | |
| LibreSpeed | [Community script](https://community-scripts.org/scripts/librespeed-rust) | Planned | |
| GitHub self-hosted runner | [Community script](https://community-scripts.org/scripts/github-runner) | Planned | First use: Caddy configuration updates |
| HashiCorp Vault | LXC or VM, to decide | Planned | Secrets management |

## Phase 3: compute

| Item | Planned method | Status | Notes |
|---|---|---|---|
| Golden images | Packer | Planned | |
| Kubernetes cluster | 3 VMs: 1 control plane, 2 workers | Planned | |

## Phase 4: applications

| Item | Planned method | Status | Notes |
|---|---|---|---|
| Jellyfin, Sonarr, Prowlarr | LXC or VM, to decide | Planned | |

## Open topics

- Quorum device or third node: postponed ([ADR-0004](adr/0004-two-node-cluster-without-quorum-device.md)).
- Backup strategy for guests and configuration: not decided yet.
- Align `pve` with `pve2` on package updates (kernel 7.0.14-20).
- DNS redundancy: a secondary Technitium on the other node, decided in the Technitium ADR.
- Terraform execution through an HCP agent or the self-hosted runner instead of local execution.
