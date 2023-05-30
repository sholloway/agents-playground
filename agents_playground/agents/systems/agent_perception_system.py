from agents_playground.agents.byproducts.definitions import Stimuli
from agents_playground.agents.byproducts.sensation import Sensation
from agents_playground.agents.default.default_agent_system import SystemWithByproducts
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_life_cycle_phase import AgentLifeCyclePhase
from agents_playground.agents.spec.byproduct_definition import ByproductDefinition

class AgentPerceptionSystem(SystemWithByproducts):
  """
  Processes stimuli. What the agent is aware of.
  The organization, identification, and interpretation of sensory information in 
  order to represent and understand the presented information or environment.
  """
  def __init__(self) -> None:
    super().__init__(
      name                    = 'agent_perception', 
      byproduct_defs          = [], 
      internal_byproduct_defs = []
    )

  def _before_subsystems_processed_pre_state_change(
    self, 
    characteristics: AgentCharacteristics, 
    parent_byproducts: dict[str, list]
  ) -> None:
    """
    Collect all sensory information that the agent is experiencing.
    """
    if Stimuli.name in parent_byproducts:  
      sensation: Sensation
      for sensation in parent_byproducts[Stimuli.name]:
        characteristics.memory.sensory_memory.sense(sensation)