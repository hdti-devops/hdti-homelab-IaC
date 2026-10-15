---
name: runbook
description: Write and maintain runbooks in docs/runbooks/, one per installed service, detailed enough to reinstall it identically. Use after any install, upgrade, reconfiguration or troubleshooting of a service.
---

# Runbooks

## Rules
- One file per service: `docs/runbooks/<product>.md`, such as `technitium-dns.md`. Start from [template.md](template.md).
- Record what was actually done, not what should have been done. Keep installer prompts and answers verbatim.
- Record versions: community script commit SHA, application version, OS template.
- Never write secrets. Write where they are stored, such as "admin password: password manager entry `homelab/technitium`".
- No public IPs, MAC addresses or serial numbers: the repository is public.
- Every later change to the service adds a row to the Change log, with the PR.
- Add the runbook to the index in `docs/runbooks/README.md`.
