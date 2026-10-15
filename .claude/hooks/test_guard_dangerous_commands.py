"""Unit tests for guard_dangerous_commands.py. Run: python -m unittest discover -s .claude/hooks -v"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from guard_dangerous_commands import evaluate  # noqa: E402

HOOK = Path(__file__).parent / "guard_dangerous_commands.py"

DENIED = [
    "terraform apply",
    "terraform -chdir=terraform/environments/homelab/dns apply -auto-approve",
    "/usr/bin/terraform destroy",
    "sh -c \"terraform apply\"",
    "echo terraform apply",
    "terraform force-unlock 1234",
    "terraform state rm module.dns",
    "terraform state push backup.tfstate",
    "terraform workspace delete homelab-dns",
    "tofu apply",
    "git push --force origin main",
    "git push --force-with-lease",
    "git push -f",
    "git push origin +main",
    "git commit -n -m wip",
    "git commit -anm wip",
    "git commit --no-verify -m wip",
    "git -c core.hooksPath=/dev/null commit -m wip",
    "git config core.hooksPath .none",
    "git reset --hard HEAD~1",
    "git clean -fdx",
    "git branch -D feature/old",
    "git branch --delete --force feature/old",
    "pct destroy 101",
    "qm destroy 301 --purge",
    "pvecm expected 1",
    "pvecm delnode pve2",
    "pvesm remove local-lvm",
    "lvremove pve/data",
    "wipefs -a /dev/sda",
    "mkfs.ext4 /dev/sdb1",
    "zfs destroy rpool/data",
    "dd if=/dev/zero of=/dev/sda bs=1M",
    "gh repo delete hdti-devops/hdti-homelab-IaC --yes",
    "gh api -X DELETE repos/hdti-devops/x",
    "terraform \\\n  apply",
    "cd terraform/environments/homelab/dns && terraform apply",
    "sh <<'EOF'\nterraform apply\nEOF",
    "terraform plan; terraform destroy",
]

ASKED = [
    "terraform state mv module.a module.b",
    "terraform import proxmox_virtual_environment_container.dns pve2/lxc/101",
]

ALLOWED = [
    "terraform plan",
    "terraform -chdir=terraform/environments/homelab/dns plan -out=dns.tfplan",
    "terraform validate",
    "terraform fmt -check -recursive",
    "terraform state list",
    "git push -u origin feature/safety-enforcement",
    "git push -u origin bugfix/fix-dns",
    "git commit -F message.txt",
    "git commit -m \"docs: add runbook\"",
    "git branch -d feature/merged",
    "git status",
    "pct list",
    "qm config 301",
    "pvecm status",
    "pvesm status",
    "gh pr create --base main --title t --body-file b.md",
    "gh api repos/hdti-devops/hdti-homelab-IaC",
    "git add docs/adr/README.md",
    "python - <<'PY'\ntext = 'folders such as terraform/ are added later'\nother = 'apply the approved fixes'\nPY",
]


class EvaluateTests(unittest.TestCase):
    def test_denied(self):
        for command in DENIED:
            with self.subTest(command=command):
                self.assertEqual(evaluate(command)[0], "deny")

    def test_asked(self):
        for command in ASKED:
            with self.subTest(command=command):
                self.assertEqual(evaluate(command)[0], "ask")

    def test_allowed(self):
        for command in ALLOWED:
            with self.subTest(command=command):
                self.assertIsNone(evaluate(command))


class HookContractTests(unittest.TestCase):
    def run_hook(self, payload: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(HOOK)], input=payload, capture_output=True, text=True)

    def test_deny_output(self):
        result = self.run_hook(json.dumps({"tool_name": "Bash", "tool_input": {"command": "terraform apply"}}))
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "PreToolUse")
        self.assertEqual(output["permissionDecision"], "deny")

    def test_powershell_tool_is_guarded(self):
        result = self.run_hook(json.dumps({"tool_name": "PowerShell", "tool_input": {"command": "git push -f"}}))
        self.assertEqual(json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_safe_command_defers(self):
        result = self.run_hook(json.dumps({"tool_name": "Bash", "tool_input": {"command": "terraform plan"}}))
        self.assertEqual((result.returncode, result.stdout.strip()), (0, ""))

    def test_other_tools_ignored(self):
        result = self.run_hook(json.dumps({"tool_name": "Write", "tool_input": {"content": "terraform apply"}}))
        self.assertEqual((result.returncode, result.stdout.strip()), (0, ""))

    def test_invalid_input_fails_closed(self):
        self.assertEqual(self.run_hook("not json").returncode, 2)


if __name__ == "__main__":
    unittest.main()
