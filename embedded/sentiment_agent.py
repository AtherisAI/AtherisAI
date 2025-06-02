import time
import random
from typing import Dict, Any, List
from atheris.core.agent_base import AgentBase
from atheris.core.persistence_manager import PersistenceManager
from atheris.utils.text_preprocessing import preprocess_text


class SentimentAgent(AgentBase):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.agent_name = "sentiment_agent"
        self.persistence = PersistenceManager()
        self.recent_inputs: List[str] = []
        self.sentiment_scores: Dict[str, float] = {}

    def run(self):
        print("[SentimentAgent] Running sentiment analysis loop...")

    def analyze_sentiment(self, message_id: str, content: str) -> float:
        clean_text = preprocess_text(content)
        score = self._mock_sentiment_score(clean_text)
        self.sentiment_scores[message_id] = score
        self._save()
        print(f"[SentimentAgent] Analyzed '{message_id}' with score {score}")
        return score

    def _mock_sentiment_score(self, text: str) -> float:
        keywords = {
            "positive": ["good", "great", "awesome", "love", "support", "win", "excellent", "agree"],
            "negative": ["bad", "terrible", "hate", "broken", "scam", "fraud", "problem", "disagree"]
        }
        score = 0
        for word in keywords["positive"]:
            if word in text:
                score += 1
        for word in keywords["negative"]:
            if word in text:
                score -= 1
        normalized_score = round((score + 5) / 10, 2)
        return min(max(normalized_score, 0.0), 1.0)

    def batch_analyze(self, messages: Dict[str, str]):
        for mid, content in messages.items():
            self.analyze_sentiment(mid, content)

    def get_scores(self) -> Dict[str, float]:
        return self.sentiment_scores

    def list_top_sentiments(self, top_n: int = 5) -> List[str]:
        sorted_items = sorted(self.sentiment_scores.items(), key=lambda x: x[1], reverse=True)
        return [f"{k}: {v}" for k, v in sorted_items[:top_n]]

    def list_negative_cases(self) -> List[str]:
        return [k for k, v in self.sentiment_scores.items() if v < 0.4]

    def average_score(self) -> float:
        if not self.sentiment_scores:
            return 0.0
        return round(sum(self.sentiment_scores.values()) / len(self.sentiment_scores), 2)

    def export_summary(self) -> Dict[str, Any]:
        return {
            "total_messages": len(self.sentiment_scores),
            "average_score": self.average_score(),
            "top_positives": self.list_top_sentiments(3),
            "negatives_detected": self.list_negative_cases()
        }

    def _save(self):
        self.persistence.save(self.agent_name, "sentiment_scores", self.sentiment_scores)

    def status(self):
        base = super().status()
        base.update({
            "total_analyzed": len(self.sentiment_scores),
            "avg_score": self.average_score()
        })
        return base


if __name__ == "__main__":
    agent = SentimentAgent({})
    agent.run()

    messages = {
        "msg001": "I love how this DAO listens to its members.",
        "msg002": "This vote process is terrible and slow.",
        "msg003": "Great update to the proposal system!",
        "msg004": "Everything is broken again, typical.",
        "msg005": "I support the new governance structure.",
        "msg006": "Honestly, this feels like a scam.",
        "msg007": "Amazing speed improvements!",
        "msg008": "Bad execution of a good idea.",
        "msg009": "Excellent clarity in the new roadmap.",
        "msg010": "I strongly disagree with the validator incentives."
    }

    agent.batch_analyze(messages)

    print("Sentiment Summary:")
    summary = agent.export_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")
