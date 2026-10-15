#!/usr/bin/env python3
"""Claude Code PreToolUse hook: deny or escalate dangerous shell commands.

Reads the hook input JSON on stdin and inspects `tool_input.command` for the Bash and PowerShell tools.
Prints a `hookSpecificOutput` decision (`deny` or `ask`) when a rule matches; prints nothing otherwise,
which defers to the permission rules in `.claude/settings.json`.

Commands are parsed, not grepped: each line and chained command (`;`, `&&`, `||`, `|`, `&`) is split into
arguments, wrappers (`sudo`, `env`, `timeout`, ...) are skipped, and nested commands are unwrapped
(`sh -c`, `pwsh -Command`, `eval`, `ssh host cmd`, `$(...)`, backticks, `find -exec`).
Options are read the way each tool reads them, so `git push -fu` is a force push while
`gh pr create --title "terraform destroy"` is only a PR title.

Limits: a script written to disk and executed later is not inspected. Standard library only, Python 3.8+.
Launched through `run_guard.sh`, which blocks the command when no Python interpreter works.
"""

from __future__ import annotations

import base64
import binascii
import json
import re
import shlex
import sys
from typing import Callable, Dict, List, Optional, Tuple

DENY = "deny"
ASK = "ask"
Decision = Tuple[str, str]  # (decision, reason)
MAX_DEPTH = 5

# Tokens to skip before the real program, and the options of each wrapper that take a value.
WRAPPER_VALUE_OPTIONS: Dict[str, set] = {
    "sudo": {"-u", "-g", "-h", "-p", "-C", "-D", "-r", "-t", "-U"},
    "doas": {"-u", "-C"},
    "env": {"-u", "-C", "-S"},
    "nice": {"-n"},
    "ionice": {"-c", "-n", "-p"},
    "xargs": {"-n", "-I", "-d", "-L", "-P", "-s", "-E", "-a"},
    "stdbuf": {"-i", "-o", "-e"},
    "command": set(), "exec": set(), "nohup": set(), "time": set(), "builtin": set(),
    "timeout": {"-s", "-k"},
}
SHELL_KEYWORDS = {"if", "then", "else", "elif", "while", "until", "do", "!", "{", "(", "time"}
SHELLS = {"sh", "bash", "zsh", "dash", "ksh", "ash"}
POWERSHELLS = {"pwsh", "powershell"}


def program_name(token: str) -> str:
    """Return the bare, lowercase program name: no directory and no Windows extension."""
    name = re.split(r"[\\/]", token)[-1].lower()
    return re.sub(r"\.(exe|cmd|bat|ps1)$", "", name)


def split_segments(text: str) -> List[str]:
    """Split text into simple commands on newlines and on unquoted `;`, `&&`, `||`, `|`, `&`.

    Newlines always split, even inside quotes, so every line of a heredoc is inspected on its own.
    """
    segments: List[str] = []
    for line in text.replace("\\\r\n", " ").replace("\\\n", " ").splitlines():
        current, quote, escaped = [], None, False
        for char in line:
            if escaped:  # `\;` and similar stay literal outside quotes.
                current.append(char)
                escaped = False
            elif char == "\\" and not quote:
                current.append(char)
                escaped = True
            elif quote:
                current.append(char)
                if char == quote:
                    quote = None
            elif char in "'\"":
                quote = char
                current.append(char)
            elif char in ";&|":
                segments.append("".join(current))
                current = []
            else:
                current.append(char)
        segments.append("".join(current))
    return [segment.strip() for segment in segments if segment.strip()]


def tokenize(segment: str) -> List[str]:
    """Split a segment into arguments. Backslashes are kept so Windows paths survive."""
    lexer = shlex.shlex(segment, posix=True)
    lexer.whitespace_split = True
    lexer.escape = ""
    lexer.commenters = ""
    try:
        return list(lexer)
    except ValueError:  # Unbalanced quotes: fall back to a plain split without quote characters.
        return [token.strip("'\"") for token in segment.split()]


