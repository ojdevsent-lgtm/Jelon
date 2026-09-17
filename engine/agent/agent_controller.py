from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol, Any

class Model(Protocol):
    def generate(self, prompt: str) -> str: ...

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
class AgentResult:
    status: str
    summary: str
    steps: list[Step]

class AgentController:
    def __init__(self, model: Model | None = None):
        self.model = model

    def plan(self, goal: Goal) -> list[Step]:
        if self.model is None:
            return [Step(action="inspect_and_plan", tool=None, arguments={"goal": goal.text})]
        raw = self.model.generate(f"Create a safe execution plan for: {goal.text}")
        return [Step(action=raw)]

    def run(self, goal: Goal) -> AgentResult:
        steps = self.plan(goal)
        return AgentResult("planned", "Goal accepted and execution plan created.", steps)
