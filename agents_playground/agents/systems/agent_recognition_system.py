
from typing import Dict, List
from agents_playground.agents.byproducts.sensation import Sensation
from agents_playground.agents.default.default_agent_system import SystemWithByproducts
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.agents.systems.agent_visual_system import VisualSensation
from agents_playground.simulation.tag import Tag

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
DEFAULT_RECOGNITION_TTL: int = 60 * 7

class AgentRecognitionSystem(SystemWithByproducts):
  def __init__(self) -> None:
    super().__init__(
      name = 'recognition_system', 
      byproduct_defs = [], 
      internal_byproduct_defs = []
    )

  def _before_subsystems_processed_pre_state_change(
    self, 
    characteristics: AgentCharacteristics, 
    parent_byproducts: dict[str, list],
    other_agents: List[AgentLike]
  ) -> None:
    """
    Looks at the agent's sensory memory for instances of VisualSensation.
    If another agent was seen, the recognition system determines if the other
    agent is recognized or not. This is currently handled by calculating the 
    Manhattan distance between the two agents. If the distance is less than 
    a threshold, then the other agent is recognized.  

    The recognition of the other agent is placed into the working memory.
    """
    sensed_agents: List[VisualSensation] = [
      sense for sense in characteristics.memory.sensory_memory.memory_store 
      if isinstance(sense, VisualSensation)
    ]

    if len(sensed_agents) < 1:
      # Save time by stopping early.
      return
    
    # Build a dict
    # TODO: Move this up the chain. Have the hierarchy of systems expect a dict.   
    other_agents_map: Dict[Tag, AgentLike] = {
      agent.identity.id: agent 
      for agent in other_agents
    }

    seen_agent: VisualSensation
    for seen_agent in sensed_agents:
      for agent_id in seen_agent.seen:
        other_agent: AgentLike = other_agents_map[agent_id]
        seen_distance: float =  characteristics.position.location.find_distance(other_agent.position.location)
        if seen_distance <= DEFAULT_RECOGNITION_THRESHOLD:
          # The agent recognizes the other agent. Record this in the working memory.
          characteristics.memory.working_memory.recognitions.store(other_agent.identity.id, DEFAULT_RECOGNITION_TTL)  