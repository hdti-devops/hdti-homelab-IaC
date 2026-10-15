"""Unit tests for the guard hook and its launcher. Run: python -m unittest discover -s .claude/hooks -v"""

import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from guard_dangerous_commands import evaluate  # noqa: E402

HOOK_DIR = Path(__file__).parent
HOOK = HOOK_DIR / "guard_dangerous_commands.py"
LAUNCHER = HOOK_DIR / "run_guard.sh"


def encoded_powershell(command: str) -> str:
    return base64.b64encode(command.encode("utf-16-le")).decode("ascii")


DENIED = [
    # Terraform
    "terraform apply",
    "terraform -chdir=terraform/environments/homelab/dns apply -auto-approve",
    "/usr/bin/terraform destroy",
    "C:\\tools\\terraform.exe apply",
    "terraform force-unlock 1234",
    "terraform state rm module.dns",
    "terraform state push backup.tfstate",
    "terraform workspace delete homelab-dns",
    "tofu apply",
    "cd terraform/environments/homelab/dns && terraform apply",
    "terraform plan; terraform destroy",
    "terraform \\\n  apply",
    # Wrapped and nested
    "sudo terraform apply",
    "env TF_LOG=debug terraform apply",
    "timeout 60 terraform apply",
    "sh -c \"terraform apply\"",
    "bash -lc 'terraform plan && terraform apply'",
    "sh <<'EOF'\nterraform apply\nEOF",
    "eval \"terraform destroy\"",
    "echo $(terraform apply)",
    "echo `git push --force`",
    "ssh root@pve \"pct destroy 101\"",
    "ssh -p 22 -i key root@pve qm destroy 301",
    "pwsh -Command \"git push --force\"",
    "powershell -EncodedCommand " + encoded_powershell("terraform apply"),
    "powershell -enc not-base64!",
    "cmd /c git push -f",
    "find . -name x -exec git clean -fdx \\;",
    # git
    "git push --force origin main",
    "git push --force-with-lease",
    "git push -f",
    "git push -fu origin main",
    "git push origin +main",
    "git push origin --delete main",
    "git push origin -d main",
    "git push origin :main",
    "git commit -n -m wip",
    "git commit -anm wip",
    "git commit --no-verify -m wip",
    "git -c core.hooksPath=/dev/null commit -m wip",
    "git config core.hooksPath .none",
    "git reset --hard HEAD~1",
    "git clean -fdx",
    "git -C /tmp/x clean -fdx",
    "git branch -D feature/old",
    "git branch -fD x",
    "git branch --delete --force feature/old",
    # Proxmox and storage
    "pct destroy 101",
    "qm destroy 301 --purge",
    "pvecm expected 1",
    "pvecm delnode pve2",
    "pvecm create newcluster",
    "pvecm add 192.168.2.200",
    "pvesm remove local-lvm",
    "pvesm free local-lvm:vm-101-disk-0",
    "pvesh delete /nodes/pve/lxc/101",
    "pvesh delete /nodes/pve/qemu/301",
    "pvesh delete /storage/local-lvm",
    "pvesh delete /cluster/config/nodes/pve2",
    "lvremove pve/data",
    "wipefs -a /dev/sda",
    "mkfs.ext4 /dev/sdb1",
    "zfs destroy rpool/data",
    "zpool labelclear /dev/sdb",
    "dd if=/dev/zero of=/dev/sda bs=1M",
    # GitHub
    "gh repo delete hdti-devops/hdti-homelab-IaC --yes",
    "gh api -X DELETE repos/hdti-devops/x",
    "gh api --method=DELETE repos/hdti-devops/x",
]

ASKED = [
    "terraform state mv module.a module.b",
    "terraform import proxmox_virtual_environment_container.dns pve2/lxc/101",
    "pvesh delete /access/users/terraform@pve/token/old",
    "pvesh set /nodes/pve/network/vmbr0 --cidr 192.168.2.200/24",
]

