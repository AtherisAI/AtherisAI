import importlib
from typing import Dict, Type, Any, Optional
from atheris.core.agent_base import AgentBase


class AgentRegistry:
    _registry: Dict[str, Type[AgentBase]] = {}

    @classmethod
    def register(cls, name: str, agent_class: Type[AgentBase]):
        """
        Register an agent class by name.

        Args:
            name (str): Unique identifier for the agent
            agent_class (Type[AgentBase]): The agent class
        """
        if not issubclass(agent_class, AgentBase):
            raise ValueError("Agent class must inherit from AgentBase")
        cls._registry[name] = agent_class
        print(f"[AgentRegistry] Registered agent '{name}'")

    @classmethod
    def get(cls, name: str) -> Optional[Type[AgentBase]]:
        """
        Retrieve an agent class by name.

        Args:
            name (str): Name of the registered agent
        Returns:
            Type[AgentBase] or None
        """
        return cls._registry.get(name)

    @classmethod
    def create(cls, name: str, config: Dict[str, Any]) -> AgentBase:
        """
        Instantiate an agent from its name and config.

        Args:
            name (str): Registered agent name
            config (dict): Configuration dictionary

        Returns:
            AgentBase: Instantiated agent object
        """
        agent_class = cls.get(name)
        if not agent_class:
            raise ValueError(f"Agent '{name}' not found in registry.")
        return agent_class(config)


def dynamic_import(module_path: str, class_name: str) -> Type[AgentBase]:
    """
    Dynamically imports a class from a module.

    Args:
        module_path (str): e.g. 'atheris.embedded.learning_agent'
        class_name (str): e.g. 'LearningAgent'

    Returns:
        The imported class
    """
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    if not issubclass(cls, AgentBase):
        raise TypeError("Imported class must inherit from AgentBase")
    return cls


# Example static registrations (can also happen dynamically at runtime)
if __name__ == "__main__":
    from atheris.embedded.learning_agent import LearningAgent
    from atheris.interactive.chatbot_agent import ChatBotAgent

    AgentRegistry.register("learning", LearningAgent)
    AgentRegistry.register("chatbot", ChatBotAgent)

    config = {"interval": 5}
    learning_instance = AgentRegistry.create("learning", config)
    chatbot_instance = AgentRegistry.create("chatbot", config)

    print("Instantiated:", learning_instance.__class__.__name__)
    print("Instantiated:", chatbot_instance.__class__.__name__)
