import time
import threading
from typing import Dict, Any
from datetime import datetime
from atheris.solana.rpc_connector import get_latest_block, get_vote_status

class ContextManager:
    def __init__(self, update_interval: int = 10):
        """
        Initializes the context manager and begins context refresh loop.
        """
        self.context: Dict[str, Any] = {}
        self.update_interval = update_interval
        self.running = False
        self.thread = None

    def start(self):
        """Starts background context refresh loop."""
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        print("[ContextManager] Context updates started.")

    def stop(self):
        """Stops context updates."""
        self.running = False
        print("[ContextManager] Context updates stopped.")

    def _run_loop(self):
        """Fetches and updates shared context at regular intervals."""
        while self.running:
            try:
                self._update_context()
            except Exception as e:
                print(f"[ContextManager] Error updating context: {e}")
            time.sleep(self.update_interval)

    def _update_context(self):
        """Build the current context snapshot."""
        timestamp = datetime.utcnow().isoformat()
        block_info = get_latest_block()
        vote_info = get_vote_status()

        self.context = {
            "timestamp": timestamp,
            "solana_block": block_info,
            "vote_summary": vote_info,
            "active_proposals": self._mock_active_proposals(),
            "global_status": {
                "network_health": "stable" if block_info.get("slot", 0) % 2 == 0 else "syncing",
                "agent_mode": "live",
            }
        }

        print(f"[ContextManager] Context updated at {timestamp}")

    def _mock_active_proposals(self):
        """Placeholder for proposal tracking — replace with governance agent integration."""
        return [
            {"id": "prop-001", "status": "voting", "votes_for": 128, "votes_against": 40},
            {"id": "prop-002", "status": "draft", "author": "0xabc...123"}
        ]

    def get(self, key: str, default: Any = None) -> Any:
        """Access specific part of context."""
        return self.context.get(key, default)

    def snapshot(self) -> Dict[str, Any]:
        """Return a copy of the full context."""
        return self.context.copy()


# Test mode
if __name__ == "__main__":
    ctx = ContextManager(update_interval=5)
    ctx.start()

    try:
        for _ in range(3):
            time.sleep(6)
            print("Snapshot:", ctx.snapshot())
    except KeyboardInterrupt:
        ctx.stop()
