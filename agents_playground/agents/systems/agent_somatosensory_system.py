from types import SimpleNamespace
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_life_cycle_phase import AgentLifeCyclePhase
from agents_playground.agents.spec.agent_system import AgentSystem

class AgentSomatosensorySystem(AgentSystem):
  """
  Provides the sense of touch. The skin perceives position, motion, temperature and tactile stimulation.
  """
  def __init__(self) -> None:
    self.name = 'somatosensory-system'
    self.subsystems = SimpleNamespace()

  def _before_subsystems_processed(self, characteristics: AgentCharacteristics, agent_phase: AgentLifeCyclePhase) -> None:
    """
    - What is the agent touching? 
    - What is their temperature? Are they hot, cold?
    """
    return
