import time
from typing import Dict, Any
from atheris.core.agent_base import AgentBase
from atheris.core.persistence_manager import PersistenceManager
from atheris.core.core_events import event_bus

class OutputAgent(AgentBase):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.agent_name = "output"
        self.persistence = PersistenceManager()

    def run(self):
        """Generate final outputs from processed analytical results."""
        analysis = self.persistence.load("analysis", "latest")
        if not analysis:
            print("[OutputAgent] No analysis data available.")
            return

        output = {
            "summary": self._generate_summary(analysis),
            "timestamp": time.time()
        }

        # Save and emit
        self.persistence.save(self.agent_name, "latest", output)
        self.persistence.append_log(self.agent_name, output)

        event_bus.emit("alert_triggered", {
            "type": "output_ready",
            "payload": output
        })

        print("[OutputAgent] Output generated and stored.")

    def _generate_summary(self, analysis: Dict[str, Any]) -> Dict[str, str]:
        """Format a human-readable summary for dashboards or governance bots."""
        summary = {}

        net = analysis.get("network", {})
        gov = analysis.get("governance", {})
        wallets = analysis.get("wallets", {})

        summary["network_status"] = f"Network is {net.get('network_health', 'unknown')}."
        summary["governance_engagement"] = f"There are {gov.get('active_proposals', 0)} active proposals."
        summary["wallet_spike"] = "Wallet activity spike detected." if wallets.get("spike_detected") else "No wallet anomalies."

        return summary

    def status(self) -> Dict[str, Any]:
        base = super().status()
        base.update({"last_output": time.time()})
        return base


# Standalone test
if __name__ == "__main__":
    agent = OutputAgent({"interval": 7})
    for _ in range(3):
        agent.run()
        time.sleep(agent.interval)