def strip_wrappers(argv: List[str]) -> List[str]:
    """Drop variable assignments, shell keywords and wrappers in front of the real program."""
    index = 0
    while index < len(argv):
        token = argv[index]
        name = program_name(token)
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", token) or token in SHELL_KEYWORDS or token == "&":
            index += 1
        elif name in WRAPPER_VALUE_OPTIONS:
            value_options = WRAPPER_VALUE_OPTIONS[name]
            index += 1
            while index < len(argv) and (argv[index].startswith("-") or re.match(r"^[A-Za-z_]\w*=", argv[index])):
                index += 2 if argv[index] in value_options else 1
            if name == "timeout" and index < len(argv):
                index += 1  # Duration.
        else:
            break
    return argv[index:]


def short_flags(token: str) -> str:
    """Letters of a short option cluster such as `-fu`, or an empty string."""
    return token[1:] if re.match(r"^-[A-Za-z]+$", token) else ""


def positional(args: List[str], value_options: set = frozenset()) -> List[str]:
    """Non-option arguments, skipping the values of options that take one."""
    result, index = [], 0
    while index < len(args):
        token = args[index]
        if token == "--":
            result.extend(args[index + 1:])
            break
        if token in value_options:
            index += 2
            continue
        if not token.startswith("-"):
            result.append(token)
        index += 1
    return result


# --- Per-program rules -------------------------------------------------------------------------------

def check_terraform(args: List[str]) -> Optional[Decision]:
    words = positional(args)
    sub = words[0] if words else ""
    nxt = words[1] if len(words) > 1 else ""
    if sub in {"apply", "destroy", "force-unlock"}:
        return DENY, f"terraform {sub} requires the user to run it or explicitly authorize it."
    if sub == "state" and nxt in {"rm", "push"}:
        return DENY, f"terraform state {nxt} edits state irreversibly."
    if sub == "workspace" and nxt == "delete":
        return DENY, "Deleting a Terraform workspace destroys its state."
    if sub == "state" and nxt in {"mv", "replace-provider"}:
        return ASK, f"terraform state {nxt} changes resource addresses in state."
    if sub in {"import", "taint", "untaint"}:
        return ASK, f"terraform {sub} changes state."
    return None


GIT_GLOBAL_VALUE_OPTIONS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env", "--exec-path"}
GIT_COMMIT_VALUE_OPTIONS = {"-m", "-F", "-C", "-c", "-t", "--message", "--file", "--author", "--date", "--template",
                            "--reuse-message", "--reedit-message", "--fixup", "--squash", "--trailer", "--cleanup"}
GIT_PUSH_VALUE_OPTIONS = {"-o", "--push-option", "--repo", "--receive-pack", "--exec"}


