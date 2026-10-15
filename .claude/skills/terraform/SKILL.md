---
name: terraform
description: Terraform conventions for this repo. Layout, HCP Terraform state and workspaces, providers, secrets, validation checklist and safety. Use for any task that reads, writes or runs Terraform.
---

# Terraform

## Layout
```
terraform/
  modules/<module-name>/                 # Reusable logic, no environment-specific values, README required
  environments/homelab/<component>/      # Thin root per component: providers, backend, module calls
```
- Inspect the existing structure and conventions before adding files. Create folders only when the first resource needs them.
- Roots stay thin. Non-secret environment values live in the root `locals`.

## State and HCP Terraform
- Organization `hdti`, project `homelab`.
- One workspace per root, named `homelab-<component>`, such as `homelab-dns`. Small blast radius and fast plans.
- Share values between roots with outputs and the `tfe_outputs` data source.
- Execution mode is **Local**: HCP stores state and locks only, because HCP-hosted runners cannot reach `192.168.2.0/24`.
  Moving to an HCP agent or a self-hosted runner requires an ADR.
- Configure the backend with a `cloud {}` block. Never initialize or change a backend before checking the current
  configuration and explaining the impact to the user.

## Versions and providers
- Use the latest stable Terraform compatible with the providers and HCP. Verify versions online before pinning.
- Pin `required_version` and providers with `~>`. Commit `.terraform.lock.hcl`.
- Prefer official or well-maintained providers: `bpg/proxmox` for Proxmox, `cloudflare/cloudflare` for Cloudflare.
  Evaluate the Technitium provider when DNS work starts.

## Code
- Declarative and idempotent. Prefer native resources and data sources.
  No `local-exec` or `remote-exec` when a native solution exists.
- Explicit variables with type, description and validation where useful. Clear `snake_case` names for resources, variables and outputs.
- No hardcoded environment-specific values in modules.
- No secrets in source. Pass them through environment variables (`TF_VAR_*`, provider variables), GitHub Secrets, and later Vault.
- Mark sensitive variables and outputs `sensitive = true`. This only redacts output: values still land in state.

## Before declaring a change complete
1. `terraform fmt -check -recursive` from the repo root, or `terraform fmt` on modified files.
2. `terraform validate` in each affected, initialized root.
3. `tflint` with the repo configuration.
4. `trivy config` on the affected Terraform directory.
5. Review the diff for unintended changes, hardcoded values, secrets and generated files.
6. Report every check that could not run, and why.

## Safety
- `terraform plan` is allowed. Summarize adds, changes and destroys, and highlight every destroy or replace.
- Never run `apply`, `destroy`, `state rm`, `state mv`, `state push`, `import` or `force-unlock` without explicit authorization.
- Never delete or overwrite state or plan files. Never commit them.

## Documentation
- Each module README documents inputs and outputs: name, type, description, default and validation.
- Keep `docs/` consistent with the actual infrastructure. Never document facts that were not verified.
