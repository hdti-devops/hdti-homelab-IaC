# ADR-0003: Naming and ID conventions for Proxmox guests

- **Status:** Accepted
- **Date:** 2026-10-15
- **Deciders:** Repository owner

## Context and problem statement

Guests will be created on two nodes by community scripts, Terraform and Packer.
VMIDs, hostnames and tags need a convention before the first guest exists, so that the inventory stays readable
and guests can move between nodes or change product without renaming.

## Decision drivers

- A VMID or hostname should reveal the guest's role at a glance.
- Moving a guest to the other node must not require a new identifier.
- Replacing a product, such as another DNS server, should not force a hostname change.
- Room to grow, including Kubernetes nodes and templates.

## Considered options

1. VMID ranges by role, role-based hostnames.
2. VMID equal to the last octet of the guest IP.
3. VMID ranges by node.

## Decision outcome

Chosen option: **VMID ranges by role, role-based hostnames**.

| VMID range | Role |
|---|---|
| 100-199 | Core network: DNS, reverse proxy, VPN, DDNS |
| 200-299 | Platform and operations: secrets, runners, monitoring, speed tests |
| 300-399 | Kubernetes nodes |
| 400-499 | Applications and media |
| 9000-9099 | Templates |

- Hostname: `<role>-<nn>`, lowercase. Examples: `dns-01`, `proxy-01`, `vpn-01`, `k8s-cp-01`, `k8s-worker-01`.
- Tags: product name, plus the provisioning method (`community-script` or `terraform`).
- Templates: `tpl-<os>-<version>`.

### Consequences

- Good: role is visible from the VMID and hostname, and node placement can change freely.
- Good: 100 IDs per role is far more than the static IP pool allows.
- Bad: the VMID does not reveal the IP, so the inventory is the lookup table.

### Confirmation

The `proxmox` and `community-scripts` skills apply this convention, and `/pr` checks the inventory.

## Pros and cons of the options

### VMID ranges by role

- Good, because role is readable and independent of node and IP.
- Bad, because the IP must be looked up in the inventory.

### VMID equal to the IP last octet

- Good, because the VMID gives the IP directly.
- Bad, because only 53 IDs exist (`.202-.254`), and changing an IP forces a new VMID.

### VMID ranges by node

- Good, because the node is visible.
- Bad, because a migration forces a new VMID, which breaks references.

## More information

- [Inventory](../architecture/inventory.md)

## Revision history

| Date | Change | Reason |
|---|---|---|
| 2026-10-15 | Created | |
