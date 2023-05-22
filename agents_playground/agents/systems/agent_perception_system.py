from types import SimpleNamespace
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_life_cycle_phase import AgentLifeCyclePhase
from agents_playground.agents.spec.agent_system import AgentSystem


class AgentPerceptionSystem(AgentSystem):
  """
  The organization, identification, and interpretation of sensory information in 
  order to represent and understand the presented information or environment.
  """

  def __init__(self) -> None:
    self.name = 'agent-perception'
    self.subsystems = SimpleNamespace()

  def before_subsystems_processed(self, characteristics: AgentCharacteristics, agent_phase: AgentLifeCyclePhase) -> None:
    """
    TODO: Collect all sensory information that the agent is experiencing.
    """
    return
  
  def after_subsystems_processed(self, characteristics: AgentCharacteristics, agent_phase: AgentLifeCyclePhase) -> None:
    """
    TODO: Prepare the stimuli for the attention subsystem.
    - This could mean storing it in one of the Agent's memory stores.
    """
    return