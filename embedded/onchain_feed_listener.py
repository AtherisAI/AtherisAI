import asyncio
import json
import time
from typing import Dict, Any, List
from solana.rpc.async_api import AsyncClient
from solana.publickey import PublicKey
from atheris.core.agent_base import AgentBase
from atheris.core.persistence_manager import PersistenceManager


class OnchainFeedListener(AgentBase):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.agent_name = "onchain_feed_listener"
        self.rpc_url = config.get("rpc_url", "https://api.mainnet-beta.solana.com")
        self.accounts_to_watch: List[str] = config.get("accounts", [])
        self.indexed_events: List[Dict[str, Any]] = []
        self.persistence = PersistenceManager()

    async def monitor_accounts(self):
        client = AsyncClient(self.rpc_url)
        print(f"[OnchainFeedListener] Monitoring {len(self.accounts_to_watch)} accounts...")

        while True:
            for acc in self.accounts_to_watch:
                try:
                    pubkey = PublicKey(acc)
                    response = await client.get_account_info(pubkey)
                    if response["result"]["value"]:
                        data = {
                            "account": acc,
                            "timestamp": time.time(),
                            "slot": response["result"]["context"]["slot"],
                            "lamports": response["result"]["value"]["lamports"]
                        }
                        self.indexed_events.append(data)
                        self._save()
                        print(f"[OnchainFeedListener] Event captured for {acc} at slot {data['slot']}")
                except Exception as e:
                    print(f"[OnchainFeedListener] Error fetching {acc}: {e}")
            await asyncio.sleep(15)  # interval between fetches

    def add_account(self, account_pubkey: str):
        if account_pubkey not in self.accounts_to_watch:
            self.accounts_to_watch.append(account_pubkey)
            print(f"[OnchainFeedListener] Added account {account_pubkey} to watchlist.")

    def get_event_log(self) -> List[Dict[str, Any]]:
        return self.indexed_events

    def _save(self):
        self.persistence.save(self.agent_name, "event_log", self.indexed_events)

    def status(self):
        base = super().status()
        base.update({"accounts_monitored": len(self.accounts_to_watch)})
        return base


# Example usage
if __name__ == "__main__":
    config = {
        "rpc_url": "https://api.mainnet-beta.solana.com",
        "accounts": [
            "Vote111111111111111111111111111111111111111",  # Governance
            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"  # SPL Token
        ]
    }

    listener = OnchainFeedListener(config)
    asyncio.run(listener.monitor_accounts())
