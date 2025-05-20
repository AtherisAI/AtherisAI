import threading
import queue
from typing import Dict, List, Any, Callable
from atheris.core.agent_base import AgentBase


class ExecutionPipeline:
    def __init__(self):
        """
        Initializes the execution pipeline with agent queues and routing logic.
        """
        self.agents: Dict[str, AgentBase] = {}
        self.queues: Dict[str, queue.Queue] = {}
        self.routes: Dict[str, List[str]] = {}
        self.handlers: Dict[str, Callable[[Any], None]] = {}
        self.running = False

    def register_agent(self, name: str, agent: AgentBase):
        """
        Register a new agent with its own execution queue.
        """
        self.agents[name] = agent
        self.queues[name] = queue.Queue()
        print(f"[ExecutionPipeline] Agent '{name}' registered.")

    def define_route(self, from_agent: str, to_agents: List[str]):
        """
        Define one-way routing between agents (by name).
        """
        self.routes[from_agent] = to_agents
        print(f"[ExecutionPipeline] Route added: {from_agent} → {to_agents}")

    def register_output_handler(self, agent_name: str, handler: Callable[[Any], None]):
        """
        Register a custom handler for agent output (e.g. send to dashboard).
        """
        self.handlers[agent_name] = handler
        print(f"[ExecutionPipeline] Output handler registered for '{agent_name}'.")

    def enqueue_task(self, agent_name: str, data: Any):
        """
        Add a task to a specific agent's queue.
        """
        if agent_name in self.queues:
            self.queues[agent_name].put(data)
            print(f"[ExecutionPipeline] Task enqueued to '{agent_name}'.")

    def start(self):
        """
        Start pipeline execution in background threads.
        """
        self.running = True
        for name in self.agents:
            thread = threading.Thread(target=self._agent_loop, args=(name,), daemon=True)
            thread.start()
            print(f"[ExecutionPipeline] Execution thread started for '{name}'.")

    def stop(self):
        """
        Stop all pipeline operations.
        """
        self.running = False
        print("[ExecutionPipeline] Pipeline stopped.")

    def _agent_loop(self, name: str):
        """
        Agent-specific execution loop.
        Processes queued tasks and routes results as needed.
        """
        agent = self.agents[name]
        q = self.queues[name]

        while self.running:
            try:
                if not q.empty():
                    task_data = q.get()
                    result = agent.run_with_input(task_data) if hasattr(agent, 'run_with_input') else agent.run()

                    # Output handler (dashboard, alerts, etc.)
                    if name in self.handlers:
                        self.handlers[name](result)

                    # Route result to next agents
                    next_agents = self.routes.get(name, [])
                    for dest in next_agents:
                        self.enqueue_task(dest, result)

            except Exception as e:
                print(f"[ExecutionPipeline] Error in '{name}': {e}")

    def reset(self):
        """
        Clears all queues and routes (for test or restart).
        """
        for q in self.queues.values():
            with q.mutex:
                q.queue.clear()
        self.routes = {}
        print("[ExecutionPipeline] Pipeline reset complete.")


# Example usage
if __name__ == "__main__":
    from atheris.embedded.learning_agent import LearningAgent
    from atheris.embedded.analytical_agent import AnalyticalAgent
    from atheris.embedded.output_agent import OutputAgent

    # Dummy test agents
    agents = {
        "learning": LearningAgent({"interval": 3}),
        "analysis": AnalyticalAgent({"interval": 3}),
        "output": OutputAgent({"interval": 3})
    }

    pipeline = ExecutionPipeline()
    for name, agent in agents.items():
        pipeline.register_agent(name, agent)

    # Define flow: learning → analysis → output
    pipeline.define_route("learning", ["analysis"])
    pipeline.define_route("analysis", ["output"])

    # Start execution
    pipeline.start()

    # Inject starting task
    pipeline.enqueue_task("learning", {"start": True})

    try:
        while True:
            pass
    except KeyboardInterrupt:
        pipeline.stop()
