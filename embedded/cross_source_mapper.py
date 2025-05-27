import time
import random
from typing import Dict, Any, List
from atheris.core.agent_base import AgentBase
from atheris.core.persistence_manager import PersistenceManager
from atheris.core.core_events import event_bus

# Mock database of off-chain identity mappings
MOCK_IDENTITY_DB = {
    "wallet123": {"username": "@daoqueen", "platform": "Discord"},
    "wallet456": {"username": "@solanadev", "platform": "Twitter"},
    "wallet789": {"username": "@modbot", "platform": "Discourse"}
}

class CrossSourceMapper(AgentBase):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.agent_name = "cross_mapper"
        self.persistence = PersistenceManager()
        self.identity_map: Dict[str, Any] = {}

    def run(self):
        print("[CrossSourceMapper] Linking wallets to off-chain identities...")
        wallets = self._get_wallets_from_activity()

        for w in wallets:
            if w in self.identity_map:
                continue

            profile = self._resolve_identity(w)
            if profile:
                self.identity_map[w] = profile
                event_bus.emit("alert_triggered", {
                    "type": "identity_linked",
                    "wallet": w,
                    "profile": profile,
                    "timestamp": time.time()
                })

        self.persistence.save(self.agent_name, "map", self.identity_map)
        self.persistence.append_log(self.agent_name, {
            "timestamp": time.time(),
            "linked_wallets": len(self.identity_map)
        })

        print(f"[CrossSourceMapper] Linked {len(self.identity_map)} wallet identities.")

    def _get_wallets_from_activity(self) -> List[str]:
        """Mock: pull recent wallets from other modules (normally from wallet activity logs)."""
        return ["wallet123", "wallet456", "wallet789", "wallet999"]

    def _resolve_identity(self, wallet: str) -> Dict[str, str]:
        """Resolve wallet to an off-chain identity (mocked)."""
        if wallet in MOCK_IDENTITY_DB:
            return MOCK_IDENTITY_DB[wallet]
        return {"username": f"anon_{wallet[-4:]}", "platform": "unknown"}

    def status(self) -> Dict[str, Any]:
        base = super().status()
        base.update({"resolved_links": len(self.identity_map)})
        return base


# Example test
if __name__ == "__main__":
    config = {
        "interval": 6
    }

    agent = CrossSourceMapper(config)
    for _ in range(3):
        agent.run()
        time.sleep(agent.interval)
