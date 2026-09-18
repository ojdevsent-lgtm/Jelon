import unittest

from engine.computer.windows import WindowsComputerAdapter


class WindowsComputerAdapterTests(unittest.TestCase):
    def test_methods_exist(self):
        adapter = WindowsComputerAdapter()
        for name in ("launch_process", "open_path", "mouse_move", "mouse_click", "key_press", "hotkey", "type_text"):
            self.assertTrue(callable(getattr(adapter, name)))


if __name__ == "__main__":
    unittest.main()
