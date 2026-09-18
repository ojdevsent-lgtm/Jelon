from __future__ import annotations
import json
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
    attempts: int = 0

class AgentController:
    """Bounded goal -> plan -> tool -> observe -> correct loop.

    Learning is persisted outside the model weights. Tool execution remains
    constrained by the supplied ToolRegistry/policy.
    """

    def __init__(
        self,
        model: Model | None = None,
        tool_registry: Any | None = None,
        learning_store: Any | None = None,
        self_correction: Any | None = None,
        max_steps: int = 12,
    ):
        self.model = model
        self.tool_registry = tool_registry
        self.learning_store = learning_store
        self.self_correction = self_correction
        self.max_steps = max_steps

    def plan(self, goal: Goal) -> list[Step]:
        if self.model is None:
            return [Step(action="inspect_and_plan", arguments={"goal": goal.text})]
        raw = self.model.generate(
            "Return a JSON array of agent steps. Each step must have "
            '{"action": "...", "tool": null|string, "arguments": {}}. '
            "Use only the minimum actions required. "
            f"Goal: {goal.text}"
        ).strip()
        try:
            items = json.loads(raw)
            if isinstance(items, list):
                result = []
                for item in items:
                    if isinstance(item, dict):
                        result.append(Step(
                            action=str(item.get("action", "")),
                            tool=item.get("tool"),
                            arguments=item.get("arguments") or {},
                        ))
                if result:
                    return result
        except (json.JSONDecodeError, TypeError):
            pass
        return [Step(action=raw or "inspect_and_plan")]

    def _observe(self, result: Any) -> Observation:
        if isinstance(result, Observation):
            return result
        if isinstance(result, dict):
            return Observation(
                bool(result.get("success", False)),
                str(result.get("output", "")),
                result.get("data") or {},
            )
        return Observation(True, str(result))

    def _execute(self, step: Step) -> Observation:
        if self.tool_registry is None or not step.tool:
            return Observation(True, f"Planned: {step.action}")
        executor = getattr(self.tool_registry, "execute", None)
        if executor is None:
            return Observation(False, "Tool registry has no execute() method.")
        try:
            return self._observe(executor(step.tool, step.arguments))
        except Exception as exc:
            return Observation(False, f"{type(exc).__name__}: {exc}")

    def run(self, goal: Goal) -> AgentResult:
        steps = self.plan(goal)[: self.max_steps]
        observations: list[Observation] = []
        attempts = 0
        index = 0

        while index < len(steps) and attempts < self.max_steps:
            step = steps[index]
            attempts += 1
            observation = self._execute(step)
            observations.append(observation)

            if observation.success:
                index += 1
                continue

            if self.self_correction is None:
                summary = f"Tool '{step.tool}' failed." if step.tool else "Planned step failed."
                if self.learning_store:
                    self.learning_store.record_task(goal.text, "failed", summary)
                return AgentResult("failed", summary, steps, observations, attempts)

            instruction = self.self_correction.next_instruction(
                goal.text, observation.output, attempts
            )
            if not instruction:
                summary = "Agent stopped after bounded self-correction attempts."
                if self.learning_store:
                    self.learning_store.record_task(goal.text, "failed", summary)
                return AgentResult("failed", summary, steps, observations, attempts)

            corrected = self._instruction_to_step(instruction)
            steps.insert(index, corrected)

        completed = index >= len(steps)
        status = "completed" if completed else "failed"
        summary = "Agent execution completed." if completed else "Agent stopped at execution limit."
        if self.learning_store:
            self.learning_store.record_task(goal.text, status, summary)
        return AgentResult(status, summary, steps, observations, attempts)

    @staticmethod
    def _instruction_to_step(instruction: str) -> Step:
        try:
            item = json.loads(instruction)
            if isinstance(item, dict):
                return Step(
                    action=str(item.get("action", instruction)),
                    tool=item.get("tool"),
                    arguments=item.get("arguments") or {},
                )
        except (json.JSONDecodeError, TypeError):
            pass
        return Step(action=instruction)
