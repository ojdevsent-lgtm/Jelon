from __future__ import annotations
from engine.agent.agent_controller import AgentController, Goal
from engine.agent.tools import PermissionPolicy, ToolRegistry
from engine.learning.store import LearningStore
from engine.learning.self_correction import SelfCorrection, RetryPolicy
from engine.model.local_model import LocalModel


def build_agent(model: LocalModel, policy: PermissionPolicy | None = None, data_path: str = "data/jelon_learning.json") -> AgentController:
    """Construct Jelon core with all currently available local layers."""
    registry = ToolRegistry(policy or PermissionPolicy())
    store = LearningStore(data_path)
    correction = SelfCorrection(model, RetryPolicy())
    return AgentController(model, registry, store, correction)


def run_goal(agent: AgentController, text: str):
    return agent.run(Goal(text))
