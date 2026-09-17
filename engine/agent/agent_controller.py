from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol, Any

class Model(Protocol):
    def generate(self, prompt: str) -> str: ...

class Tool(Protocol):
    def execute(self, arguments: dict[str, Any]) -> Any: ...

@dataclass
class Goal:
    text: str
    context: dict[str, Any] = field(default_factory=dict)

@dataclass
class Step:
    action: str
    tool: str | None = None
    arguments: dict[str, Any] = field(default_factory=dict)

@dataclass
class Observation:
    success: bool
    output: str
    data: dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentResult:
    status: str
    summary: str
    steps: list[Step]
    observations: list[Observation] = field(default_factory=list)

class AgentController:
    def __init__(self, model: Model | None = None, tools: dict[str, Tool] | None = None, max_steps: int = 12):
        self.model = model
        self.tools = tools or {}
        self.max_steps = max_steps

    def plan(self, goal: Goal) -> list[Step]:
        if self.model is None:
            return [Step(action="inspect_and_plan", arguments={"goal": goal.text})]
        raw = self.model.generate(
            "Create a safe execution plan. Return one tool action per line. "
            f"Goal: {goal.text}"
        )
        steps: list[Step] = []
        for line in raw.splitlines():
            line = line.strip()
            if line:
                steps.append(Step(action=line))
        return steps or [Step(action="inspect_and_plan", arguments={"goal": goal.text})]

    def run(self, goal: Goal) -> AgentResult:
        steps = self.plan(goal)[: self.max_steps]
        observations: list[Observation] = []
        for step in steps:
            if not step.tool:
                observations.append(Observation(True, f"Planned: {step.action}"))
                continue
            tool = self.tools.get(step.tool)
            if tool is None:
                observation = Observation(False, f"Unknown tool: {step.tool}")
            else:
                try:
                    observation = tool.execute(step.arguments)
                except Exception as exc:
                    observation = Observation(False, str(exc))
            observations.append(observation)
            if not observation.success:
                return AgentResult("failed", f"Execution stopped at tool '{step.tool}'.", steps, observations)
        return AgentResult("completed", "Agent execution completed within the configured step limit.", steps, observations)
