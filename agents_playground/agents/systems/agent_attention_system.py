from types import SimpleNamespace
from typing import List

from more_itertools import consume
from agents_playground.agents.cognitive_processes.agent_cognitive_process import AgentCognitiveProcess

from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_life_cycle_phase import AgentLifeCyclePhase
from agents_playground.agents.spec.agent_system import AgentSystem

class AgentAttentionSystem(AgentSystem):
  """
  A state of focused awareness on a subset of the available sensation 
  perception information. 
  
  A key function of attention is to identify irrelevant data and filter it out, 
  enabling significant data to be distributed to the other mental processes.

  Responsible for spinning up cognitive processes (CP). Each frame ticks away at each 
  cognitive process. A CP can have a fixed time to live that could expire if 
  certain things don't happen or are interrupted (like an injury). 
  """
  # A cognitive process could take various amounts of time (frames). 
  # TODO: Would it make sense for cognitive processes to be subsystems?
  # My initial thought is it's not a good fit. Cognitive processes have a shelf 
  # life then end where as subsystems are part of the agent and are only released
  # when the agent dies.
  active_mental_processes: List[AgentCognitiveProcess] 
  
  def __init__(self) -> None:
    self.name = 'agent-attention'
    self.subsystems = SimpleNamespace()

  def _before_subsystems_processed(self, characteristics: AgentCharacteristics, agent_phase: AgentLifeCyclePhase) -> None:
    """
    TODO: 
    - Process the sensory memory. 
    - Does a new cognitive process need to be spun up?
    """
    return
  
  def _after_subsystems_processed(self, characteristics: AgentCharacteristics, agent_phase: AgentLifeCyclePhase) -> None:
    """
    TODO: 
    - Iterate one frame of processing for each cognitive process. 
    """
    consume(map(lambda mental_process: mental_process.think(), self.active_mental_processes)) 
    return