from __future__ import annotations

import os
import tempfile
import unittest

from engine.desktop_server import DesktopServer


class DesktopServerControlTests(unittest.TestCase):
    def test_control_is_disabled_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_policy = os.environ.get("JELON_POLICY_PATH")
            old_memory = os.environ.get("JELON_MEMORY_PATH")
            os.environ["JELON_POLICY_PATH"] = os.path.join(tmp, "policy.json")
            os.environ["JELON_MEMORY_PATH"] = os.path.join(tmp, "memory.json")
            try:
                server = DesktopServer()
                status = server.handle({"type": "status"})
                self.assertFalse(status["computer_control"])
                self.assertEqual(status["autonomy"], "ask")
            finally:
                if old_policy is None:
                    os.environ.pop("JELON_POLICY_PATH", None)
                else:
                    os.environ["JELON_POLICY_PATH"] = old_policy
                if old_memory is None:
                    os.environ.pop("JELON_MEMORY_PATH", None)
                else:
                    os.environ["JELON_MEMORY_PATH"] = old_memory

    def test_control_can_be_explicitly_enabled_and_disabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["JELON_POLICY_PATH"] = os.path.join(tmp, "policy.json")
            os.environ["JELON_MEMORY_PATH"] = os.path.join(tmp, "memory.json")
            server = DesktopServer()

            enabled = server.handle({"type": "policy.set", "computer_control": True})
            self.assertTrue(enabled["computer_control"])
            self.assertEqual(enabled["autonomy"], "trusted_workspace")
            self.assertIn("windows_computer", enabled["tools"])

            disabled = server.handle({"type": "policy.set", "computer_control": False})
            self.assertFalse(disabled["computer_control"])
            self.assertEqual(disabled["autonomy"], "ask")

            os.environ.pop("JELON_POLICY_PATH", None)
            os.environ.pop("JELON_MEMORY_PATH", None)


if __name__ == "__main__":
    unittest.main()
