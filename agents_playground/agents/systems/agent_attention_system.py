from types import SimpleNamespace
from typing import List

from more_itertools import consume
from agents_playground.agents.cognitive_processes.agent_cognitive_process import AgentCognitiveProcess
from agents_playground.agents.default.default_agent_system import DefaultAgentSystem

from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_life_cycle_phase import AgentLifeCyclePhase
from agents_playground.agents.spec.agent_system import AgentSystem

class AgentAttentionSystem(DefaultAgentSystem):
  """
  A state of focused awareness on a subset of the available sensation 
  perception information. 
  
  A key function of attention is to identify irrelevant data and filter it out, 
  enabling significant data to be distributed to the other mental processes.

  Responsible for spinning up cognitive processes (CP). Each frame ticks away at each 
  cognitive process. A CP can have a fixed time to live that could expire if 
  certain things don't happen or are interrupted (like an injury). 
  
  A cognitive process could take various amounts of time (frames). 
  
  Question: Would it make sense for cognitive processes to be subsystems?
  My initial thought is it's not a good fit. Cognitive processes have a shelf 
  life then end where as subsystems are part of the agent and are only released
  when the agent dies.
  """
  
  def __init__(self) -> None:
    super().__init__(name = 'agent-attention')
    self.active_mental_processes: List[AgentCognitiveProcess]  = []

  def _before_subsystems_processed_pre_state_change(
    self, 
    characteristics: AgentCharacteristics, 
    parent_byproducts: dict[str, list]) -> None:
    """
    TODO: 
    - Process the sensory memory. 
    - Does a new cognitive process need to be spun up?
    """
    return
  
  def _after_subsystems_processed_pre_state_change(
    self, 
    characteristics: AgentCharacteristics, 
    parent_byproducts: dict[str, list]) -> None:
    """
    - Iterate one frame of processing for each cognitive process. 
    """
    consume(map(lambda mental_process: mental_process.think(), self.active_mental_processes)) 
    return