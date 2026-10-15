#!/usr/bin/env python3
"""Claude Code PreToolUse hook: block or escalate dangerous shell commands.

Reads the hook input JSON on stdin and inspects `tool_input.command` for the Bash and PowerShell tools.
Prints a `hookSpecificOutput` decision (`deny` or `ask`) when a rule matches; prints nothing otherwise,
which defers to the normal permission rules in `.claude/settings.json`.

This is one safety layer among several (permission rules, this hook, pre-commit, CI). It matches command
text, so it cannot catch everything, for example a script written to disk and executed later.
Standard library only.
"""

from __future__ import annotations

import json
import re
import sys

IGNORE_CASE = re.IGNORECASE

# (pattern, flags, reason). Irreversible or safety-bypassing actions: always denied.
DENY_RULES: list[tuple[str, int, str]] = [
    (r"\b(terraform|tofu)\b.*\b(apply|destroy|force-unlock)\b", IGNORE_CASE,
     "Terraform apply/destroy/force-unlock requires the user to run it or explicitly authorize it."),
    (r"\b(terraform|tofu)\b.*\bstate\s+(rm|push)\b", IGNORE_CASE,
     "Terraform state rm/push edits state irreversibly."),
    (r"\b(terraform|tofu)\b.*\bworkspace\s+delete\b", IGNORE_CASE,
     "Deleting a Terraform workspace destroys its state."),
    (r"\bgit\b.*\bpush\b.*(--force|\s-f(\s|$)|\s\+\S)", 0,
     "Force push rewrites remote history."),
    (r"\bgit\b.*\bcommit\b.*(--no-verify|\s-[a-zA-Z]*n[a-zA-Z]*(\s|$))", 0,
     "Skipping commit hooks (--no-verify / -n) bypasses secret and data checks."),
    (r"core\.hookspath", IGNORE_CASE,
     "Changing core.hooksPath disables the pre-commit checks."),
    (r"\bgit\b.*\breset\b.*--hard\b", 0,
     "git reset --hard discards local changes."),
    (r"\bgit\b(\s+-\S+)*\s+clean\b", 0,
     "git clean deletes untracked files."),
    (r"\bgit\b.*\bbranch\b.*(\s-D\b|--delete\b.*--force\b|--force\b.*--delete\b)", 0,
     "Force-deleting a branch can lose unmerged work."),
    (r"\b(pct|qm)\s+destroy\b", 0,
     "Destroying a Proxmox guest is irreversible."),
    (r"\bpvecm\s+(expected|delnode|add)\b", 0,
     "Cluster quorum and membership changes require explicit authorization (ADR-0004)."),
    (r"\bpvesm\s+remove\b", 0,
     "Removing Proxmox storage requires explicit authorization."),
    (r"\b(lvremove|lvreduce|vgremove|pvremove|wipefs|sgdisk|mkfs(\.\w+)?)\b", 0,
     "Destructive storage operation."),
    (r"\bzfs\s+destroy\b|\bzpool\s+(destroy|labelclear)\b", 0,
     "Destructive ZFS operation."),
    (r"\bdd\b.*\bof=", 0,
     "dd writing to a target can overwrite disks."),
    (r"\bgh\s+repo\s+delete\b", 0,
     "Deleting a GitHub repository is irreversible."),
    (r"\bgh\s+api\b.*(-X|--method)\s*=?\s*DELETE\b", IGNORE_CASE,
     "DELETE calls on the GitHub API require explicit authorization."),
]

# Legitimate after explicit user approval: escalate to the permission dialog.
ASK_RULES: list[tuple[str, int, str]] = [
    (r"\b(terraform|tofu)\b.*\bstate\s+mv\b", IGNORE_CASE,
     "terraform state mv changes resource addresses in state."),
    (r"\b(terraform|tofu)\b.*\bimport\b", IGNORE_CASE,
     "terraform import writes existing resources into state."),
]

GUARDED_TOOLS = {"Bash", "PowerShell"}


SEGMENT_SEPARATORS = re.compile(r"\n|;|&&|\|\|?")


def segments(command: str) -> list[str]:
    """Split a command into simple commands: one per line and per `;`, `&&`, `||` or `|`.

    Line continuations are joined first so `terraform \\<newline> apply` stays one segment.
    Matching per segment avoids false positives on multi-line text such as heredocs or prose,
    while a dangerous command still matches on its own line.
    """
    joined = command.replace("\\\r\n", " ").replace("\\\n", " ")
    parts = (re.sub(r"\s+", " ", part).strip() for part in SEGMENT_SEPARATORS.split(joined))
    return [part for part in parts if part]


def evaluate(command: str) -> tuple[str, str] | None:
    """Return (decision, reason) for a command, or None to defer to normal permissions."""
    for rules, decision in ((DENY_RULES, "deny"), (ASK_RULES, "ask")):
        for segment in segments(command):
            for pattern, flags, reason in rules:
                if re.search(pattern, segment, flags):
                    return decision, reason
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as error:
        print(f"guard_dangerous_commands: invalid hook input: {error}", file=sys.stderr)
        return 2  # Fail closed: block the tool call.

    if payload.get("tool_name") not in GUARDED_TOOLS:
        return 0
    command = (payload.get("tool_input") or {}).get("command") or ""
    result = evaluate(command)
    if result is None:
        return 0

    decision, reason = result
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": f"Blocked by .claude/hooks/guard_dangerous_commands.py: {reason}",
        }
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
