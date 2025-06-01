import time
from typing import Dict, Any, Optional
from atheris.core.agent_base import AgentBase
from atheris.core.persistence_manager import PersistenceManager


class IdentityInterface(AgentBase):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.agent_name = "identity_interface"
        self.persistence = PersistenceManager()
        self.identities: Dict[str, Dict[str, Any]] = self.persistence.load(self.agent_name, "profiles") or {}

    def run(self):
        """Identity resolution is on-demand."""
        print("[IdentityInterface] Loaded", len(self.identities), "identities.")

    def register(self, wallet: str, alias: Optional[str] = None):
        if wallet in self.identities:
            print(f"[IdentityInterface] Wallet {wallet} already registered.")
            return

        self.identities[wallet] = {
            "alias": alias or f"user_{wallet[:5]}",
            "contributions": 0,
            "trust_score": 0.5,
            "last_active": time.time()
        }
        self._save()
        print(f"[IdentityInterface] Registered identity: {wallet} as {self.identities[wallet]['alias']}")

    def record_contribution(self, wallet: str):
        if wallet not in self.identities:
            self.register(wallet)
        self.identities[wallet]["contributions"] += 1
        self.identities[wallet]["last_active"] = time.time()
        self._update_trust(wallet)
        self._save()
        print(f"[IdentityInterface] Contribution recorded for {wallet}")

    def _update_trust(self, wallet: str):
        contribs = self.identities[wallet]["contributions"]
        self.identities[wallet]["trust_score"] = min(1.0, 0.4 + (contribs * 0.05))

    def resolve(self, wallet: str) -> str:
        profile = self.identities.get(wallet)
        if profile:
            return f"{profile['alias']} (trust: {round(profile['trust_score'], 2)})"
        return "Unknown contributor"

    def list_identities(self) -> Dict[str, Any]:
        return self.identities

    def _save(self):
        self.persistence.save(self.agent_name, "profiles", self.identities)

    def status(self):
        base = super().status()
        base.update({"identities_tracked": len(self.identities)})
        return base


# Example usage
if __name__ == "__main__":
    agent = IdentityInterface({})
    agent.run()

    agent.register("9xL1WLmR...FKE", "dev_alex")
    agent.record_contribution("9xL1WLmR...FKE")

    print("=== Identity Resolution ===")
    print(agent.resolve("9xL1WLmR...FKE"))
