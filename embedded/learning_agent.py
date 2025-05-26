import time
import random
from typing import Dict, Any
from atheris.core.agent_base import AgentBase
from atheris.core.context_manager import ContextManager
from atheris.core.persistence_manager import PersistenceManager
from atheris.core.core_events import event_bus

# Optional mock
from atheris.solana.rpc_connector import get_account_info, get_network_metrics

class LearningAgent(AgentBase):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.context = ContextManager()
        self.persistence = PersistenceManager()
        self.sources = config.get("sources", ["network", "governance", "wallets"])
        self.agent_name = "learning"

    def run(self):
        """
        Periodically collect data from all configured sources.
        """
        collected_data = {}

        if "network" in self.sources:
            net_data = self._fetch_network_metrics()
            collected_data["network"] = net_data

        if "governance" in self.sources:
            gov_data = self._fetch_governance_data()
            collected_data["governance"] = gov_data

        if "wallets" in self.sources:
            wallet_data = self._fetch_wallet_activity()
            collected_data["wallets"] = wallet_data

        # Store and emit
        self.persistence.save(self.agent_name, "latest", collected_data)
        self.persistence.append_log(self.agent_name, collected_data)

        event_bus.emit("new_block", {"agent": self.agent_name, "data": collected_data})

        print(f"[LearningAgent] Collected and saved new batch of data.")

    def _fetch_network_metrics(self) -> Dict[str, Any]:
        """Simulate fetching real-time Solana network metrics."""
        metrics = get_network_metrics()
        print("[LearningAgent] Fetched network metrics:", metrics)
        return metrics

    def _fetch_governance_data(self) -> Dict[str, Any]:
        """Mocked governance proposal/state data."""
        proposals = [
            {"id": "prop-123", "status": "voting", "votes": 342},
            {"id": "prop-124", "status": "draft", "author": "wallet789"}
        ]
        print("[LearningAgent] Fetched governance data:", proposals)
        return {"proposals": proposals, "timestamp": time.time()}

    def _fetch_wallet_activity(self) -> Dict[str, Any]:
        """Mocked wallet activity data."""
        wallet_actions = [
            {"wallet": "wallet123", "txs": random.randint(1, 20)},
            {"wallet": "wallet456", "txs": random.randint(0, 5)},
        ]
        print("[LearningAgent] Fetched wallet activity:", wallet_actions)
        return {"wallets": wallet_actions, "timestamp": time.time()}

    def status(self) -> Dict[str, Any]:
        """Extended status for monitoring."""
        base = super().status()
        base.update({"sources": self.sources})
        return base


# Standalone test
if __name__ == "__main__":
    config = {
        "interval": 5,
        "sources": ["network", "governance", "wallets"]
    }

    agent = LearningAgent(config)
    for _ in range(3):
        agent.run()
        time.sleep(agent.interval)
