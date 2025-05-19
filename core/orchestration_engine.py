import time
import threading
from typing import Dict, List
from atheris.core.agent_base import AgentBase

class OrchestrationEngine:
    def __init__(self, agents: Dict[str, AgentBase], schedule: List[List[str]]):
        """
        Initialize the orchestration engine.

        Args:
            agents (dict): All available agents, indexed by name
            schedule (list of list): Ordered execution groups by agent names
        """
        self.agents = agents
        self.schedule = schedule  # e.g. [["learning"], ["analysis"], ["output"]]
        self.running = False
        self.interval = 10  # default full-cycle interval

    def start(self):
        """Start the orchestration loop in a separate thread"""
        print("[OrchestrationEngine] Starting orchestration...")
        self.running = True
        threading.Thread(target=self._run_loop, daemon=True).start()

    def _run_loop(self):
        """Main execution loop"""
        while self.running:
            print("[OrchestrationEngine] Beginning execution cycle...")
            for step_index, group in enumerate(self.schedule):
                print(f"[OrchestrationEngine] Executing step {step_index+1}: {group}")
                self._execute_group(group)
                time.sleep(0.5)  # buffer between steps

            print("[OrchestrationEngine] Cycle complete. Sleeping...\n")
            time.sleep(self.interval)

    def _execute_group(self, group: List[str]):
        """Execute a group of agents in parallel"""
        threads = []
        for name in group:
            agent = self.agents.get(name)
            if agent and agent.active:
                thread = threading.Thread(target=self._safe_execute, args=(name, agent), daemon=True)
                threads.append(thread)
                thread.start()

        for thread in threads:
            thread.join()

    def _safe_execute(self, name: str, agent: AgentBase):
        """Safely execute agent and handle errors"""
        try:
            print(f"[OrchestrationEngine] Running agent: {name}")
            agent.execute()
        except Exception as e:
            print(f"[OrchestrationEngine] Error in agent '{name}': {e}")

    def stop(self):
        """Stop orchestration cycle"""
        self.running = False
        print("[OrchestrationEngine] Orchestration stopped.")

    def update_schedule(self, new_schedule: List[List[str]]):
        """Dynamically update agent execution order"""
        self.schedule = new_schedule
        print(f"[OrchestrationEngine] Schedule updated to: {new_schedule}")

    def set_cycle_interval(self, interval: int):
        """Set delay between full cycles"""
        self.interval = interval
        print(f"[OrchestrationEngine] Cycle interval set to {interval}s")


# Example usage
if __name__ == "__main__":
    from atheris.embedded.learning_agent import LearningAgent
    from atheris.embedded.analytical_agent import AnalyticalAgent
    from atheris.embedded.output_agent import OutputAgent

    agents = {
        "learning": LearningAgent({"interval": 3}),
        "analysis": AnalyticalAgent({"interval": 3}),
        "output": OutputAgent({"interval": 3})
    }

    schedule = [["learning"], ["analysis"], ["output"]]
    engine = OrchestrationEngine(agents, schedule)
    engine.start()

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        engine.stop()
