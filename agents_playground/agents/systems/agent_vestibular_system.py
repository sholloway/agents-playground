from types import SimpleNamespace
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_life_cycle_phase import AgentLifeCyclePhase
from agents_playground.agents.spec.agent_system import AgentSystem

class AgentVestibularSystem(AgentSystem):
  """
  Provides the sense of balance. The inner ears perceive gravity and acceleration.
  """
  def __init__(self) -> None:
    self.name = 'vestibular-system'
    self.subsystems = SimpleNamespace()

  def before_subsystems_processed(self, characteristics: AgentCharacteristics, agent_phase: AgentLifeCyclePhase) -> None:
    """What is impacting the agent's balance? Are they nauseous?"""
    return
