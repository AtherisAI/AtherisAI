import time
import statistics
from typing import Dict, Any
from atheris.core.agent_base import AgentBase
from atheris.core.persistence_manager import PersistenceManager
from atheris.core.core_events import event_bus

class AnalyticalAgent(AgentBase):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.agent_name = "analysis"
        self.persistence = PersistenceManager()

    def run(self):
        """Main analytical cycle."""
        raw_data = self.persistence.load("learning", "latest")
        if not raw_data:
            print("[AnalyticalAgent] No data available from LearningAgent.")
            return

        analysis_result = {}

        if "network" in raw_data:
            net_insights = self._analyze_network(raw_data["network"])
            analysis_result["network"] = net_insights

        if "governance" in raw_data:
            gov_insights = self._analyze_governance(raw_data["governance"])
            analysis_result["governance"] = gov_insights

        if "wallets" in raw_data:
            wallet_insights = self._analyze_wallets(raw_data["wallets"])
            analysis_result["wallets"] = wallet_insights

        # Save and emit
        self.persistence.save(self.agent_name, "latest", analysis_result)
        self.persistence.append_log(self.agent_name, analysis_result)

        event_bus.emit("alert_triggered", {
            "type": "analysis_complete",
            "data": analysis_result,
            "timestamp": time.time()
        })

        print("[AnalyticalAgent] Analysis complete and stored.")

    def _analyze_network(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Solana network metrics (mocked for now)."""
        slot = data.get("slot", 0)
        return {
            "network_health": "stable" if slot % 2 == 0 else "volatile",
            "recommendation": "continue operations" if slot % 2 == 0 else "delay governance changes"
        }

    def _analyze_governance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate proposal statuses and voting behavior."""
        proposals = data.get("proposals", [])
        active = [p for p in proposals if p["status"] == "voting"]
        return {
            "active_proposals": len(active),
            "engagement_score": round(len(active) / max(1, len(proposals)), 2)
        }

    def _analyze_wallets(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify contributor patterns or suspicious activity."""
        wallets = data.get("wallets", [])
        tx_counts = [w["txs"] for w in wallets]
        mean_txs = statistics.mean(tx_counts) if tx_counts else 0
        spike_detected = any(tx > mean_txs * 2 for tx in tx_counts)
        return {
            "average_activity": round(mean_txs, 2),
            "spike_detected": spike_detected
        }

    def status(self) -> Dict[str, Any]:
        base = super().status()
        base.update({"last_analysis": time.time()})
        return base


# Standalone test
if __name__ == "__main__":
    agent = AnalyticalAgent({"interval": 6})
    for _ in range(3):
        agent.run()
        time.sleep(agent.interval)
