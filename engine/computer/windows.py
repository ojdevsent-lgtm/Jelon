from __future__ import annotations

import ctypes
import os
import subprocess
import time
from pathlib import Path
from typing import Iterable


class WindowsComputerAdapter:
    """Concrete Windows input/process adapter using only the standard library."""

    _user32 = ctypes.windll.user32 if os.name == "nt" else None

    def _require_windows(self):
        if self._user32 is None:
            raise OSError("WindowsComputerAdapter requires Windows.")

    def launch_process(self, command: str, wait: bool = False) -> str:
        self._require_windows()
        if not command.strip():
            raise ValueError("command must not be empty")
        proc = subprocess.Popen(command, shell=True)
        if wait:
            proc.wait()
        return f"process started: pid={proc.pid}"

    def open_path(self, path: str) -> str:
        self._require_windows()
        target = str(Path(path).expanduser())
        if not os.path.exists(target):
            raise FileNotFoundError(target)
        os.startfile(target)
        return f"opened: {target}"

    def mouse_move(self, x: int, y: int) -> str:
        self._require_windows()
        self._user32.SetCursorPos(int(x), int(y))
        return f"mouse moved to {int(x)},{int(y)}"

    def mouse_click(self, button: str = "left", double: bool = False) -> str:
        self._require_windows()
        flags = {"left": (0x0002, 0x0004), "right": (0x0008, 0x0010), "middle": (0x0020, 0x0040)}
        if button not in flags:
            raise ValueError("button must be left, right, or middle")
        down, up = flags[button]
        for _ in range(2 if double else 1):
            self._user32.mouse_event(down, 0, 0, 0, 0)
            self._user32.mouse_event(up, 0, 0, 0, 0)
            if double:
                time.sleep(0.05)
        return f"{button} click"

    def key_press(self, virtual_key: int) -> str:
        self._require_windows()
        vk = int(virtual_key)
        self._user32.keybd_event(vk, 0, 0, 0)
        self._user32.keybd_event(vk, 0, 2, 0)
        return f"key pressed: {vk}"

    def hotkey(self, virtual_keys: Iterable[int]) -> str:
        self._require_windows()
        keys = [int(k) for k in virtual_keys]
        if not keys:
            raise ValueError("virtual_keys must not be empty")
        for vk in keys:
            self._user32.keybd_event(vk, 0, 0, 0)
        for vk in reversed(keys):
            self._user32.keybd_event(vk, 0, 2, 0)
        return "hotkey sent: " + "+".join(str(k) for k in keys)

    def type_text(self, text: str, interval: float = 0.0) -> str:
        self._require_windows()
        KEYEVENTF_UNICODE = 0x0004
        KEYEVENTF_KEYUP = 0x0002

        class KEYBDINPUT(ctypes.Structure):
            _fields_ = [("wVk", ctypes.c_ushort), ("wScan", ctypes.c_ushort),
                        ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong),
                        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

        class INPUT(ctypes.Structure):
            _fields_ = [("type", ctypes.c_ulong), ("ki", KEYBDINPUT)]

        extra = ctypes.c_ulong(0)
        sent = 0
        for char in text:
            scan = ord(char)
            inputs = (INPUT * 2)(
                INPUT(1, KEYBDINPUT(0, scan, KEYEVENTF_UNICODE, 0, ctypes.pointer(extra))),
                INPUT(1, KEYBDINPUT(0, scan, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP, 0, ctypes.pointer(extra))),
            )
            if self._user32.SendInput(2, ctypes.byref(inputs), ctypes.sizeof(INPUT)) != 2:
                raise ctypes.WinError()
            sent += 1
            if interval > 0:
                time.sleep(interval)
        return f"typed {sent} characters"
