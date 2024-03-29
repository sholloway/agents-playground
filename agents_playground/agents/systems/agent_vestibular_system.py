from types import SimpleNamespace
from typing import Dict, List
from agents_playground.agents.byproducts.definitions import Stimuli
from agents_playground.agents.byproducts.sensation import Sensation, SensationType
from agents_playground.agents.default.default_agent_system import SystemWithByproducts
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_life_cycle_phase import AgentLifeCyclePhase
from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.agents.spec.agent_system import AgentSystemLike
from agents_playground.agents.spec.byproduct_definition import ByproductDefinition
from agents_playground.simulation.tag import Tag

class VestibularSensation(Sensation):
  def __init__(self) -> None:
    self.type = SensationType.Vestibular

class AgentVestibularSystem(SystemWithByproducts):
  """
  Provides the sense of balance. The inner ears perceive gravity and acceleration.
  """
  def __init__(self) -> None:
    super().__init__(
      name                    = 'vestibular_system', 
      byproduct_defs          = [Stimuli], 
      internal_byproduct_defs = []
    )

  def _before_subsystems_processed_pre_state_change(
    self, 
    characteristics: AgentCharacteristics, 
    parent_byproducts: dict[str, list],
    other_agents: Dict[Tag, AgentLike]
  ) -> None:
    """What is impacting the agent's balance? Are they nauseous?"""
    self.byproducts_store.store(self.name, Stimuli.name, VestibularSensation())
