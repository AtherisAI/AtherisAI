import unittest
from typing import List, Dict


# === Mock Agent Classes for Full Stack Simulation ===

class LearningAgent:
    def collect(self) -> Dict:
        print("[LearningAgent] Collecting data...")
        return {"data": "raw sentiment data"}

class AnalyticalAgent:
    def analyze(self, data: Dict) -> Dict:
        print("[AnalyticalAgent] Analyzing data...")
        return {"analysis": "positive sentiment"}

class OutputAgent:
    def generate(self, analysis: Dict) -> str:
        print("[OutputAgent] Generating output...")
        return f"Sentiment result: {analysis['analysis']}"

class ResponderAgent:
    def respond(self, event: str) -> str:
        print(f"[ResponderAgent] Reacting to {event}")
        return f"Responder triggered by {event}"

class ChatBotAgent:
    def interact(self, query: str) -> str:
        print(f"[ChatBotAgent] Received query: {query}")
        return f"Answering: {query}"


# === End-to-End Test Class ===

class TestEndToEndPipeline(unittest.TestCase):

    def setUp(self):
        self.learning = LearningAgent()
        self.analytical = AnalyticalAgent()
        self.output = OutputAgent()
        self.responder = ResponderAgent()
        self.chatbot = ChatBotAgent()

    def test_data_pipeline(self):
        raw = self.learning.collect()
        analysis = self.analytical.analyze(raw)
        result = self.output.generate(analysis)
        self.assertEqual(result, "Sentiment result: positive sentiment")

    def test_event_response(self):
        response = self.responder.respond("new transaction")
        self.assertIn("Responder triggered", response)

    def test_chatbot_interface(self):
        reply = self.chatbot.interact("What is the sentiment today?")
        self.assertIn("Answering", reply)

    def test_multiple_agents_flow(self):
        for _ in range(3):
            raw = self.learning.collect()
            analysis = self.analytical.analyze(raw)
            result = self.output.generate(analysis)
            self.assertTrue(result.startswith("Sentiment result"))

    def tearDown(self):
        print("[TestEndToEndPipeline] Test complete.")


if __name__ == "__main__":
    unittest.main()
