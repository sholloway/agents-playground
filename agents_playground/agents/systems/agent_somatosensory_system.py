from types import SimpleNamespace
from agents_playground.agents.byproducts.definitions import Stimuli
from agents_playground.agents.byproducts.sensation import Sensation
from agents_playground.agents.default.default_agent_system import SystemWithByproducts
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_life_cycle_phase import AgentLifeCyclePhase
from agents_playground.agents.spec.agent_system import AgentSystem
from agents_playground.agents.spec.byproduct_definition import ByproductDefinition

class AgentSomatosensorySystem(SystemWithByproducts):
  """
  Provides the sense of touch. The skin perceives position, motion, temperature and tactile stimulation.
  """
  def __init__(self) -> None:
    super().__init__(
      name                    = 'somatosensory_system', 
      byproduct_defs          = [Stimuli], 
      internal_byproduct_defs = []
    )

  def _before_subsystems_processed_pre_state_change(
    self, 
    characteristics: AgentCharacteristics, 
    parent_byproducts: dict[str, list]
  ) -> None:
    """
    - What is the agent touching? 
    - What is their temperature? Are they hot, cold?
    """
    return
