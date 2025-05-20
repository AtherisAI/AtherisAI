import time
from typing import Callable, Dict, Any, List
from atheris.core.agent_base import AgentBase
from atheris.core.persistence_manager import PersistenceManager


class FeedbackLoop:
    def __init__(self, agents: Dict[str, AgentBase], scoring_fn: Callable[[str, Any], float]):
        """
        Initialize feedback loop system.

        Args:
            agents (dict): Mapping of agent names to instances
            scoring_fn (func): Function to evaluate output quality
        """
        self.agents = agents
        self.scoring_fn = scoring_fn
        self.persistence = PersistenceManager()
        self.feedback_data: Dict[str, List[float]] = {}

    def evaluate_output(self, agent_name: str, output: Any):
        """
        Score a given agent output and record feedback.

        Args:
            agent_name (str): Name of the agent
            output (Any): Output to evaluate
        """
        score = self.scoring_fn(agent_name, output)
        print(f"[FeedbackLoop] Scored output from '{agent_name}' — Score: {score}")

        if agent_name not in self.feedback_data:
            self.feedback_data[agent_name] = []

        self.feedback_data[agent_name].append(score)
        self.persistence.append_log(agent_name, {
            "feedback_score": score,
            "output": output
        })

        if len(self.feedback_data[agent_name]) >= 5:
            self._adjust_agent_policy(agent_name)

    def _adjust_agent_policy(self, agent_name: str):
        """
        Adjust parameters of an agent based on recent feedback.

        For now, adjusts only interval timing — can be extended to model weights, source weighting, etc.
        """
        agent = self.agents.get(agent_name)
        if not agent:
            print(f"[FeedbackLoop] Agent '{agent_name}' not found.")
            return

        recent_scores = self.feedback_data[agent_name][-5:]
        avg_score = sum(recent_scores) / len(recent_scores)

        print(f"[FeedbackLoop] Avg score for '{agent_name}' = {avg_score:.2f}")

        # Example policy: slow down bad agents, speed up good ones
        if avg_score < 0.5:
            agent.interval = min(agent.interval + 1, 30)
            print(f"[FeedbackLoop] Slowing down '{agent_name}' to {agent.interval}s")
        elif avg_score > 0.8:
            agent.interval = max(agent.interval - 1, 1)
            print(f"[FeedbackLoop] Speeding up '{agent_name}' to {agent.interval}s")

        # Save new interval to persistence
        self.persistence.checkpoint_agent(agent_name, {"interval": agent.interval})

    def restore_feedback_state(self):
        """
        Load past feedback scores from logs (for continuity).
        """
        for agent_name in self.agents.keys():
            logs = self.persistence.get_log_history(agent_name)
            for entry in logs:
                if "feedback_score" in entry.get("event", {}):
                    score = entry["event"]["feedback_score"]
                    self.feedback_data.setdefault(agent_name, []).append(score)

    def manual_feedback(self, agent_name: str, score: float):
        """
        Allow external system (admin, dashboard) to submit a feedback score manually.
        """
        print(f"[FeedbackLoop] Manual feedback received for '{agent_name}' — Score: {score}")
        self.feedback_data.setdefault(agent_name, []).append(score)
        self.persistence.append_log(agent_name, {"feedback_score": score})


# Example scoring function
def dummy_scorer(agent_name: str, output: Any) -> float:
    # Placeholder logic — real implementation would evaluate quality of decisions, analysis, etc.
    import random
    return round(random.uniform(0, 1), 2)


# Example test run
if __name__ == "__main__":
    from atheris.embedded.output_agent import OutputAgent

    agents = {
        "output": OutputAgent({"interval": 5})
    }

    loop = FeedbackLoop(agents, scoring_fn=dummy_scorer)
    loop.restore_feedback_state()

    # Simulate output and feedback loop
    for _ in range(10):
        result = agents["output"].run()
        loop.evaluate_output("output", result)
        time.sleep(1)
