from jinja2 import Environment, FileSystemLoader
import os
from typing import List, Dict

# Configure Jinja environment for template rendering
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

class FrontendRenderer:
    def __init__(self):
        self.env = env
        print("[FrontendRenderer] Initialized with templates from:", TEMPLATE_DIR)

    def render_sentiment(self, sentiment_data: List[Dict]) -> str:
        template = self.env.get_template("sentiment.html")
        return template.render(sentiments=sentiment_data)

    def render_contributors(self, contributor_data: Dict[str, Dict]) -> str:
        template = self.env.get_template("contributors.html")
        return template.render(contributors=contributor_data)

    def render_alerts(self, alerts: List[Dict]) -> str:
        template = self.env.get_template("alerts.html")
        return template.render(alerts=alerts)

    def render_dashboard(self, sentiment_data, contributor_data, alerts) -> str:
        template = self.env.get_template("dashboard.html")
        return template.render(
            sentiments=sentiment_data,
            contributors=contributor_data,
            alerts=alerts
        )


# Example usage (simulated rendering)
if __name__ == "__main__":
    renderer = FrontendRenderer()

    example_sentiments = [
        {"message_id": "msg1", "score": 3},
        {"message_id": "msg2", "score": 1}
    ]

    example_contributors = {
        "wallet001": {"name": "Alice", "tasks": 5},
        "wallet002": {"name": "Bob", "tasks": 2}
    }

    example_alerts = [
        {"type": "warning", "message": "Low validator uptime"},
        {"type": "info", "message": "Governance proposal passed"}
    ]

    print(renderer.render_sentiment(example_sentiments))
    print(renderer.render_contributors(example_contributors))
    print(renderer.render_alerts(example_alerts))
    print(renderer.render_dashboard(example_sentiments, example_contributors, example_alerts))
