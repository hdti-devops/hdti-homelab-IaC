---
name: packer
description: Packer conventions for building Proxmox golden images (VM templates). Use for any task involving Packer templates or image builds.
---

# Packer

Not started yet. Distributions, layout details and build cadence are decided with the user when the first image is built,
and recorded in an ADR. Verify current best practices and plugin versions online at that time.

## Baseline
- HCL2 only, one folder per image under `packer/<image-name>/`. Pin `required_plugins`, starting with the Proxmox plugin.
- Builder `proxmox-iso` with an unattended install file committed to the repo.
- Images are cloud-init ready, include the QEMU guest agent and are fully patched at build time.
- Clean up at the end of the build: SSH host keys, `machine-id`, cloud-init state, logs.
- No secrets in templates: use `PKR_VAR_*` environment variables and mark variables `sensitive = true`.
- Use a dedicated `packer@pve` token with a least-privilege role (`proxmox` skill).
- Template VMIDs in `9000-9099`, named `tpl-<os>-<version>`. Write OS version, build date and git commit in the template description.
- Before declaring done: `packer fmt -check`, `packer init` and `packer validate`. Report checks that could not run.
- Write a runbook for building and updating each image.
