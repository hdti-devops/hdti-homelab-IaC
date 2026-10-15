# ADR-0004: Two-node cluster without a quorum device

- **Status:** Accepted
- **Date:** 2026-10-15
- **Deciders:** Repository owner

## Context and problem statement

`pve` and `pve2` were joined into the Proxmox cluster `hdti-homelab` to manage both from one interface.
Corosync gives each node one vote and requires 2 votes for quorum.
When one node is down, the other loses quorum: running guests keep running, but starting guests
and changing configuration fail until quorum returns. There is no shared storage and no HA.

## Decision drivers

- Single management interface for both nodes.
- No extra hardware for now.
- Keep the setup simple at the start.

## Considered options

1. Keep the two-node cluster without a quorum device and accept the risk.
2. Add a QDevice on a third, lightweight device.
3. Split into two standalone nodes.
4. Add a third Proxmox node.

## Decision outcome

Chosen option: **keep the two-node cluster without a quorum device**, because it keeps the single management view
with no extra hardware, and HA is not needed yet.

### Consequences

- Good: one interface, shared users, roles and API tokens across both nodes.
- Bad: an outage or reboot of one node blocks guest starts and configuration changes on the other.
- Bad: no HA. Critical services such as DNS should not depend on both nodes being up.

### Confirmation

`pvecm status` shows the expected votes. The `proxmox` skill forbids `pvecm expected 1` without explicit authorization.

## Pros and cons of the options

### Keep two nodes without a QDevice

- Good, because there is no cost and no change.
- Bad, because each node depends on the other for quorum.

### Add a QDevice

- Good, because either node keeps quorum alone.
- Bad, because it needs a third always-on device.

### Two standalone nodes

- Good, because each node is fully independent.
- Bad, because there are two interfaces, separate users and tokens, and leaving a cluster is a delicate operation.

### Third node

- Good, because it gives real quorum and allows HA later.
- Bad, because it costs hardware and power.

## More information

Revisit when HA is needed, when Kubernetes or critical services span both nodes, or after outages caused by lost quorum.

## Revision history

| Date | Change | Reason |
|---|---|---|
| 2026-10-15 | Created | |
