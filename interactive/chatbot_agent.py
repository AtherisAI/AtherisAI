import time
from typing import Dict, Any
from atheris.core.agent_base import AgentBase
from atheris.core.persistence_manager import PersistenceManager
from atheris.core.context_manager import ContextManager


class ChatBotAgent(AgentBase):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.agent_name = "chatbot"
        self.context = ContextManager()
        self.persistence = PersistenceManager()
        self.routes = {
            "governance": self._handle_governance_query,
            "network": self._handle_network_query,
            "wallet": self._handle_wallet_query
        }

    def run(self):
        """ChatBotAgent does not require scheduled polling."""
        print("[ChatBotAgent] Ready for natural language queries.")

    def query(self, text: str) -> str:
        """Process a natural language query and return a response."""
        print(f"[ChatBotAgent] Received query: {text}")

        category = self._classify_query(text)

        if category in self.routes:
            return self.routes[category](text)
        else:
            return "I'm not sure how to answer that yet. Try asking about governance, network, or wallets."

    def _classify_query(self, text: str) -> str:
        """Very basic keyword classifier (placeholder for NLP model)."""
        text_lower = text.lower()
        if any(k in text_lower for k in ["proposal", "vote", "governance"]):
            return "governance"
        if any(k in text_lower for k in ["network", "slot", "solana"]):
            return "network"
        if any(k in text_lower for k in ["wallet", "activity", "address"]):
            return "wallet"
        return "unknown"

    def _handle_governance_query(self, text: str) -> str:
        """Return information about proposals or voting."""
        data = self.persistence.load("governance_tracker", "latest")
        if not data:
            return "I don't have current governance data available."
        active = [p for p in data.values() if p.get("status") == "voting"]
        return f"There are currently {len(active)} active proposals on-chain."

    def _handle_network_query(self, text: str) -> str:
        """Return Solana network context."""
        ctx = self.context.snapshot()
        net = ctx.get("solana_block", {})
        return f"The current Solana slot is {net.get('slot', 'unknown')} and the network appears {ctx.get('global_status', {}).get('network_health', 'unknown')}."

    def _handle_wallet_query(self, text: str) -> str:
        """Return wallet activity insights."""
        data = self.persistence.load("wallet_tracker", "snapshot")
        if not data:
            return "No recent wallet activity detected."
        active_wallets = [w for w, info in data.items() if info.get("spike")]
        return f"{len(active_wallets)} wallets have shown unusually high activity."

    def status(self):
        base = super().status()
        base.update({"mode": "interactive", "query_routes": list(self.routes.keys())})
        return base


# Example run
if __name__ == "__main__":
    agent = ChatBotAgent({})
    agent.run()

    queries = [
        "How many active proposals are there?",
        "What is the current Solana slot?",
        "Which wallets have high activity?",
        "Tell me about validators."
    ]

    for q in queries:
        print("Q:", q)
        print("A:", agent.query(q))
        print("---")
        time.sleep(1)
