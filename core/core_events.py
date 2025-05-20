from typing import Callable, Dict, List, Any
import time


# Define global event catalog
EVENT_TYPES = {
    "proposal_created": "Triggered when a new DAO proposal is submitted",
    "proposal_updated": "When proposal metadata or state changes",
    "vote_cast": "When a wallet casts a vote",
    "validator_changed": "Validator performance or role changed",
    "token_moved": "Significant token movement detected",
    "new_block": "New Solana block observed",
    "wallet_active": "A monitored wallet becomes active",
    "alert_triggered": "Any alert condition is met",
    "agent_error": "An agent failed or raised an exception",
}


class EventBus:
    def __init__(self):
        """
        Initializes a pub-sub style event system.
        """
        self.subscribers: Dict[str, List[Callable[[Dict], None]]] = {}

    def subscribe(self, event_type: str, handler: Callable[[Dict], None]):
        """
        Subscribe a handler to a specific event type.

        Args:
            event_type (str): The event to listen for
            handler (callable): A function that takes a payload dict
        """
        if event_type not in EVENT_TYPES:
            raise ValueError(f"Unknown event type: {event_type}")

        if event_type not in self.subscribers:
            self.subscribers[event_type] = []

        self.subscribers[event_type].append(handler)
        print(f"[EventBus] Subscribed to '{event_type}'")

    def emit(self, event_type: str, payload: Dict[str, Any]):
        """
        Emit an event and notify all subscribed handlers.

        Args:
            event_type (str): The type of event to fire
            payload (dict): Event-specific data
        """
        if event_type not in EVENT_TYPES:
            raise ValueError(f"Unknown event type: {event_type}")

        print(f"[EventBus] Emitting event '{event_type}' with payload: {payload}")

        for handler in self.subscribers.get(event_type, []):
            try:
                handler(payload)
            except Exception as e:
                print(f"[EventBus] Error in handler for '{event_type}': {e}")


# Global instance to be shared
event_bus = EventBus()


# Example: simulate an agent reacting to vote_cast
def vote_logger(payload: Dict[str, Any]):
    print(f"[VoteLogger] Vote detected: {payload}")


def alert_bot(payload: Dict[str, Any]):
    print(f"[AlertBot] Alert triggered at {payload.get('timestamp')} for {payload.get('type')}")


# Run mock example
if __name__ == "__main__":
    event_bus.subscribe("vote_cast", vote_logger)
    event_bus.subscribe("alert_triggered", alert_bot)

    event_bus.emit("vote_cast", {"voter": "wallet123", "proposal": "prop-007", "choice": "yes"})
    event_bus.emit("alert_triggered", {"timestamp": time.time(), "type": "governance"})
