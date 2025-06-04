import unittest
from unittest.mock import MagicMock, patch
from typing import List
import time

# Simulated MasterAgent for testing
class MasterAgent:
    def __init__(self):
        self.running = False
        self.agents: List[str] = []

    def register_agent(self, agent_name: str):
        self.agents.append(agent_name)
        print(f"[MasterAgent] Registered agent: {agent_name}")

    def start(self):
        self.running = True
        print("[MasterAgent] Started")

    def stop(self):
        self.running = False
        print("[MasterAgent] Stopped")

    def status(self):
        return {"running": self.running, "agent_count": len(self.agents)}


class TestMasterAgent(unittest.TestCase):

    def setUp(self):
        self.master = MasterAgent()

    def test_register_agent(self):
        self.master.register_agent("learning_agent")
        self.master.register_agent("output_agent")
        self.assertIn("learning_agent", self.master.agents)
        self.assertIn("output_agent", self.master.agents)
        self.assertEqual(len(self.master.agents), 2)

    def test_start_and_stop(self):
        self.assertFalse(self.master.running)
        self.master.start()
        self.assertTrue(self.master.running)
        self.master.stop()
        self.assertFalse(self.master.running)

    def test_status(self):
        self.master.register_agent("responder_agent")
        self.master.start()
        status = self.master.status()
        self.assertTrue(status["running"])
        self.assertEqual(status["agent_count"], 1)

    def test_double_start(self):
        self.master.start()
        self.master.start()
        self.assertTrue(self.master.running)

    def test_register_multiple_agents(self):
        for i in range(5):
            self.master.register_agent(f"agent_{i}")
        self.assertEqual(len(self.master.agents), 5)

    def test_stop_without_start(self):
        self.master.stop()
        self.assertFalse(self.master.running)

    def test_empty_status(self):
        status = self.master.status()
        self.assertFalse(status["running"])
        self.assertEqual(status["agent_count"], 0)

    def tearDown(self):
        self.master.stop()


if __name__ == "__main__":
    unittest.main()
