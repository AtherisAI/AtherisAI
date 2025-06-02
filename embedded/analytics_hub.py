from typing import Dict, Any, List
from atheris.core.agent_base import AgentBase
from atheris.core.persistence_manager import PersistenceManager


class AnalyticsHub(AgentBase):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.agent_name = "analytics_hub"
        self.persistence = PersistenceManager()

    def run(self):
        print("[AnalyticsHub] Aggregating analytics...")

    def aggregate(self) -> Dict[str, Any]:
        learning = self.persistence.load("learning_agent", "learning_data") or {}
        sentiment = self.persistence.load("sentiment_agent", "sentiment_scores") or {}
        activity = self.persistence.load("activity_mapper", "contributor_activity") or {}
        recommendations = self.persistence.load("output_agent", "recommendations") or {}

        aggregated = {
            "learning_insights": learning,
            "sentiment_analysis": sentiment,
            "contributor_map": activity,
            "strategic_recommendations": recommendations
        }

        return aggregated

    def summarize(self) -> str:
        data = self.aggregate()
        summary = []

        if data["sentiment_analysis"]:
            avg_sent = sum(data["sentiment_analysis"].values()) / len(data["sentiment_analysis"])
            summary.append(f"Avg sentiment score: {round(avg_sent, 2)}")
        else:
            summary.append("No sentiment data available.")

        summary.append(f"Recommendations generated: {len(data['strategic_recommendations'])}")
        summary.append(f"Active contributors tracked: {len(data['contributor_map'])}")

        return "\n".join(summary)

    def status(self):
        base = super().status()
        base.update({"aggregates_available": True})
        return base


# Example usage
if __name__ == "__main__":
    hub = AnalyticsHub({})
    hub.run()

    print("=== Aggregated Insights ===")
    print(hub.summarize())
