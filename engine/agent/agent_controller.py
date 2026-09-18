from __future__ import annotations
import json
import re
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
    """Bounded goal -> plan -> tool -> observe -> correct loop."""
    def __init__(self, model=None, tool_registry=None, learning_store=None, self_correction=None, max_steps=12):
        self.model, self.tool_registry = model, tool_registry
        self.learning_store, self.self_correction = learning_store, self_correction
        self.max_steps = max_steps

    def _tool_context(self):
        if self.tool_registry is None:
            return "[]"
        return json.dumps(self.tool_registry.describe(), ensure_ascii=False)

    @staticmethod
    def _extract_json(raw):
        text = str(raw).strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\\s*", "", text, flags=re.I)
            text = re.sub(r"\\s*```$", "", text)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"(\\[[\\s\\S]*\\]|\\{[\\s\\S]*\\})", text)
            if not match: return None
            try: return json.loads(match.group(1))
            except json.JSONDecodeError: return None

    def _steps_from_model(self, raw):
        parsed = self._extract_json(raw)
        items = parsed if isinstance(parsed, list) else ([parsed] if isinstance(parsed, dict) else [])
        result = []
        for item in items:
            if not isinstance(item, dict): continue
            args = item.get("arguments")
            if not isinstance(args, dict): args = {}
            result.append(Step(str(item.get("action", "inspect")).strip() or "inspect",
                               str(item["tool"]) if item.get("tool") is not None else None, args))
        return result

    def plan(self, goal):
        if self.model is None: return [Step("inspect_and_plan", arguments={"goal": goal.text})]
        prompt = (
            "You are Jelon, a bounded local computer agent. Return ONLY a JSON array of steps. "
            "Each step is {\"action\":\"...\",\"tool\":null|string,\"arguments\":{}}. "
            "Use only registered tools; never invent tool names; do not claim actions happened without observations.\n"
            f"Available tools: {self._tool_context()}\nGoal: {goal.text}\n"
            f"Context: {json.dumps(goal.context, ensure_ascii=False)}"
        )
        return self._steps_from_model(self.model.generate(prompt)) or [Step("inspect_and_plan", arguments={"goal": goal.text})]

    def _observe(self, result):
        if isinstance(result, Observation): return result
        if isinstance(result, dict): return Observation(bool(result.get("success", False)), str(result.get("output", "")), result.get("data") or {})
        return Observation(True, str(result))

    def _execute(self, step):
        if self.tool_registry is None or not step.tool: return Observation(True, f"Planned: {step.action}")
        try: return self._observe(self.tool_registry.execute(step.tool, step.arguments))
        except Exception as exc: return Observation(False, f"{type(exc).__name__}: {exc}")

    def _correction(self, goal, step, observation, attempt):
        if self.self_correction is None: return None
        payload = json.dumps({"failed_step": step.__dict__, "observation": observation.output, "attempt": attempt, "available_tools": self.tool_registry.describe() if self.tool_registry else []}, ensure_ascii=False)
        instruction = self.self_correction.next_instruction(goal.text, payload, attempt)
        if not instruction: return None
        corrected = self._steps_from_model(instruction)
        return corrected[0] if corrected else self._instruction_to_step(instruction)

    def run(self, goal):
        steps = self.plan(goal)[:self.max_steps]
        observations, attempts, index = [], 0, 0
        while index < len(steps) and attempts < self.max_steps:
            step = steps[index]; attempts += 1
            observation = self._execute(step); observations.append(observation)
            if observation.success: index += 1; continue
            corrected = self._correction(goal, step, observation, attempts)
            if corrected is None:
                summary = f"Step failed: {observation.output}"
                if self.learning_store: self.learning_store.record_task(goal.text, "failed", summary)
                return AgentResult("failed", summary, steps, observations, attempts)
            steps.insert(index, corrected)
        completed = index >= len(steps)
        status = "completed" if completed else "failed"
        summary = "Agent execution completed." if completed else "Agent stopped at execution limit."
        if self.learning_store: self.learning_store.record_task(goal.text, status, summary)
        return AgentResult(status, summary, steps, observations, attempts)

    @staticmethod
    def _instruction_to_step(instruction):
        parsed = AgentController._extract_json(instruction)
        if isinstance(parsed, dict): return Step(str(parsed.get("action", instruction)), parsed.get("tool"), parsed.get("arguments") or {})
        return Step(action=instruction)