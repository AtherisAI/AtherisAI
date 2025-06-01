import time
from typing import Dict, Any, List
from atheris.core.agent_base import AgentBase
from atheris.core.persistence_manager import PersistenceManager


class ContributorHelper(AgentBase):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.agent_name = "contributor_helper"
        self.persistence = PersistenceManager()

    def run(self):
        print("[ContributorHelper] Ready to assist contributors.")

    def suggest_actions(self, wallet: str) -> List[str]:
        profile = self._get_profile(wallet)
        if not profile:
            return ["No contributor profile found. Please register your identity first."]

        suggestions = []
        proposals = self._get_active_proposals()
        last_active = profile.get("last_active", 0)
        now = time.time()

        # Suggest reviewing active proposals
        if proposals:
            suggestions.append(f"Review {len(proposals)} active proposals before the next vote window.")

        # Activity reminders
        if now - last_active > 3 * 86400:
            suggestions.append("You've been inactive for a few days. Consider checking into the contributor board.")

        # Contribution-based recommendations
        if profile["contributions"] < 3:
            suggestions.append("Complete an onboarding task to increase your trust score.")

        return suggestions

    def _get_profile(self, wallet: str) -> Dict[str, Any]:
        identities = self.persistence.load("identity_interface", "profiles") or {}
        return identities.get(wallet)

    def _get_active_proposals(self) -> List[Dict[str, Any]]:
        proposals = self.persistence.load("governance_tracker", "latest") or {}
        return [p for p in proposals.values() if p.get("status") == "voting"]

    def status(self):
        base = super().status()
        base.update({"mode": "on_demand"})
        return base


# Example usage
if __name__ == "__main__":
    helper = ContributorHelper({})
    helper.run()

    wallet = "9xL1WLmR...FKE"
    print(f"=== Suggestions for {wallet} ===")
    for s in helper.suggest_actions(wallet):
        print("-", s)
