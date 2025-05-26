import time
from typing import Dict, Any
from atheris.core.agent_base import AgentBase
from atheris.core.persistence_manager import PersistenceManager
from atheris.core.core_events import event_bus
from atheris.solana.rpc_connector import (
    get_latest_block,
    get_validator_list,
    get_governance_accounts,
    get_recent_transactions
)


class SolanaIndexer(AgentBase):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.agent_name = "indexer"
        self.persistence = PersistenceManager()
        self.last_slot_checked = config.get("start_slot", 0)

    def run(self):
        """Main loop to pull and store recent on-chain data from Solana."""
        print("[SolanaIndexer] Pulling on-chain Solana data...")

        latest_block = get_latest_block()
        slot = latest_block.get("slot", 0)

        if slot <= self.last_slot_checked:
            print(f"[SolanaIndexer] No new slots since {self.last_slot_checked}.")
            return

        validators = get_validator_list()
        governance_accounts = get_governance_accounts()
        transactions = get_recent_transactions(slot)

        indexed_data = {
            "slot": slot,
            "validators": validators,
            "governance_accounts": governance_accounts,
            "transactions": transactions,
            "timestamp": time.time()
        }

        self.persistence.save(self.agent_name, "latest", indexed_data)
        self.persistence.append_log(self.agent_name, indexed_data)

        self.last_slot_checked = slot

        # Emit an event for pipeline or alert bots
        event_bus.emit("new_block", {
            "slot": slot,
            "tx_count": len(transactions),
            "validators": len(validators),
            "governance_accounts": len(governance_accounts)
        })

        print(f"[SolanaIndexer] Indexed slot {slot} with {len(transactions)} transactions.")

    def status(self) -> Dict[str, Any]:
        base = super().status()
        base.update({"last_slot_checked": self.last_slot_checked})
        return base


# Example run
if __name__ == "__main__":
    config = {
        "interval": 6,
        "start_slot": 100000
    }

    agent = SolanaIndexer(config)
    for _ in range(3):
        agent.run()
        time.sleep(agent.interval)
