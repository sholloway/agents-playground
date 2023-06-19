from types import SimpleNamespace
from typing import Dict, List, Tuple

from agents_playground.agents.byproducts.definitions import Stimuli
from agents_playground.agents.byproducts.sensation import Sensation, SensationType
from agents_playground.agents.default.default_agent_system import SystemWithByproducts
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.simulation.tag import Tag

class VisualSensation(Sensation):
  def __init__(self, seen: Tuple[Tag, ...]) -> None:
    self.type = SensationType.Visual
    self.seen: Tuple[Tag, ...] = seen

  def __repr__(self) -> str:
    return f'{self.__class__.__name__}(type={self.type}, seen={self.seen})'
  
  def __key(self) -> Tuple[SensationType, Tuple[Tag, ...]]:
    return (self.type, self.seen)
    
  def __hash__(self) -> int:
    return hash(self.__key())
  
  def __eq__(self, other: object) -> bool:
    if isinstance(other, VisualSensation):
      return self.__key() == other.__key()
    return False    
  


class AgentVisualSystem(SystemWithByproducts):
  """
  Provides the sense of sight. The eyes perceive light.
  """
  def __init__(self) -> None:
    super().__init__(
      name                    = 'visual_system', 
      byproduct_defs          = [Stimuli], 
      internal_byproduct_defs = []
    )

  """
  Thoughts:
  The default sim is a top down model. That doesn't have to be the case though.

  Top Down Model:
  - Agent has a physical orientation. (2d vector)
  - The agent has a view frustum. In 2d this can be a simple triangle.
    Rather than ray casting, an agent can "see something" if:
    1. That something intersects with the agent's view frustum.
    2. A ray cast from the agent to the "something" does not have any other
       collision first.
  """
  def _before_subsystems_processed_pre_state_change(
    self, 
    characteristics: AgentCharacteristics, 
    parent_byproducts: Dict[str, List],
    other_agents: List[AgentLike]
  ) -> None:
    """What does the agent see?"""

    # Given the agent's view frustum, what can the agent see?
    # characteristics.physicality.frustum
    
    # For the moment, let's use brute force.
    # Just check every agent in the scene minus this one.
    can_see_agent_ids: List[Tag] = []
    other_agent: AgentLike
    for other_agent in other_agents:
      if characteristics.physicality.frustum.intersect(other_agent.physicality.aabb):
        can_see_agent_ids.append(other_agent.identity.id)

    self.byproducts_store.store(self.name, Stimuli.name, VisualSensation(tuple(can_see_agent_ids)))

"""
    The implementation of the life systems are each nontrivial. They should be on 
    their own branch.
    The challenge here, is the agent needs access to the scene.
    The other agents, the entities. Lights whatever. 

    How does a sim work?
    SimLoop -> _process_sim_cycle()
      TaskScheduler -> consume() the queued Tasks
        A Scene Specific Task -> Loop through Agents in a scene
          Agent -> transition_state() 

    We shouldn't pass the entire scene in. This will create recursive dependencies. 
    Just pass the entities and agents.
    
    Need to filter active the active agent out early so the agent isn't testing 
    if it sees itself.

    This is probably where performance is going to get harder.
    Ray casting is expensive.

    I could do something similar to the Conway's game. Have a data structure
    that associates the agent's cell location. Then find the cells that the view 
    frustum overlaps, then just select those agents.
    Use a triangle for an agent's view frustum to simplify the intersection tests.

    Then cast a ray from the agent to each of the filtered agents and check if anything 
    intersects first.

    Considerations
    - Could navigation meshes help reduce the search space?
    - Do research on 
      - Line of Sight 
        - Ray Checks
          - Naive approach is to simply do a ray cast from the active agent
            to all of the other active agents. Does anything occlude it?
        - Distance
          - Needs to be a three tier range of "I know who you are" to "I know that's a person" to "I can't make that out".
          - This should be sim specific.
      - Sense Management
      - Sensory Perception
      - What are options for WebGPU in Python? WGSL is the GPU language.

    Algorithm
    1. Prepare the structure that organize Agents by their current location.
    2. Prepare the structure that organizes the static entities by their current location.
       Note: We may be able to get away with doing this step just once.
       Note: This is sim specific.
    3. Filter out any agent that is sleeping or otherwise inactive.
    4. For agent in the active agents.
      A. Calculate the agent's view frustum from their facing vector.
    5. For agent in the active agents.
      A. Find the cells that the agent's view Frustum intersects.
      B. Find any agents that are in the cells from the last step.
      For each selected agent, 
        1. Cast a ray from the active agent to the selected agent.
        2. Determine if anything else (entities, other agents) intersects that ray.
           If the answer is no, then active agent can "see" the selected agent.
           The visual system should store a Sensation memory in its Stimuli byproduct.
           Associate the seen agent's ID in the sensation memory.


    Pipeline Approach
    We can use a general proximity filter for all nervous system subsystems.
    Perhaps the Nervous System is responsible for that or create a new system 
    such as Proximity System.

    Filter Agents (proximity test) -> Filter Entities (proximity test) ->  


    Classic Approach
    - Organize the work into two phases: broad tests, narrow tests.
    """