import time
from typing import Dict, Any, List
from atheris.core.agent_base import AgentBase
from atheris.core.persistence_manager import PersistenceManager


class WorkflowTrigger(AgentBase):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.agent_name = "workflow_trigger"
        self.persistence = PersistenceManager()
        self.triggers: List[Dict[str, Any]] = []

    def run(self):
        print("[WorkflowTrigger] Listening for workflow triggers...")

    def add_trigger(self, signal_type: str, match_criteria: Dict[str, Any], target_workflow: str):
        """Register a new signal->workflow trigger."""
        trigger = {
            "signal_type": signal_type,
            "match_criteria": match_criteria,
            "target_workflow": target_workflow,
            "registered_at": time.time()
        }
        self.triggers.append(trigger)
        self._save()
        print(f"[WorkflowTrigger] Registered trigger for {signal_type} -> {target_workflow}")

    def evaluate_signal(self, signal: Dict[str, Any]):
        """Evaluate incoming signal and trigger workflows if matched."""
        matches = []
        for trig in self.triggers:
            if trig["signal_type"] == signal.get("type"):
                # Basic key match
                if all(signal.get(k) == v for k, v in trig["match_criteria"].items()):
                    matches.append(trig["target_workflow"])

        for workflow in matches:
            self._launch_workflow(workflow, signal)

    def _launch_workflow(self, workflow_name: str, signal: Dict[str, Any]):
        print(f"[WorkflowTrigger] Launching workflow '{workflow_name}' due to signal:", signal)

    def _save(self):
        self.persistence.save(self.agent_name, "triggers", self.triggers)

    def list_triggers(self) -> List[Dict[str, Any]]:
        return self.triggers

    def status(self):
        base = super().status()
        base.update({"registered_triggers": len(self.triggers)})
        return base


# Example usage
if __name__ == "__main__":
    trigger = WorkflowTrigger({})
    trigger.run()

    # Add a trigger
    trigger.add_trigger(
        signal_type="proposal_created",
        match_criteria={"category": "finance"},
        target_workflow="auto_review_finance_proposal"
    )

    # Send a signal
    signal = {
        "type": "proposal_created",
        "category": "finance",
        "proposal_id": "fin-042"
    }

    print("=== Evaluating Signal ===")
    trigger.evaluate_signal(signal)
