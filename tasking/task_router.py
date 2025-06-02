import time
from typing import Dict, List, Any
from atheris.core.agent_base import AgentBase
from atheris.core.persistence_manager import PersistenceManager


class TaskRouter(AgentBase):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.agent_name = "task_router"
        self.persistence = PersistenceManager()
        self.task_queue: List[Dict[str, Any]] = []
        self.assignment_log: Dict[str, Dict[str, Any]] = {}
        self.contributors: List[str] = config.get("contributors", [])

    def run(self):
        print("[TaskRouter] Task routing system is live...")

    def register_contributor(self, name: str):
        if name not in self.contributors:
            self.contributors.append(name)
            print(f"[TaskRouter] Contributor {name} registered.")

    def add_task(self, task_id: str, description: str, priority: int = 5):
        task = {
            "task_id": task_id,
            "description": description,
            "priority": priority,
            "assigned_to": None,
            "timestamp": time.time(),
            "status": "pending"
        }
        self.task_queue.append(task)
        self._save()
        print(f"[TaskRouter] Added task {task_id} with priority {priority}.")

    def assign_tasks(self):
        if not self.contributors:
            print("[TaskRouter] No contributors registered.")
            return

        self.task_queue.sort(key=lambda x: x["priority"], reverse=True)
        for idx, task in enumerate(self.task_queue):
            if task["assigned_to"] is None:
                contributor = self.contributors[idx % len(self.contributors)]
                task["assigned_to"] = contributor
                task["status"] = "assigned"
                self.assignment_log[task["task_id"]] = {
                    "contributor": contributor,
                    "assigned_at": time.time()
                }
                print(f"[TaskRouter] Assigned task {task['task_id']} to {contributor}")

        self._save()

    def complete_task(self, task_id: str):
        for task in self.task_queue:
            if task["task_id"] == task_id and task["status"] == "assigned":
                task["status"] = "completed"
                self._save()
                print(f"[TaskRouter] Task {task_id} marked as completed.")
                return

    def list_tasks(self, status_filter: str = None) -> List[Dict[str, Any]]:
        if status_filter:
            return [t for t in self.task_queue if t["status"] == status_filter]
        return self.task_queue

    def get_assignment_log(self) -> Dict[str, Dict[str, Any]]:
        return self.assignment_log

    def _save(self):
        self.persistence.save(self.agent_name, "tasks", self.task_queue)
        self.persistence.save(self.agent_name, "log", self.assignment_log)

    def status(self):
        base = super().status()
        base.update({
            "total_tasks": len(self.task_queue),
            "contributors": len(self.contributors)
        })
        return base


if __name__ == "__main__":
    config = {
        "contributors": ["Alice", "Bob", "Carol"]
    }

    router = TaskRouter(config)
    router.run()

    router.add_task("task001", "Review the latest proposal", 7)
    router.add_task("task002", "Draft a new validator FAQ", 5)
    router.add_task("task003", "Moderate discussion on forum", 6)

    router.assign_tasks()
    router.complete_task("task001")

    print("Assigned Tasks:")
    for task in router.list_tasks("assigned"):
        print(task)

    print("Completed Tasks:")
    for task in router.list_tasks("completed"):
        print(task)
