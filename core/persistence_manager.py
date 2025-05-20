import os
import json
import time
from typing import Any, Dict, Optional

STORAGE_ROOT = "./storage/"


class PersistenceManager:
    def __init__(self, base_path: str = STORAGE_ROOT):
        """
        Initialize the persistence manager.

        Args:
            base_path (str): Root path for all storage
        """
        self.base_path = base_path
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        print(f"[PersistenceManager] Initialized at {base_path}")

    def _file_path(self, agent_name: str, key: str) -> str:
        """
        Construct the file path for a given agent and key.
        """
        agent_dir = os.path.join(self.base_path, agent_name)
        if not os.path.exists(agent_dir):
            os.makedirs(agent_dir)
        return os.path.join(agent_dir, f"{key}.json")

    def save(self, agent_name: str, key: str, data: Any):
        """
        Save data to a JSON file.

        Args:
            agent_name (str): Name of the agent
            key (str): Identifier (e.g., 'checkpoint', 'output')
            data (Any): JSON-serializable object
        """
        path = self._file_path(agent_name, key)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"[PersistenceManager] Saved {key} for '{agent_name}'")

    def load(self, agent_name: str, key: str) -> Optional[Any]:
        """
        Load data from a JSON file.

        Returns:
            Loaded data or None if file not found.
        """
        path = self._file_path(agent_name, key)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def append_log(self, agent_name: str, log_data: Dict[str, Any]):
        """
        Append a log entry with timestamp to agent's log file.

        Args:
            log_data (dict): JSON log entry
        """
        log_path = self._file_path(agent_name, "log")
        existing = []

        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                existing = json.load(f)

        log_entry = {
            "timestamp": time.time(),
            "event": log_data
        }
        existing.append(log_entry)

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2)

        print(f"[PersistenceManager] Logged event for '{agent_name}'")

    def checkpoint_agent(self, agent_name: str, state_data: Dict[str, Any]):
        """
        Save an agent's checkpoint.
        """
        self.save(agent_name, "checkpoint", state_data)

    def restore_agent(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Load agent checkpoint if exists.
        """
        return self.load(agent_name, "checkpoint")

    def get_log_history(self, agent_name: str) -> list:
        """
        Return agent's full event log.
        """
        return self.load(agent_name, "log") or []

    def clear_agent_data(self, agent_name: str):
        """
        Delete all stored data for a given agent.
        """
        agent_dir = os.path.join(self.base_path, agent_name)
        if os.path.exists(agent_dir):
            for f in os.listdir(agent_dir):
                os.remove(os.path.join(agent_dir, f))
            os.rmdir(agent_dir)
            print(f"[PersistenceManager] Cleared data for '{agent_name}'")


# Example usage
if __name__ == "__main__":
    pm = PersistenceManager()
    agent = "learning"

    # Save checkpoint
    state = {"last_block": 15740321, "last_fetch": time.time()}
    pm.checkpoint_agent(agent, state)

    # Load checkpoint
    restored = pm.restore_agent(agent)
    print("Restored state:", restored)

    # Append logs
    pm.append_log(agent, {"action": "fetch", "status": "success"})

    # Load full log
    log = pm.get_log_history(agent)
    print("Log history:", log)
