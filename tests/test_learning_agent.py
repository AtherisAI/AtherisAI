import unittest
from unittest.mock import patch, MagicMock
import time

# Simulated LearningAgent for test purposes
class LearningAgent:
    def __init__(self, data_sources):
        self.data_sources = data_sources
        self.collected_data = []
        self.active = False

    def start(self):
        self.active = True
        print("[LearningAgent] Started collecting data")

    def stop(self):
        self.active = False
        print("[LearningAgent] Stopped")

    def collect(self):
        if not self.active:
            return
        for source in self.data_sources:
            data = source.fetch()
            if data:
                self.collected_data.append(data)
                print(f"[LearningAgent] Collected data: {data}")

    def status(self):
        return {
            "active": self.active,
            "data_points": len(self.collected_data)
        }


# Fake data source for mocking
class FakeSource:
    def __init__(self, name, payload):
        self.name = name
        self.payload = payload

    def fetch(self):
        return {"source": self.name, "payload": self.payload}


class TestLearningAgent(unittest.TestCase):

    def setUp(self):
        source1 = FakeSource("onchain", {"txs": 25})
        source2 = FakeSource("offchain", {"tweets": 10})
        self.agent = LearningAgent([source1, source2])

    def test_start_and_stop(self):
        self.agent.start()
        self.assertTrue(self.agent.active)
        self.agent.stop()
        self.assertFalse(self.agent.active)

    def test_collect_data(self):
        self.agent.start()
        self.agent.collect()
        self.assertEqual(len(self.agent.collected_data), 2)

    def test_status_report(self):
        self.agent.start()
        self.agent.collect()
        status = self.agent.status()
        self.assertTrue(status["active"])
        self.assertEqual(status["data_points"], 2)

    def test_no_collection_when_inactive(self):
        self.agent.collect()
        self.assertEqual(len(self.agent.collected_data), 0)

    def test_multiple_collections(self):
        self.agent.start()
        self.agent.collect()
        self.agent.collect()
        self.assertEqual(len(self.agent.collected_data), 4)

    def tearDown(self):
        self.agent.stop()


if __name__ == "__main__":
    unittest.main()
