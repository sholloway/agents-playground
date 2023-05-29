from types import SimpleNamespace
from typing import List
from agents_playground.agents.byproducts.sensation import Sensation
from agents_playground.agents.default.default_agent_system import SystemWithByproducts
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_life_cycle_phase import AgentLifeCyclePhase
from agents_playground.agents.spec.agent_system import AgentSystem, ByproductDefinition
from agents_playground.agents.spec.byproduct_definition import ByproductDefinition

class AgentGustatorySystem(SystemWithByproducts):
  """
  Provides the sense of taste. The mouth perceives chemicals.
  """  
  def __init__(self) -> None:
    super().__init__(
      name                    = 'gustatory-system', 
      byproduct_defs          = [ByproductDefinition('stimuli', Sensation)], 
      internal_byproduct_defs = []
    )

  def _before_subsystems_processed(self, characteristics: AgentCharacteristics, agent_phase: AgentLifeCyclePhase) -> None:
    """
    - Is there anything in the agent's mouth? What does it taste like? 
    """
    return
