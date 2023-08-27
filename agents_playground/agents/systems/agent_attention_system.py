from types import SimpleNamespace
from typing import Dict, List

from more_itertools import consume
from agents_playground.agents.byproducts.sensation import Sensation
from agents_playground.agents.cognitive_processes.agent_cognitive_process import Thought
from agents_playground.agents.default.default_agent_system import DefaultAgentSystem
from agents_playground.agents.memory.memory import Memory

from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.agents.spec.agent_system import SystemMemoryError
from agents_playground.agents.systems.agent_auditory_system import AuditorySensation
from agents_playground.agents.systems.agent_visual_system import VisualSensation
from agents_playground.containers.ttl_store import TTLStore
from agents_playground.fp.containers import FPList
from agents_playground.simulation.tag import Tag

def internal_musing(store, item):
  print(f'thinking stuff: {item}')

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
  
  def __init__(self, input_memory_container:str = 'sensory_memory') -> None:
    super().__init__(name = 'agent_attention')
    self._input_memory_container = input_memory_container
   #self.active_mental_processes: List[AgentCognitiveProcess]  = [] # TODO: Change to a TTLStore.
    self.active_mental_processes = TTLStore[Thought]()

  def _before_subsystems_processed_pre_state_change(
    self, 
    characteristics: AgentCharacteristics, 
    parent_byproducts: dict[str, list],
    other_agents: Dict[Tag, AgentLike]
  ) -> None:
    """
    TODO: Process the sensory memory. 
    - Does a new cognitive process need to be spun up?

    What is the logic for spinning up a particular type of cognitive process 
    based on stimuli?
     - How can this be defined in a simulation agnostic way?
     - Should I repurpose the fuzzy state map?
     - One consideration is that a sim can register it's own system to include.
       So, if the mapping in this system isn't appropriate, another System can 
       be used in a sim.
    """
    try:
      sensory_memories: FPList[Memory] =  characteristics.memory['sensory_memory'].unwrap()
    except KeyError:
      error_msg = f'AgentAttentionSystem requires the agent has a MemoryContainer named {self._input_memory_container}.'
      raise SystemMemoryError(error_msg)

    for sense in sensory_memories:
      match sense.unwrap():
        case VisualSensation():
          self.active_mental_processes.store(Thought(), 30, internal_musing)
        case AuditorySensation():
          self.active_mental_processes.store(Thought(), 30)
  
  def _after_subsystems_processed_pre_state_change(
    self, 
    characteristics: AgentCharacteristics, 
    parent_byproducts: dict[str, list], 
    other_agents: Dict[Tag, AgentLike]
  ) -> None:
    """
    - Iterate one frame of processing for each cognitive process. 
    """
    # consume(map(lambda mental_process: mental_process.think(), self.active_mental_processes)) 
    self.active_mental_processes.tick()
    return