ALLOWED = [
    # Read-only or safe
    "terraform plan",
    "terraform plan -destroy",
    "terraform show apply.tfplan",
    "terraform -chdir=terraform/environments/homelab/dns plan -out=dns.tfplan",
    "terraform validate",
    "terraform fmt -check -recursive",
    "terraform state list",
    "echo terraform apply",
    "git status",
    "git push -u origin feature/safety-enforcement",
    "git push -u origin bugfix/fix-dns",
    "git commit -F message.txt",
    "git commit -m \"docs: explain -n flag\"",
    "git commit -m \"docs: never reset --hard\"",
    "git commit -am \"feat: add runbook\"",
    "git branch -d feature/merged",
    "git clean -n",
    "git config --get core.hooksPath",
    "git add docs/adr/README.md",
    "gh pr create --base main --title \"ci: block terraform destroy\" --body-file b.md",
    "gh api repos/hdti-devops/hdti-homelab-IaC",
    "pct list",
    "qm config 301",
    "pvecm status",
    "pvesm status",
    "pvesh get /cluster/resources --output-format json-pretty",
    "ls 2>&1 | grep x",
    "python - <<'PY'\ntext = 'folders such as terraform/ are added later'\nother = 'apply the approved fixes'\nPY",
]


class EvaluateTests(unittest.TestCase):
    def check(self, commands, expected):
        for command in commands:
            with self.subTest(command=command):
                result = evaluate(command)
                self.assertEqual(result[0] if result else None, expected)

    def test_denied(self):
        self.check(DENIED, "deny")

    def test_asked(self):
        self.check(ASKED, "ask")

    def test_allowed(self):
        self.check(ALLOWED, None)


def run(argv, payload, env=None):
    return subprocess.run(argv, input=payload, capture_output=True, text=True, env=env)


def bash_payload(command, tool="Bash"):
    return json.dumps({"tool_name": tool, "tool_input": {"command": command}})


class HookContractTests(unittest.TestCase):
    def test_deny_output(self):
        result = run([sys.executable, str(HOOK)], bash_payload("terraform apply"))
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "PreToolUse")
        self.assertEqual(output["permissionDecision"], "deny")
        self.assertTrue(output["permissionDecisionReason"].startswith("Denied"))

    def test_ask_output_does_not_say_blocked(self):
        result = run([sys.executable, str(HOOK)], bash_payload("terraform import a b"))
        output = json.loads(result.stdout)["hookSpecificOutput"]
        self.assertEqual(output["permissionDecision"], "ask")
        self.assertTrue(output["permissionDecisionReason"].startswith("Needs your explicit approval"))

    def test_powershell_tool_is_guarded(self):
        result = run([sys.executable, str(HOOK)], bash_payload("git push -f", tool="PowerShell"))
        self.assertEqual(json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_safe_command_defers(self):
        result = run([sys.executable, str(HOOK)], bash_payload("terraform plan"))
        self.assertEqual((result.returncode, result.stdout.strip()), (0, ""))

    def test_other_tools_ignored(self):
        payload = json.dumps({"tool_name": "Write", "tool_input": {"content": "terraform apply"}})
        result = run([sys.executable, str(HOOK)], payload)
        self.assertEqual((result.returncode, result.stdout.strip()), (0, ""))

    def test_invalid_input_fails_closed(self):
        self.assertEqual(run([sys.executable, str(HOOK)], "not json").returncode, 2)


SH = shutil.which("sh")


@unittest.skipIf(SH is None, "sh is not available")
class LauncherTests(unittest.TestCase):
    def test_launcher_runs_hook(self):
        result = run([SH, str(LAUNCHER)], bash_payload("terraform apply"))
        self.assertEqual(json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_launcher_fails_closed_without_python(self):
        with tempfile.TemporaryDirectory() as empty_dir:
            env = dict(os.environ, PATH=empty_dir)
            result = run([SH, str(LAUNCHER)], bash_payload("terraform plan"), env=env)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Command blocked", result.stderr)


if __name__ == "__main__":
    unittest.main()
