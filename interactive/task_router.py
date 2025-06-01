import time
import random
from typing import Dict, Any, List
from atheris.core.agent_base import AgentBase
from atheris.core.persistence_manager import PersistenceManager


class TaskRouter(AgentBase):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.agent_name = "task_router"
        self.persistence = PersistenceManager()
        self.pending_tasks = []

    def run(self):
        print("[TaskRouter] Task routing agent initialized.")

    def register_task(self, task_type: str, payload: Dict[str, Any]):
        task_id = f"{task_type}_{int(time.time())}"
        task = {
            "id": task_id,
            "type": task_type,
            "payload": payload,
            "assigned_to": self._find_target(task_type),
            "status": "queued",
            "created_at": time.time()
        }
        self.pending_tasks.append(task)
        self._save()
        print(f"[TaskRouter] Registered task {task_id} for {task['assigned_to']}")

    def _find_target(self, task_type: str) -> str:
        """Placeholder logic to find an agent or contributor."""
        if task_type in ["respond", "classify", "alert"]:
            return f"agent_{task_type}"
        contributors = self._get_contributors()
        if contributors:
            return random.choice(contributors)
        return "agent_fallback"

    def _get_contributors(self) -> List[str]:
        data = self.persistence.load("identity_interface", "profiles") or {}
        return list(data.keys())

    def get_queue(self) -> List[Dict[str, Any]]:
        return self.pending_tasks

    def mark_done(self, task_id: str):
        for task in self.pending_tasks:
            if task["id"] == task_id:
                task["status"] = "completed"
                self._save()
                print(f"[TaskRouter] Task {task_id} marked as completed.")
                return
        print(f"[TaskRouter] Task {task_id} not found.")

    def _save(self):
        self.persistence.save(self.agent_name, "task_queue", self.pending_tasks)

    def status(self):
        base = super().status()
        base.update({"pending_tasks": len(self.pending_tasks)})
        return base


# Example usage
if __name__ == "__main__":
    router = TaskRouter({})
    router.run()

    router.register_task("respond", {"event": "proposal_created", "proposal_id": "prop-202"})
    router.register_task("alert", {"wallet": "9xL1...", "reason": "suspicious behavior"})

    print("=== Task Queue ===")
    for task in router.get_queue():
        print("-", task)
