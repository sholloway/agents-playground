from types import SimpleNamespace
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_life_cycle_phase import AgentLifeCyclePhase
from agents_playground.agents.spec.agent_system import AgentSystem

class AgentGustatorySystem(AgentSystem):
  """
  Provides the sense of taste. The mouth perceives chemicals.
  """
  def __init__(self) -> None:
    self.name = 'gustatory-system'
    self.subsystems = SimpleNamespace()

  def before_subsystems_processed(self, characteristics: AgentCharacteristics, agent_phase: AgentLifeCyclePhase) -> None:
    """
    - Is there anything in the agent's mouth? What does it taste like? 
    """
    return
