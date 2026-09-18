import tempfile
import unittest
from pathlib import Path
from engine.security.desktop_policy import DesktopPolicy, PolicyStore
from engine.security.permission_gate import PermissionGate

class DesktopPolicyTests(unittest.TestCase):
    def test_safe_defaults(self):
        policy = DesktopPolicy()
        policy.validate()
        self.assertFalse(policy.allow_network)
        self.assertFalse(policy.allow_browser)
        self.assertFalse(policy.allow_git_push)
        self.assertEqual(policy.autonomy, "ask")

    def test_browser_requires_network(self):
        with self.assertRaises(ValueError):
            DesktopPolicy(allow_browser=True).validate()

    def test_push_requires_authorized_repo(self):
        with self.assertRaises(ValueError):
            DesktopPolicy(allow_git_push=True, autonomy="trusted_workspace").validate()

    def test_policy_persists(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "policy.json"
            PolicyStore(path).save(DesktopPolicy(autonomy="trusted_workspace", allow_processes=True))
            loaded = PolicyStore(path).load()
            self.assertEqual(loaded.autonomy, "trusted_workspace")
            self.assertTrue(loaded.allow_processes)

    def test_gate_blocks_network_by_default(self):
        self.assertFalse(PermissionGate(DesktopPolicy()).check("allow_network").allowed)

if __name__ == "__main__":
    unittest.main()
