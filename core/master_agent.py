import threading
import time
from typing import Dict, List

# Agent imports (defined in other files)
from atheris.embedded.learning_agent import LearningAgent
from atheris.embedded.analytical_agent import AnalyticalAgent
from atheris.embedded.output_agent import OutputAgent
from atheris.interactive.responder_agent import ResponderAgent
from atheris.interactive.chatbot_agent import ChatBotAgent

class MasterAgent:
    def __init__(self, config: Dict):
        """
        Initialize the master agent with configuration for each AI agent.
        """
        self.config = config
        self.agents = {
            "learning": LearningAgent(config.get("learning", {})),
            "analysis": AnalyticalAgent(config.get("analysis", {})),
            "output": OutputAgent(config.get("output", {})),
            "responder": ResponderAgent(config.get("responder", {})),
            "chatbot": ChatBotAgent(config.get("chatbot", {})),
        }
        self.agent_threads: List[threading.Thread] = []
        self.running = False

    def start_all_agents(self):
        """
        Start all agents in individual threads.
        """
        self.running = True
        for name, agent in self.agents.items():
            thread = threading.Thread(target=self._run_agent_loop, args=(name, agent), daemon=True)
            self.agent_threads.append(thread)
            thread.start()
            print(f"[MasterAgent] Started agent '{name}'")

    def _run_agent_loop(self, name: str, agent):
        """
        Continuously run an agent on its defined interval.
        """
        print(f"[MasterAgent] Running loop for agent: {name}")
        while self.running:
            try:
                agent.run()
                time.sleep(agent.interval)
            except Exception as e:
                print(f"[MasterAgent] Error in '{name}': {e}")
                time.sleep(3)

    def stop_all_agents(self):
        """
        Stop all agents and mark the system as inactive.
        """
        print("[MasterAgent] Stopping all agents...")
        self.running = False
        for agent in self.agents.values():
            agent.stop()

    def get_status(self) -> Dict:
        """
        Returns a summary of the system status and agent health.
        """
        return {name: agent.status() for name, agent in self.agents.items()}

# Run as script (for testing purposes)
if __name__ == "__main__":
    sample_config = {
        "learning": {"interval": 5},
        "analysis": {"interval": 8},
        "output": {"interval": 10},
        "responder": {"interval": 4},
        "chatbot": {"interval": 6}
    }

    master_agent = MasterAgent(sample_config)

    try:
        master_agent.start_all_agents()
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        master_agent.stop_all_agents()
