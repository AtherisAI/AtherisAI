import time
import random
from typing import Dict, Any
from atheris.core.agent_base import AgentBase
from atheris.core.persistence_manager import PersistenceManager
from atheris.core.core_events import event_bus
from atheris.solana.rpc_connector import get_wallet_activity


class WalletActivityAgent(AgentBase):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.agent_name = "wallet_tracker"
        self.persistence = PersistenceManager()
        self.snapshot: Dict[str, Any] = {}

    def run(self):
        print("[WalletActivityAgent] Tracking wallet activity...")
        data = get_wallet_activity()

        if not data:
            print("[WalletActivityAgent] No wallet activity returned.")
            return

        alerts = []
        for wallet in data:
            wallet_id = wallet["wallet"]
            tx_count = wallet["txs"]
            history = self.snapshot.get(wallet_id, {"tx_history": [], "spike": False})

            history["tx_history"].append(tx_count)
            if len(history["tx_history"]) > 10:
                history["tx_history"].pop(0)

            avg = sum(history["tx_history"]) / len(history["tx_history"])
            spike = tx_count > avg * 2

            if spike and not history.get("spike"):
                alerts.append(wallet_id)
                event_bus.emit("wallet_active", {
                    "wallet": wallet_id,
                    "tx_count": tx_count,
                    "avg": avg,
                    "spike": True,
                    "timestamp": time.time()
                })

            history["spike"] = spike
            self.snapshot[wallet_id] = history

        # Store results
        self.persistence.save(self.agent_name, "snapshot", self.snapshot)
        self.persistence.append_log(self.agent_name, {
            "timestamp": time.time(),
            "wallets_analyzed": len(data),
            "spikes_detected": len(alerts)
        })

        print(f"[WalletActivityAgent] Analyzed {len(data)} wallets. Spikes: {alerts}")

    def status(self) -> Dict[str, Any]:
        base = super().status()
        base.update({
            "wallets_tracked": len(self.snapshot)
        })
        return base


# Example test
if __name__ == "__main__":
    config = {
        "interval": 5
    }

    agent = WalletActivityAgent(config)
    for _ in range(3):
        agent.run()
        time.sleep(agent.interval)
