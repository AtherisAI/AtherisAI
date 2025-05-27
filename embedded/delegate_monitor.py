import time
from typing import Dict, Any
from atheris.core.agent_base import AgentBase
from atheris.core.persistence_manager import PersistenceManager
from atheris.core.core_events import event_bus
from atheris.solana.rpc_connector import get_validator_list


class DelegateMonitor(AgentBase):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.agent_name = "delegate_monitor"
        self.persistence = PersistenceManager()
        self.last_snapshot = {}

    def run(self):
        print("[DelegateMonitor] Fetching validator state...")
        validators = get_validator_list()
        if not validators:
            print("[DelegateMonitor] No validator data retrieved.")
            return

        changes = []
        for v in validators:
            key = v["identity"]
            last = self.last_snapshot.get(key, {})
            now_score = v.get("score", 0)
            last_score = last.get("score", now_score)

            score_drop = now_score < last_score * 0.8
            vote_diff = v.get("votes", 0) - last.get("votes", 0)

            if score_drop:
                changes.append({"validator": key, "drop_detected": True})
                event_bus.emit("validator_changed", {
                    "identity": key,
                    "drop_detected": True,
                    "old_score": last_score,
                    "new_score": now_score,
                    "timestamp": time.time()
                })

            self.last_snapshot[key] = v

        self.persistence.save(self.agent_name, "latest", self.last_snapshot)
        self.persistence.append_log(self.agent_name, {
            "timestamp": time.time(),
            "validators_checked": len(validators),
            "score_drops": len(changes)
        })

        print(f"[DelegateMonitor] Checked {len(validators)} validators. Drops detected: {len(changes)}")

    def status(self) -> Dict[str, Any]:
        base = super().status()
        base.update({"tracked_validators": len(self.last_snapshot)})
        return base


# Example run
if __name__ == "__main__":
    config = {
        "interval": 8
    }

    agent = DelegateMonitor(config)
    for _ in range(3):
        agent.run()
        time.sleep(agent.interval)
