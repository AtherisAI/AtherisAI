import time
import random
from typing import Dict, Any
from atheris.core.agent_base import AgentBase
from atheris.core.persistence_manager import PersistenceManager
from atheris.core.core_events import event_bus
from atheris.solana.rpc_connector import get_protocol_traffic


class NetworkTrafficAgent(AgentBase):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.agent_name = "traffic_monitor"
        self.persistence = PersistenceManager()
        self.history: Dict[str, list] = {}

    def run(self):
        print("[NetworkTrafficAgent] Fetching current protocol activity...")
        traffic_data = get_protocol_traffic()

        if not traffic_data:
            print("[NetworkTrafficAgent] No traffic data returned.")
            return

        anomalies = []
        for program_id, tx_count in traffic_data.items():
            history = self.history.get(program_id, [])
            history.append(tx_count)
            if len(history) > 10:
                history.pop(0)

            avg = sum(history) / len(history) if history else 0
            spike = tx_count > avg * 2

            if spike:
                anomalies.append(program_id)
                event_bus.emit("alert_triggered", {
                    "type": "traffic_spike",
                    "program_id": program_id,
                    "tx_count": tx_count,
                    "average": round(avg, 2),
                    "timestamp": time.time()
                })

            self.history[program_id] = history

        self.persistence.save(self.agent_name, "traffic", self.history)
        self.persistence.append_log(self.agent_name, {
            "timestamp": time.time(),
            "programs_tracked": len(traffic_data),
            "anomalies": len(anomalies)
        })

        print(f"[NetworkTrafficAgent] Monitored {len(traffic_data)} programs. Anomalies: {anomalies}")

    def status(self) -> Dict[str, Any]:
        base = super().status()
        base.update({
            "programs_monitored": len(self.history)
        })
        return base


# Example mock test
if __name__ == "__main__":
    config = {
        "interval": 5
    }

    agent = NetworkTrafficAgent(config)
    for _ in range(3):
        agent.run()
        time.sleep(agent.interval)
