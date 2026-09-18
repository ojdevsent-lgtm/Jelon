from __future__ import annotations

from engine.agent.tools import PermissionPolicy
from engine.computer.agent_tool import WindowsComputerTool
from engine.computer.windows import WindowsComputerAdapter
from engine.integration import build_agent


def build_windows_agent(
    model,
    *,
    allow_processes: bool = False,
    allow_browser: bool = False,
    allow_network: bool = False,
    allow_git_write: bool = False,
    allow_git_push: bool = False,
    data_path: str = "data/jelon_learning.json",
    browser_tool=None,
    git_tool=None,
):
    """Build a Jelon agent with Windows control plus optional browser/Git tools.

    Browser and Git adapters are injected rather than imported here, keeping the
    core offline-first and allowing different implementations.
    """
    policy = PermissionPolicy(
        allow_processes=allow_processes,
        allow_browser=allow_browser,
        allow_network=allow_network,
        allow_git_write=allow_git_write,
        allow_git_push=allow_git_push,
    )
    tools = [WindowsComputerTool(WindowsComputerAdapter())]
    if browser_tool is not None:
        tools.append(browser_tool)
    if git_tool is not None:
        tools.append(git_tool)
    return build_agent(model, policy=policy, data_path=data_path, tools=tools)
