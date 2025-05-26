import time
from typing import Dict, Any
from atheris.core.agent_base import AgentBase
from atheris.core.persistence_manager import PersistenceManager
from atheris.core.core_events import event_bus
from atheris.solana.rpc_connector import get_governance_accounts


class GovernanceTracker(AgentBase):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.agent_name = "governance_tracker"
        self.persistence = PersistenceManager()
        self.last_snapshot = {}

    def run(self):
        """Main loop to check proposals and vote flows."""
        print("[GovernanceTracker] Checking DAO governance activity...")
        data = get_governance_accounts()

        if not data:
            print("[GovernanceTracker] No governance data retrieved.")
            return

        for prop in data:
            pid = prop["id"]
            current_status = prop.get("status", "unknown")

            # Check if this proposal was previously seen
            prev = self.last_snapshot.get(pid)
            if not prev:
                self._handle_new_proposal(prop)
            elif prev.get("status") != current_status:
                self._handle_status_change(prop, prev)

            self.last_snapshot[pid] = prop

        self.persistence.save(self.agent_name, "latest", self.last_snapshot)
        self.persistence.append_log(self.agent_name, {"updated": time.time(), "count": len(data)})

    def _handle_new_proposal(self, proposal: Dict[str, Any]):
        print(f"[GovernanceTracker] New proposal: {proposal['id']}")
        event_bus.emit("proposal_created", {
            "id": proposal["id"],
            "author": proposal.get("author", ""),
            "status": proposal.get("status"),
            "timestamp": time.time()
        })

    def _handle_status_change(self, proposal: Dict[str, Any], previous: Dict[str, Any]):
        print(f"[GovernanceTracker] Proposal {proposal['id']} changed status from {previous['status']} to {proposal['status']}")
        event_bus.emit("proposal_updated", {
            "id": proposal["id"],
            "old_status": previous["status"],
            "new_status": proposal["status"],
            "timestamp": time.time()
        })

    def status(self) -> Dict[str, Any]:
        base = super().status()
        base.update({
            "proposals_tracked": len(self.last_snapshot)
        })
        return base


# Example run
if __name__ == "__main__":
    config = {
        "interval": 10
    }

    agent = GovernanceTracker(config)
    for _ in range(3):
        agent.run()
        time.sleep(agent.interval)
