import json
import tempfile
import unittest
from pathlib import Path

from engine.agent.agent_controller import AgentController, Goal, Observation
from engine.agent.tools import PermissionPolicy, ToolRegistry
from engine.learning.store import LearningStore
from engine.learning.self_correction import SelfCorrection, RetryPolicy

class FakeModel:
    def __init__(self, responses):
        self.responses = iter(responses)

    def generate(self, prompt):
        return next(self.responses)

class FailingTool:
    name = "dangerous"
    description = "test tool"
    capability = "allow_processes"

    def __init__(self):
        self.calls = 0

    def execute(self, arguments):
        self.calls += 1
        return Observation(False, "failed")

class SuccessfulTool:
    name = "safe"
    description = "test tool"
    capability = "allow_files"

    def execute(self, arguments):
        return Observation(True, "ok")

class AgentCoreTests(unittest.TestCase):
    def test_permission_is_enforced(self):
        registry = ToolRegistry(PermissionPolicy())
        registry.register(SuccessfulTool())
        result = registry.execute("safe", {})
        self.assertFalse(result["success"])
        self.assertIn("Permission denied", result["output"])


    def test_tool_description_is_available_to_model(self):
        registry = ToolRegistry(PermissionPolicy(allow_files=True))
        registry.register(SuccessfulTool())
        self.assertEqual(registry.describe()[0]["name"], "safe")

    def test_model_json_is_parsed_and_tool_context_is_sent(self):
        model = FakeModel(['[{"action":"run","tool":"safe","arguments":{"x":1}}]'])
        registry = ToolRegistry(PermissionPolicy(allow_files=True))
        registry.register(SuccessfulTool())
        controller = AgentController(model, registry, max_steps=2)
        steps = controller.plan(Goal("test"))
        self.assertEqual(steps[0].tool, "safe")
        self.assertEqual(steps[0].arguments["x"], 1)
        self.assertIn("Available tools", model.prompts[0])
\n    def test_learning_is_persisted(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = LearningStore(str(Path(tmp) / "learning.json"))
            store.record_task("demo", "completed", "ok")
            self.assertEqual(store.recent_tasks()[0]["goal"], "demo")

    def test_bounded_self_correction_stops(self):
        model = FakeModel(['{"action":"retry","tool":"safe","arguments":{}}'])
        correction = SelfCorrection(model, RetryPolicy(max_attempts=1))
        self.assertIsNone(correction.next_instruction("goal", "failure", 1))

    def test_failed_tool_can_be_corrected(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = LearningStore(str(Path(tmp) / "learning.json"))
            registry = ToolRegistry(PermissionPolicy(allow_files=True, allow_processes=True))
            registry.register(FailingTool())
            registry.register(SuccessfulTool())
            model = FakeModel([
                '[{"action":"run","tool":"dangerous","arguments":{}}]',
                '{"action":"fallback","tool":"safe","arguments":{}}'
            ])
            correction = SelfCorrection(model, RetryPolicy(max_attempts=3))
            controller = AgentController(model, registry, store, correction, max_steps=4)
            result = controller.run(Goal("test correction"))
            self.assertEqual(result.status, "completed")
            self.assertGreaterEqual(len(result.observations), 2)

if __name__ == "__main__":
    unittest.main()
