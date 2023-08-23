
from typing import Dict, List
from agents_playground.agents.byproducts.sensation import Sensation
from agents_playground.agents.default.default_agent_system import SystemWithByproducts
from agents_playground.agents.memory.agent_memory_model import AgentMemoryModel
from agents_playground.agents.memory.memory import Memory
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.agents.spec.agent_system import SystemMemoryError
from agents_playground.agents.systems.agent_visual_system import VisualSensation
from agents_playground.containers.ttl_store import TTLStore
from agents_playground.core.constants import TARGET_FRAMES_PER_SEC
from agents_playground.fp.containers import FPList
from agents_playground.simulation.tag import Tag
from agents_playground.spatial.types import Coordinate

"""
The maximum distance this agent can recognize another agent.
Note, this is different from seeing another agent. We can 
See other people in the distance, but not recognize them 
due to lightning, weather conditions, or physical limitations.

The distance is between two grid coordinates (agent.position.location). 
Not canvas space.
"""
DEFAULT_RECOGNITION_THRESHOLD: int = 16

"""
The number of frames the memory of an agent recognizing another agent remains 
in their working memory.
"""
DEFAULT_RECOGNITION_TTL: int = int(TARGET_FRAMES_PER_SEC * 2)

class AgentRecognitionSystem(SystemWithByproducts):
  def __init__(
    self, 
    input_memory_container:str = 'sensory_memory',
    output_memory_container:str = 'working_memory'
  ) -> None:
    super().__init__(
      name = 'recognition_system', 
      byproduct_defs = [], 
      internal_byproduct_defs = []
    )
    self._input_memory_container = input_memory_container
    self._output_memory_container = output_memory_container

  def _before_subsystems_processed_pre_state_change(
    self, 
    characteristics: AgentCharacteristics, 
    parent_byproducts: dict[str, list],
    other_agents: Dict[Tag, AgentLike]
  ) -> None:
    """
    Looks at the agent's sensory memory for instances of VisualSensation.
    If another agent was seen, the recognition system determines if the other
    agent is recognized or not. This is currently handled by calculating the 
    Manhattan distance between the two agents. If the distance is less than 
    a threshold, then the other agent is recognized.  

    The recognition of the other agent is placed into the working memory.
    """
    sensed_agents: FPList[VisualSensation] = self._filter_visual_sensations(characteristics.memory)

    if len(sensed_agents) < 1:
      # Save time by stopping early.
      return

    characteristics.position.location
    self._attempt_recognition(
      characteristics.position.location, 
      characteristics.memory, 
      other_agents, 
      sensed_agents
    )
    
  def _filter_visual_sensations(self, agent_memory: AgentMemoryModel) -> FPList[VisualSensation]:
    try:
      input_memories:FPList[Memory] = agent_memory[self._input_memory_container].unwrap()
      sensed_agents: List[VisualSensation] = [
        sense_memory.unwrap() for sense_memory in input_memories 
        if isinstance(sense_memory.unwrap(), VisualSensation)
      ]
      return FPList(sensed_agents)
    except KeyError:
      error_msg = f'AgentRecognitionSystem requires the agent has a MemoryContainer named {self._input_memory_container}.'
      raise SystemMemoryError(error_msg)
    
  def _attempt_recognition(
    self, 
    current_location: Coordinate,
    agent_memory: AgentMemoryModel, 
    other_agents: Dict[Tag, AgentLike],
    sensed_agents: FPList[VisualSensation]):
    try:
      working_memories:TTLStore[Memory] = agent_memory[self._output_memory_container].unwrap()
      seen_agent: VisualSensation
      for seen_agent in sensed_agents:
        for agent_id in seen_agent.seen:
          other_agent: AgentLike = other_agents[agent_id]
          seen_distance: float =  current_location.find_distance(other_agent.position.location)
          if seen_distance <= DEFAULT_RECOGNITION_THRESHOLD:
            # The agent recognizes the other agent. Record this in the working memory.
            working_memories.store(Memory[Tag, None](other_agent.identity.id), DEFAULT_RECOGNITION_TTL)  
    except KeyError:
      error_msg = f'AgentRecognitionSystem requires the agent has a MemoryContainer named {self._output_memory_container}.'
      raise SystemMemoryError(error_msg)