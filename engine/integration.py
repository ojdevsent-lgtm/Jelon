from __future__ import annotations
from engine.agent.agent_controller import AgentController, Goal
from engine.agent.tools import PermissionPolicy, ToolRegistry
from engine.learning.store import LearningStore
from engine.learning.self_correction import SelfCorrection, RetryPolicy
from engine.model.local_model import LocalModel

def build_agent(model: LocalModel, policy=None, data_path="data/jelon_learning.json", tools=None):
    """Construct Jelon core and register only explicitly supplied tools."""
    registry = ToolRegistry(policy or PermissionPolicy())
    for tool in tools or []: registry.register(tool)
    store = LearningStore(data_path)
    return AgentController(model, registry, store, SelfCorrection(model, RetryPolicy()))

def run_goal(agent: AgentController, text: str, context=None):
    return agent.run(Goal(text, context or {}))