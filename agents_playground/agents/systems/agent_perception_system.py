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
      name                    = 'agent-perception', 
      byproduct_defs          = [ByproductDefinition('stimuli', Sensation)], 
      internal_byproduct_defs = []
    )

  def _before_subsystems_processed(self, characteristics: AgentCharacteristics, agent_phase: AgentLifeCyclePhase) -> None:
    """
    TODO: Collect all sensory information that the agent is experiencing.
    """
    return
  
  def _after_subsystems_processed(self, characteristics: AgentCharacteristics, agent_phase: AgentLifeCyclePhase) -> None:
    """
    TODO: Prepare the stimuli for the attention subsystem.
    - This could mean storing it in one of the Agent's memory stores.
    """
    return