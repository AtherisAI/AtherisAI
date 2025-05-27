import time
import random
from typing import Dict, Any
from atheris.core.persistence_manager import PersistenceManager


class AgentCalibration:
    def __init__(self, sources: Dict[str, Any]):
        """
        Initialize source tracking.

        Args:
            sources (dict): Source names with config metadata
        """
        self.sources = sources
        self.persistence = PersistenceManager()
        self.trust_scores: Dict[str, float] = {
            name: 0.5 for name in sources
        }
        self._load_history()

    def _load_history(self):
        """Load previous calibration state."""
        stored = self.persistence.load("calibration", "trust_scores")
        if stored:
            self.trust_scores.update(stored)
            print("[AgentCalibration] Loaded historical trust scores.")

    def score_source(self, source: str, success: bool, signal_strength: float = 1.0):
        """Update trust score for a given source."""
        current = self.trust_scores.get(source, 0.5)
        adjustment = 0.05 * signal_strength if success else -0.1
        new_score = min(max(current + adjustment, 0), 1)
        self.trust_scores[source] = new_score
        print(f"[AgentCalibration] Updated '{source}' trust score to {round(new_score, 2)}")

    def get_score(self, source: str) -> float:
        """Return the current trust score for a source."""
        return self.trust_scores.get(source, 0.5)

    def recommend_sources(self, threshold: float = 0.6) -> Dict[str, float]:
        """Return only high-trust sources."""
        return {k: v for k, v in self.trust_scores.items() if v >= threshold}

    def persist_scores(self):
        """Save current trust scores."""
        self.persistence.save("calibration", "trust_scores", self.trust_scores)
        print("[AgentCalibration] Trust scores saved.")


# Example usage
if __name__ == "__main__":
    config_sources = {
        "solana_rpc_1": {},
        "dao_api_v2": {},
        "snapshot_feed": {},
        "discord_index": {}
    }

    calibrator = AgentCalibration(config_sources)

    for i in range(10):
        src = random.choice(list(config_sources.keys()))
        success = random.random() > 0.3
        strength = round(random.uniform(0.5, 1.0), 2)
        calibrator.score_source(src, success, strength)
        time.sleep(0.5)

    print("Recommended Sources:", calibrator.recommend_sources())
    calibrator.persist_scores()
