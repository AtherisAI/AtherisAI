from typing import Callable, Dict, List, Any
from threading import Lock

class MessageBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable[[Any], None]]] = {}
        self.lock = Lock()
        print("[MessageBus] Initialized.")

    def subscribe(self, topic: str, callback: Callable[[Any], None]):
        with self.lock:
            if topic not in self.subscribers:
                self.subscribers[topic] = []
            self.subscribers[topic].append(callback)
            print(f"[MessageBus] Subscribed to topic '{topic}'.")

    def unsubscribe(self, topic: str, callback: Callable[[Any], None]):
        with self.lock:
            if topic in self.subscribers:
                self.subscribers[topic] = [
                    cb for cb in self.subscribers[topic] if cb != callback
                ]
                print(f"[MessageBus] Unsubscribed from topic '{topic}'.")

    def publish(self, topic: str, message: Any):
        with self.lock:
            callbacks = self.subscribers.get(topic, []).copy()
        for callback in callbacks:
            try:
                callback(message)
                print(f"[MessageBus] Dispatched message to topic '{topic}'.")
            except Exception as e:
                print(f"[MessageBus] Error in callback for topic '{topic}': {e}")


# Example usage
if __name__ == "__main__":
    bus = MessageBus()

    def agent_handler(data):
        print(f"[AgentHandler] Received: {data}")

    def dashboard_handler(data):
        print(f"[DashboardHandler] Received: {data}")

    bus.subscribe("agent.update", agent_handler)
    bus.subscribe("dashboard.render", dashboard_handler)

    bus.publish("agent.update", {"type": "status", "value": "active"})
    bus.publish("dashboard.render", {"ui": "update", "content": "Agent view refreshed"})

    bus.unsubscribe("agent.update", agent_handler)
    bus.publish("agent.update", {"type": "status", "value": "inactive"})
