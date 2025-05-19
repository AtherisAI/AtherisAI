import threading
import time
from typing import Dict, Any
from atheris.core.agent_base import AgentBase

class AgentSupervisor:
    def __init__(self, agents: Dict[str, AgentBase], check_interval: int = 10):
        """
        Initialize the supervisor with agent references and a health check interval.

        Args:
            agents (dict): Dictionary of agent name to agent instance
            check_interval (int): Interval between health checks (seconds)
        """
        self.agents = agents
        self.check_interval = check_interval
        self.supervisor_active = False
        self.thread = None
        self.last_status: Dict[str, Any] = {}

    def start(self):
        """Start the supervisor thread"""
        self.supervisor_active = True
        self.thread = threading.Thread(target=self._run_supervisor, daemon=True)
        self.thread.start()
        print("[AgentSupervisor] Monitoring started.")

    def _run_supervisor(self):
        """Internal loop to monitor all agents"""
        while self.supervisor_active:
            for name, agent in self.agents.items():
                try:
                    status = agent.status()
                    self.last_status[name] = status

                    # Check for unresponsive or failed state
                    if status["state"].startswith("Error"):
                        print(f"[AgentSupervisor] Detected error in '{name}': {status['state']}")
                        self._restart_agent(name, agent)

                except Exception as e:
                    print(f"[AgentSupervisor] Failed to check status of '{name}': {e}")

            time.sleep(self.check_interval)

    def _restart_agent(self, name: str, agent: AgentBase):
        """Attempt to restart an agent after failure"""
        print(f"[AgentSupervisor] Restarting agent '{name}'...")
        try:
            agent.stop()
            agent.active = True
            agent.state = "Restarted"
            thread = threading.Thread(target=agent.execute, daemon=True)
            thread.start()
            print(f"[AgentSupervisor] Agent '{name}' restarted.")
        except Exception as e:
            print(f"[AgentSupervisor] Failed to restart '{name}': {e}")

    def get_report(self) -> Dict[str, Any]:
        """Returns the latest snapshot of agent statuses"""
        return self.last_status

    def stop(self):
        """Stops the supervisor process"""
        self.supervisor_active = False
        print("[AgentSupervisor] Monitoring stopped.")


# Example usage (test simulation)
if __name__ == "__main__":
    from atheris.embedded.learning_agent import LearningAgent

    # Simulated test setup
    agents = {
        "learning": LearningAgent({"interval": 3})
    }

    # Start agents manually
    for a in agents.values():
        threading.Thread(target=a.execute, daemon=True).start()

    # Start supervisor
    supervisor = AgentSupervisor(agents)
    supervisor.start()

    try:
        while True:
            time.sleep(30)
            print("Status report:", supervisor.get_report())
    except KeyboardInterrupt:
        supervisor.stop()
