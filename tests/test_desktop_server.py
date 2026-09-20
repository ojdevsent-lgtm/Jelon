from __future__ import annotations

import os
import sys
import tempfile
import unittest

from engine.desktop_server import DesktopServer


class DesktopServerControlTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["JELON_POLICY_PATH"] = os.path.join(self.tmp.name, "policy.json")
        os.environ["JELON_MEMORY_PATH"] = os.path.join(self.tmp.name, "memory.json")

    def tearDown(self):
        os.environ.pop("JELON_POLICY_PATH", None)
        os.environ.pop("JELON_MEMORY_PATH", None)
        self.tmp.cleanup()

    def test_control_is_disabled_by_default(self):
        server = DesktopServer()
        status = server.handle({"type": "status"})
        self.assertFalse(status["computer_control"])
        self.assertEqual(status["autonomy"], "ask")

    def test_control_can_be_explicitly_enabled_and_disabled(self):
        server = DesktopServer()

        enabled = server.handle({"type": "policy.set", "computer_control": True})
        self.assertTrue(enabled["computer_control"])
        self.assertEqual(enabled["autonomy"], "trusted_workspace")
        if sys.platform == "win32":
            self.assertIn("windows_computer", enabled["tools"])

        disabled = server.handle({"type": "policy.set", "computer_control": False})
        self.assertFalse(disabled["computer_control"])
        self.assertEqual(disabled["autonomy"], "ask")


if __name__ == "__main__":
    unittest.main()
