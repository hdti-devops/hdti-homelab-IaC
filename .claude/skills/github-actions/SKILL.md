---
name: github-actions
description: GitHub Actions conventions for this public repo. Workflow structure, action pinning, permissions, validation checks, repository variables and secrets, and self-hosted runner security. Use for any task that creates or changes workflows or runners.
---

# GitHub Actions

## Structure
- Workflows live in `.github/workflows/` with lowercase kebab-case names, such as `terraform-ci.yml`.
- Separate validation workflows (pull requests) from deployment workflows.
- Pin third-party actions to a full commit SHA, with the release version in a comment: `uses: org/action@<sha> # v1.2.3`.
  Resolve the SHA from the release tag; never copy it from an untrusted source.
- Set explicit, minimal `permissions` at workflow level, such as `contents: read`, and widen per job only when needed.
- Every step has a `name` starting with an emoji, such as `🧹 Terraform fmt` or `🔍 Trivy scan`.
- Reuse with reusable workflows or composite actions once duplication appears.

## Variables and secrets
- When a value is reused across workflows or is a changeable source of truth, such as `TF_VERSION` or `PYTHON_VERSION`,
  suggest a repository variable (`vars.NAME`) to the user. Give the exact name and value.
- Do the same for secrets (`secrets.NAME`). Non-secret endpoints, such as `VAULT_URL`, are variables.
- Never assume a variable or secret exists: ask the user to confirm it was created.
- Never hardcode secrets, tokens, passwords, private keys or credentials. Prefer OIDC where supported.

## Validation checks in pull requests
Include what applies: Terraform fmt and validate, TFLint, Trivy config, Gitleaks, workflow linting (actionlint),
and any repository policy checks. Scope checks with path filters without weakening required security gates.
Never report a check as successful unless it ran and passed.

## Self-hosted runners (public repository)
- Standard labels: `self-hosted`, `homelab`, `proxmox`, `linux`. Jobs needing the LAN use `runs-on: [self-hosted, homelab]`.
- Self-hosted jobs never run code from forks. Trigger them only on `push` to `main`, `workflow_dispatch`,
  or `pull_request` guarded by `if: github.event.pull_request.head.repo.full_name == github.repository`.
- Never use `pull_request_target` together with a checkout of pull request code.
- Ask the user to enable "Require approval for all outside collaborators" for fork pull request workflows.
- Validation that does not need the LAN runs on GitHub-hosted runners.
- Runners run in a dedicated unprivileged LXC under a non-root user, with least-privilege tokens per consumer.
- Verify runner labels and availability before changing `runs-on`. Document runners in the inventory.
- Deployment and destructive jobs require explicit authorization through protected GitHub environments and branch protection.
