import time
from abc import ABC, abstractmethod
from typing import Dict, Optional


class AgentBase(ABC):
    def __init__(self, config: Optional[Dict] = None):
        """
        Base constructor for an AI agent.

        Args:
            config (dict): Optional dictionary with agent configuration.
        """
        self.name = self.__class__.__name__
        self.config = config or {}
        self.interval = self.config.get("interval", 5)  # seconds
        self.active = True
        self.last_run = None
        self.state = "Initialized"
        self._init_logging()

    def _init_logging(self):
        """Hook to set up agent-level logging."""
        print(f"[{self.name}] Initialized with interval {self.interval}s")

    @abstractmethod
    def run(self):
        """
        Core logic for the agent. Must be implemented by subclasses.
        """
        pass

    def stop(self):
        """
        Gracefully stops the agent's operation.
        """
        self.active = False
        self.state = "Stopped"
        print(f"[{self.name}] Stopped")

    def status(self) -> Dict:
        """
        Returns current status of the agent for monitoring purposes.
        """
        return {
            "agent": self.name,
            "active": self.active,
            "last_run": self.last_run,
            "state": self.state,
            "interval": self.interval
        }

    def _update_status(self):
        """Updates internal run timestamp and state after each run."""
        self.last_run = time.time()
        self.state = "Running"

    def _handle_exception(self, error: Exception):
        """
        Handles runtime exceptions and logs errors.
        """
        self.state = f"Error: {str(error)}"
        print(f"[{self.name}] Exception: {error}")

    def execute(self):
        """
        Internal wrapper that handles safe execution with logging and timing.
        """
        if not self.active:
            return

        try:
            self._update_status()
            self.run()
        except Exception as e:
            self._handle_exception(e)
