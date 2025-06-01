import time
from typing import Dict, Any, Tuple
from atheris.core.agent_base import AgentBase


class IntentClassifier(AgentBase):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.agent_name = "intent_classifier"

    def run(self):
        print("[IntentClassifier] Ready to classify incoming messages...")

    def classify(self, message: str) -> Tuple[str, str]:
        """
        Classify intent and return (intent_label, route_agent).

        Examples:
        - "I want to submit a proposal" -> ("proposal_submission", "proposal_generator")
        - "What’s the status of X?" -> ("inquiry", "chatbot_agent")
        - "Someone is spamming" -> ("moderation_alert", "moderation_relay")
        """
        lowered = message.lower()

        if "submit" in lowered or "proposal" in lowered:
            return "proposal_submission", "proposal_generator"
        if "status" in lowered or "update" in lowered:
            return "inquiry", "chatbot_agent"
        if "spam" in lowered or "abuse" in lowered:
            return "moderation_alert", "moderation_relay"
        if "assign" in lowered or "task" in lowered:
            return "task_request", "task_router"
        if "who am i" in lowered or "profile" in lowered:
            return "identity_query", "identity_interface"

        return "unknown", "chatbot_agent"

    def explain(self, message: str) -> str:
        """
        Explain how the intent was classified.
        """
        intent, agent = self.classify(message)
        return f"Intent: '{intent}' — Routed to: {agent}"

    def status(self):
        base = super().status()
        base.update({"mode": "real_time"})
        return base


# Example usage
if __name__ == "__main__":
    classifier = IntentClassifier({})
    classifier.run()

    messages = [
        "I want to submit a proposal about validator rewards",
        "What’s the status of the last vote?",
        "This person is spamming the group chat",
        "Assign this task to Alex",
        "Who am I in the DAO?"
    ]

    for msg in messages:
        print(f">> {msg}")
        print(" -", classifier.explain(msg))
