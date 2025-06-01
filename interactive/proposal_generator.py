import time
import random
from typing import Dict, Any, List
from atheris.core.agent_base import AgentBase
from atheris.core.persistence_manager import PersistenceManager


class ProposalGenerator(AgentBase):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.agent_name = "proposal_generator"
        self.persistence = PersistenceManager()

    def run(self):
        print("[ProposalGenerator] Generating a batch of potential proposals...")
        candidates = self._generate_drafts()
        self.persistence.save(self.agent_name, "drafts", candidates)
        print(f"[ProposalGenerator] Generated {len(candidates)} proposal drafts.")

    def _generate_drafts(self) -> List[Dict[str, Any]]:
        """Generate synthetic proposal drafts based on synthetic patterns."""
        ideas = [
            ("Fund new contributor onboarding", "Allocate SOL to support onboarding coordinators."),
            ("Expand validator incentives", "Increase yield or score bonuses for small validators."),
            ("Automate budget reallocation", "Propose agent-based treasury flow automation."),
            ("Mandate agent review cycles", "Ensure AI agents are audited every quarter."),
            ("Standardize governance metrics", "Define a shared metrics dashboard across DAOs.")
        ]

        drafts = []
        for i, (title, description) in enumerate(ideas):
            draft = {
                "id": f"draft-{int(time.time())}-{i}",
                "title": title,
                "description": description,
                "rationale": self._generate_rationale(title),
                "expected_impact": self._estimate_impact(title),
                "status": "draft"
            }
            drafts.append(draft)
        return drafts

    def _generate_rationale(self, title: str) -> str:
        """Create rationale for the proposal."""
        return f"This proposal addresses a recurring need observed in recent governance cycles related to: {title.lower()}."

    def _estimate_impact(self, title: str) -> str:
        """Estimate the proposal's effect."""
        impacts = {
            "onboarding": "Improves contributor retention by 20%",
            "validator": "Strengthens network decentralization",
            "budget": "Reduces manual overhead in treasury flows",
            "audit": "Increases agent trust and transparency",
            "metrics": "Enhances interoperability between DAOs"
        }

        for key, value in impacts.items():
            if key in title.lower():
                return value
        return "Improves governance efficiency"

    def list_drafts(self) -> List[str]:
        """Return a list of current drafts."""
        data = self.persistence.load(self.agent_name, "drafts")
        return [d["title"] for d in data] if data else []

    def status(self):
        base = super().status()
        base.update({"draft_count": len(self.list_drafts())})
        return base


# Example usage
if __name__ == "__main__":
    agent = ProposalGenerator({})
    agent.run()

    print("=== Proposal Drafts ===")
    for title in agent.list_drafts():
        print("-", title)
