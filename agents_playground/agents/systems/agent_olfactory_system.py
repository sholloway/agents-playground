from types import SimpleNamespace
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_life_cycle_phase import AgentLifeCyclePhase
from agents_playground.agents.spec.agent_system import AgentSystem

class AgentOlfactorySystem(AgentSystem):
  """
  Provides the sense of smell. The nose perceives chemicals.
  """
  def __init__(self) -> None:
    self.name = 'olfactory-system'
    self.subsystems = SimpleNamespace()

  def before_subsystems_processed(self, characteristics: AgentCharacteristics, agent_phase: AgentLifeCyclePhase) -> None:
    """
    - What does the agent smell? 
    """
    return