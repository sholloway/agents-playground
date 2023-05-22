from types import SimpleNamespace
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_life_cycle_phase import AgentLifeCyclePhase
from agents_playground.agents.spec.agent_system import AgentSystem

class AgentVisualSystem(AgentSystem):
  """
  Provides the sense of sight. The eyes perceive light.
  """
  def __init__(self) -> None:
    self.name = 'visual-system'
    self.subsystems = SimpleNamespace()

  def before_subsystems_processed(self, characteristics: AgentCharacteristics, agent_phase: AgentLifeCyclePhase) -> None:
    """What does the agent see?"""
    return