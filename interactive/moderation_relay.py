import time
from typing import Dict, Any, List
from atheris.core.agent_base import AgentBase
from atheris.core.persistence_manager import PersistenceManager


class ModerationRelay(AgentBase):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.agent_name = "moderation_relay"
        self.persistence = PersistenceManager()
        self.cases: List[Dict[str, Any]] = self.persistence.load(self.agent_name, "cases") or []

    def run(self):
        print("[ModerationRelay] Awaiting moderation reports...")

    def flag_event(self, source: str, reason: str, metadata: Dict[str, Any]):
        """Registers a moderation event and determines action."""
        case = {
            "id": f"case-{int(time.time())}",
            "source": source,
            "reason": reason,
            "metadata": metadata,
            "status": "pending",
            "created_at": time.time()
        }

        if self._is_false_positive(reason, metadata):
            case["status"] = "dismissed"
            print(f"[ModerationRelay] Dismissed false positive case from {source}.")
        else:
            case["status"] = "forwarded"
            self._route_to_agent(case)

        self.cases.append(case)
        self._save()

    def _is_false_positive(self, reason: str, metadata: Dict[str, Any]) -> bool:
        """Basic logic to detect invalid or spam reports."""
        return "test" in reason.lower() or metadata.get("severity", 0) < 1

    def _route_to_agent(self, case: Dict[str, Any]):
        """Forward valid case to response agent."""
        print(f"[ModerationRelay] Forwarding case {case['id']} to ResponderAgent for action.")
        # Placeholder — in production this would post a message or task

    def list_cases(self, status_filter: str = None) -> List[Dict[str, Any]]:
        """Returns all or filtered moderation cases."""
        if status_filter:
            return [c for c in self.cases if c["status"] == status_filter]
        return self.cases

    def _save(self):
        self.persistence.save(self.agent_name, "cases", self.cases)

    def status(self):
        base = super().status()
        base.update({"total_cases": len(self.cases)})
        return base


# Example usage
if __name__ == "__main__":
    relay = ModerationRelay({})
    relay.run()

    relay.flag_event(
        source="chat_channel_4",
        reason="spam detected",
        metadata={"message": "BUY NOW", "severity": 3, "wallet": "9xL..."}
    )

    print("=== Case List ===")
    for c in relay.list_cases():
        print("-", c)
