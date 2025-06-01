import time
from typing import Dict, Callable
from atheris.core.agent_base import AgentBase
from atheris.core.core_events import event_bus
from atheris.core.persistence_manager import PersistenceManager


class ResponderAgent(AgentBase):
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.agent_name = "responder"
        self.persistence = PersistenceManager()
        self.response_map: Dict[str, Callable] = {
            "proposal_created": self._handle_proposal_created,
            "wallet_active": self._handle_wallet_activity,
            "traffic_spike": self._handle_traffic_spike
        }
        self._subscribe_to_events()

    def _subscribe_to_events(self):
        for event_name in self.response_map:
            event_bus.subscribe(event_name, self._create_handler(event_name))
        print(f"[ResponderAgent] Subscribed to events: {list(self.response_map.keys())}")

    def _create_handler(self, event_name: str):
        def handler(payload: Dict):
            print(f"[ResponderAgent] Event '{event_name}' received.")
            self.response_map[event_name](payload)
        return handler

    def _handle_proposal_created(self, payload: Dict):
        summary = f"🗳 New Proposal Detected: {payload['id']} by {payload.get('author', 'unknown')}"
        self._log_response("proposal", summary)

    def _handle_wallet_activity(self, payload: Dict):
        summary = f"⚠️ Wallet {payload['wallet']} showed abnormal activity: {payload['tx_count']} txs"
        self._log_response("wallet", summary)

    def _handle_traffic_spike(self, payload: Dict):
        summary = f"🚨 High activity on program {payload['program_id']} — {payload['tx_count']} txs (avg: {payload['average']})"
        self._log_response("traffic", summary)

    def _log_response(self, tag: str, message: str):
        print(f"[ResponderAgent] RESPONSE: {message}")
        self.persistence.append_log(self.agent_name, {
            "timestamp": time.time(),
            "tag": tag,
            "message": message
        })

    def run(self):
        """ResponderAgent is fully event-driven — no polling logic needed."""
        print("[ResponderAgent] Waiting for events...")

    def status(self):
        base = super().status()
        base.update({"mode": "event-driven", "subscriptions": list(self.response_map.keys())})
        return base


# Example standalone simulation
if __name__ == "__main__":
    import time

    agent = ResponderAgent()
    agent.run()

    # Simulate test event
    event_bus.emit("proposal_created", {"id": "prop-900", "author": "walletXYZ"})
    time.sleep(1)
    event_bus.emit("wallet_active", {"wallet": "wallet123", "tx_count": 35})
    time.sleep(1)
    event_bus.emit("traffic_spike", {"program_id": "XYZProgram", "tx_count": 1000, "average": 420})
