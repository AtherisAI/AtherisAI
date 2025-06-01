import time
from typing import Dict, Any, List
from atheris.core.agent_base import AgentBase
from atheris.core.persistence_manager import PersistenceManager


class GovernanceAssistant(AgentBase):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.agent_name = "governance_assistant"
        self.persistence = PersistenceManager()

    def run(self):
        """No scheduled operation — works on demand via query()."""
        print("[GovernanceAssistant] Standing by for delegate queries.")

    def list_active_proposals(self) -> List[str]:
        """Returns a list of all active proposals with summaries."""
        proposals = self._get_proposals()
        summaries = []
        for p in proposals:
            if p.get("status") == "voting":
                summaries.append(self._summarize_proposal(p))
        return summaries

    def get_guidance(self, proposal_id: str) -> str:
        """Returns basic vote recommendation logic (placeholder AI model)."""
        proposals = self._get_proposals()
        match = next((p for p in proposals if p["id"] == proposal_id), None)
        if not match:
            return f"Proposal {proposal_id} not found."

        if match.get("votes_for", 0) > match.get("votes_against", 0):
            return f"🗳 Current majority is FOR on proposal {proposal_id}. Consider aligning if you agree."
        else:
            return f"🗳 Proposal {proposal_id} may be contentious. Review the details carefully."

    def _summarize_proposal(self, proposal: Dict[str, Any]) -> str:
        """Generate a simple summary string for a proposal."""
        return (
            f"📄 Proposal {proposal['id']} by {proposal.get('author', 'unknown')} "
            f"is currently in '{proposal.get('status')}' phase. "
            f"Votes: ✅ {proposal.get('votes_for', 0)} / ❌ {proposal.get('votes_against', 0)}"
        )

    def _get_proposals(self) -> List[Dict[str, Any]]:
        """Load proposal data from GovernanceTracker logs."""
        snapshot = self.persistence.load("governance_tracker", "latest")
        return list(snapshot.values()) if snapshot else []

    def status(self):
        base = super().status()
        base.update({
            "mode": "on_demand",
            "supported_queries": ["list_active_proposals", "get_guidance"]
        })
        return base


# Example test
if __name__ == "__main__":
    agent = GovernanceAssistant({})
    agent.run()

    print("=== Active Proposals ===")
    for summary in agent.list_active_proposals():
        print("-", summary)

    print("\n=== Guidance ===")
    print(agent.get_guidance("prop-123"))