def check_git(args: List[str]) -> Optional[Decision]:
    index = 0
    while index < len(args) and args[index].startswith("-"):
        token = args[index]
        if token == "-c" and index + 1 < len(args) and "core.hookspath" in args[index + 1].lower():
            return DENY, "Changing core.hooksPath disables the pre-commit checks."
        index += 2 if token in GIT_GLOBAL_VALUE_OPTIONS else 1
    if index >= len(args):
        return None
    sub, rest = args[index], args[index + 1:]

    if sub == "config" and any("core.hookspath" in token.lower() for token in rest) \
            and not {"--get", "--list", "-l"} & set(rest):
        return DENY, "Changing core.hooksPath disables the pre-commit checks."
    if sub == "push":
        for token in rest:
            if token in {"--force", "--delete", "--mirror", "--prune", "--no-verify"} or token.startswith("--force-with-lease"):
                return DENY, f"git push {token} rewrites or deletes remote history, or skips hooks."
            if {"f", "d"} & set(short_flags(token)):
                return DENY, f"git push {token} force-pushes or deletes a remote branch."
        for refspec in positional(rest, GIT_PUSH_VALUE_OPTIONS):
            if refspec.startswith(("+", ":")):
                return DENY, f"Refspec {refspec} force-pushes or deletes a remote branch."
    if sub == "commit":
        index = 0
        while index < len(rest):
            token = rest[index]
            if token == "--":
                break
            if token in GIT_COMMIT_VALUE_OPTIONS:
                index += 2
                continue
            if token == "--no-verify":
                return DENY, "Skipping commit hooks (--no-verify) bypasses secret and data checks."
            for position, letter in enumerate(short_flags(token)):
                if letter == "n":
                    return DENY, "Skipping commit hooks (-n) bypasses secret and data checks."
                if letter in "mFCct":  # Takes a value: attached, or the next argument.
                    if position == len(token) - 2:
                        index += 1
                    break
            index += 1
    if sub == "reset" and "--hard" in rest:
        return DENY, "git reset --hard discards local changes."
    if sub == "clean" and not ("--dry-run" in rest or any("n" in short_flags(token) for token in rest)):
        return DENY, "git clean deletes untracked files."
    if sub == "branch":
        letters = "".join(short_flags(token) for token in rest)
        deleting = "d" in letters or "--delete" in rest
        forcing = "f" in letters or "--force" in rest
        if "D" in letters or (deleting and forcing):
            return DENY, "Force-deleting a branch can lose unmerged work."
    return None


def check_proxmox(name: str, args: List[str]) -> Optional[Decision]:
    words = positional(args)
    sub = words[0] if words else ""
    if name in {"pct", "qm"} and sub == "destroy":
        return DENY, f"{name} destroy deletes a Proxmox guest irreversibly."
    if name == "pvesm" and sub in {"remove", "free"}:
        return DENY, f"pvesm {sub} removes storage or deletes a volume."
    if name == "pvecm" and sub in {"create", "add", "delnode", "expected"}:
        return DENY, f"pvecm {sub} changes cluster membership or quorum (ADR-0004)."
    if name == "pvesh" and len(words) > 1:
        path = words[1]
        if sub == "delete":
            if re.search(r"(^|/)(lxc|qemu|storage|cluster|disks)(/|$)", path):
                return DENY, f"pvesh delete {path} touches guests, storage or the cluster."
            return ASK, f"pvesh delete {path} deletes a Proxmox object."
        if sub in {"set", "create"} and re.search(r"(^|/)(network|firewall)(/|$)|(^|/)cluster/config", path):
            return ASK, f"pvesh {sub} {path} changes network, firewall or cluster configuration."
    return None


STORAGE_DESTROYERS = {"lvremove", "lvreduce", "vgremove", "pvremove", "wipefs", "sgdisk", "blkdiscard", "mkfs"}


def check_storage(name: str, args: List[str]) -> Optional[Decision]:
    if name in STORAGE_DESTROYERS or name.startswith("mkfs."):
        return DENY, f"{name} is a destructive storage operation."
    words = positional(args)
    if name == "zfs" and words[:1] == ["destroy"] or name == "zpool" and words[:1] in (["destroy"], ["labelclear"]):
        return DENY, f"{name} {words[0]} is a destructive ZFS operation."
    if name == "dd" and any(token.startswith("of=") for token in args):
        return DENY, "dd writing to a target can overwrite disks."
    return None


def check_gh(args: List[str]) -> Optional[Decision]:
    if args[:2] == ["repo", "delete"]:
        return DENY, "Deleting a GitHub repository is irreversible."
    if args[:1] == ["api"]:
        for index, token in enumerate(args):
            upper = token.upper()
            following = args[index + 1].upper() if index + 1 < len(args) else ""
            if upper in {"-XDELETE", "--METHOD=DELETE"} or (upper in {"-X", "--METHOD"} and following == "DELETE"):
                return DENY, "DELETE calls on the GitHub API require explicit authorization."
    return None


