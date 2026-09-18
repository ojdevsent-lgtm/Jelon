from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class RetryPolicy:
    max_attempts: int = 3

@dataclass
class TaskMemory:
    goal: str
    attempts: list[dict[str, Any]] = field(default_factory=list)

class SelfCorrection:
    """Bounded reflection helper. A model can turn observations into the next action."""
    def __init__(self, model, retry_policy: RetryPolicy | None = None):
        self.model = model
        self.retry_policy = retry_policy or RetryPolicy()

    def next_instruction(self, goal: str, observation: str, attempt: int) -> str | None:
        if attempt >= self.retry_policy.max_attempts:
            return None
        prompt = (
            "Analyze this failed agent attempt and propose one safer corrective action. "
            "Do not repeat the same failed action.\n"
            f"Goal: {goal}\nObservation: {observation}"
        )
        result = self.model.generate(prompt).strip()
        return result or None