PROGRAM_RULES: Dict[str, Callable[[str, List[str]], Optional[Decision]]] = {
    "terraform": lambda name, args: check_terraform(args),
    "tofu": lambda name, args: check_terraform(args),
    "git": lambda name, args: check_git(args),
    "gh": lambda name, args: check_gh(args),
    "pct": check_proxmox, "qm": check_proxmox, "pvesm": check_proxmox, "pvecm": check_proxmox, "pvesh": check_proxmox,
}


# --- Nested commands ---------------------------------------------------------------------------------

SSH_VALUE_OPTIONS = set("-" + letter for letter in "bcDEeFIiJLlmOopQRSWw")
UNDECODABLE = "\x00undecodable"  # Marker for an encoded PowerShell command that cannot be inspected.


def nested_commands(name: str, args: List[str]) -> List[str]:
    """Command strings hidden inside this command: shells, eval, ssh, find -exec."""
    lowered = [token.lower() for token in args]
    if name in SHELLS:
        for index, token in enumerate(args):
            if token.startswith("-") and not token.startswith("--") and "c" in token and index + 1 < len(args):
                return [args[index + 1]]
    if name in POWERSHELLS:
        for index, token in enumerate(lowered):
            if index + 1 >= len(args):
                break
            if token in {"-c", "-command"}:
                return [" ".join(args[index + 1:])]
            if token in {"-e", "-ec", "-enc", "-encodedcommand"}:
                try:
                    return [base64.b64decode(args[index + 1]).decode("utf-16-le")]
                except (binascii.Error, UnicodeDecodeError, ValueError):
                    return [UNDECODABLE]
    if name == "cmd":
        for index, token in enumerate(lowered):
            if token in {"/c", "/k"}:
                return [" ".join(args[index + 1:])]
    if name == "eval":
        return [" ".join(args)]
    if name == "ssh":
        hosts = positional(args, SSH_VALUE_OPTIONS)
        return [" ".join(hosts[1:])] if len(hosts) > 1 else []
    if name == "find":
        found, current = [], None
        for token in args:
            if token in {"-exec", "-execdir", "-ok", "-okdir"}:
                current = []
            elif current is not None and token in {";", "\\;", "+"}:
                found.append(" ".join(current))
                current = None
            elif current is not None:
                current.append(token)
        if current:  # Unterminated -exec: inspect it anyway.
            found.append(" ".join(current))
        return found
    return []


SUBSTITUTION = re.compile(r"[$<>]\(([^()]*)\)|`([^`]*)`")


def evaluate(command: str, depth: int = 0) -> Optional[Decision]:
    """Return the most severe (decision, reason) for a command, or None to defer to normal permissions."""
    if depth > MAX_DEPTH:
        return DENY, "Command nesting is too deep to inspect."
    found: List[Decision] = []
    inner = [match.group(1) or match.group(2) or "" for match in SUBSTITUTION.finditer(command)]
    for text in inner:
        result = evaluate(text, depth + 1)
        if result:
            found.append(result)
    for segment in split_segments(SUBSTITUTION.sub(" ", command)):
        argv = strip_wrappers(tokenize(segment))
        if not argv:
            continue
        name, args = program_name(argv[0]), argv[1:]
        rule = PROGRAM_RULES.get(name)
        result = rule(name, args) if rule else check_storage(name, args)
        if result:
            found.append(result)
        for text in nested_commands(name, args):
            if text == UNDECODABLE:
                found.append((DENY, "Encoded PowerShell command cannot be decoded and inspected."))
                continue
            nested = evaluate(text, depth + 1)
            if nested:
                found.append(nested)
    for decision in (DENY, ASK):
        for result in found:
            if result[0] == decision:
                return result
    return None


GUARDED_TOOLS = {"Bash", "PowerShell"}
REASON_PREFIX = {
    DENY: "Denied by the guard hook (.claude/hooks/): ",
    ASK: "Needs your explicit approval (guard hook, .claude/hooks/): ",
}


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as error:
        print(f"guard hook: invalid hook input: {error}", file=sys.stderr)
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
            "permissionDecisionReason": REASON_PREFIX[decision] + reason,
        }
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
