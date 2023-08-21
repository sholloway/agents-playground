"""
Experimental module for having loosely defined agents to support project extensions.
"""

from __future__ import annotations

from typing import Dict, List, Protocol
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_memory_spec import AgentMemoryLike

from agents_playground.agents.spec.agent_system import AgentSystemLike
from agents_playground.agents.spec.agent_identity_spec import AgentIdentityLike
from agents_playground.agents.spec.agent_life_cycle_phase import AgentLifeCyclePhase
from agents_playground.agents.spec.agent_movement_attributes import AgentMovementAttributes
from agents_playground.agents.spec.agent_physicality_spec import AgentPhysicalityLike
from agents_playground.agents.spec.agent_position_spec import AgentPositionLike
from agents_playground.agents.spec.agent_state_spec import AgentStateLike
from agents_playground.agents.spec.agent_style_spec import AgentStyleLike
from agents_playground.agents.spec.tick import Tick as FrameTick
from agents_playground.core.types import  Size
from agents_playground.simulation.tag import Tag
from agents_playground.spatial.types import Coordinate
from agents_playground.spatial.vector import Vector

class AgentLike(FrameTick, Protocol):
  """Behaves like an autonomous agent."""
  agent_state: AgentStateLike        # The internal state of the agent.
  internal_systems: AgentSystemLike  # The subsystems that compose the agent.
  identity: AgentIdentityLike        # All of the agent's IDs.
  physicality: AgentPhysicalityLike  # The agent's physical attributes.
  position: AgentPositionLike        # All the attributes related to where the agent is.     
  movement: AgentMovementAttributes  # Attributes used for movement.
  style: AgentStyleLike              # Define's the agent's look.
  memory: AgentMemoryLike           # The memory store for the agent.

  """
  Thoughts:
  - Have mortality be built in as a subsystem that is counting down. 

  System Hierarchy
  - Physical Systems
    - Mortality: Controls if and when an agent dies.
    - Nervous System
    - Etc
  - Mental Systems
    - AgentPerception
    - AgentAttention
  - Personality Systems
    - TBD
    - Note: Personality may feed into emotional systems. 
      - Example: Prone to depression may make it more likely to respond as sad.
  - Emotional Systems
    - TBD
  """
  
  def transition_state(self, other_agents: Dict[Tag, AgentLike]) -> None:
    """
    Moves the agent forward one tick in the simulation.
    """
    characteristics = self.agent_characteristics()
    self._before_state_change(characteristics)
    self._pre_state_change_process_subsystems(characteristics, other_agents)
    self._change_state(characteristics)
    self._post_state_change_process_subsystems(characteristics, other_agents)
    self._post_state_change(characteristics)

  def tick(self) -> None:
    """Signifies the passing of a simulation frame."""
    self.memory.tick()

  def _change_state(self, characteristics: AgentCharacteristics) -> None:
    self.agent_state.transition_to_next_action(characteristics)

  def agent_characteristics(self) -> AgentCharacteristics:
    """Bundles the agent characteristics."""
    return AgentCharacteristics(
        self.identity, 
        self.physicality,
        self.position,
        self.movement,
        self.style,
        self.memory
      )

  def reset(self) -> None:
    """Reset the agent state."""
    self.agent_state.reset()

  def select(self) -> None:
    """Marks the agent as selected by the user or Simulation."""
    self.agent_state.selected = True
    self._handle_agent_selected()

  def deselect(self) -> None:
    """Marks the agent as deselected by the user or Simulation."""
    self.agent_state.selected = False
    self._handle_agent_deselected()

  def face(self, direction: Vector, cell_size: Size) -> None:
    """Set the direction the agent is facing."""
    self.agent_state.require_scene_graph_update = True
    self.position.facing = direction
    self.physicality.frustum.update(self.position.location, self.position.facing, cell_size)

  def move_to(self, new_location: Coordinate, cell_size: Size) -> None:
    """Update the agent's location."""
    self.agent_state.require_scene_graph_update = True
    self.position.move_to(new_location)
    self.physicality.calculate_aabb(self.position.location, cell_size)
    self.physicality.frustum.update(self.position.location, self.position.facing, cell_size)

  def scale(self, amount: float) -> None:
    """Applies a scaling factor to the agent's size along both axes."""
    self.physicality.scale_factor = amount
    self.agent_state.require_scene_graph_update = True
  
  @property
  def selected(self) -> bool:
    """Getter for the Agent's selected status."""
    return self.agent_state.selected
  
  @property
  def agent_scene_graph_changed(self) -> bool:
    """Indicates if the agent requires a scene graph update."""
    return self.agent_state.require_scene_graph_update
  
  @property
  def agent_render_changed(self) -> bool:
    """Indicates if the agent requires a re-render."""
    return self.agent_state.require_render
  
  def _before_state_change(self, characteristics: AgentCharacteristics) -> None:
    """Optional hook to trigger behavior when an agent is selected."""
    return

  def _post_state_change(self, characteristics: AgentCharacteristics) -> None:
    """Optional hook to trigger behavior when an agent is selected."""
    return 
 
  def _handle_agent_selected(self) -> None:
    """Optional hook to trigger behavior when an agent is selected."""
    return
  
  def _handle_agent_deselected(self) -> None:
    """Optional hook to trigger behavior when an agent is deselected."""
    return
  
  def _pre_state_change_process_subsystems(self, characteristics: AgentCharacteristics, other_agents: Dict[Tag, AgentLike]) -> None:
    """Internal hook responsible for processing the subsystems before the agent's status changes."""
    self.internal_systems.process(characteristics, AgentLifeCyclePhase.PRE_STATE_CHANGE, other_agents)
  
  def _post_state_change_process_subsystems(self, characteristics: AgentCharacteristics, other_agents: Dict[Tag, AgentLike]) -> None:
    """Internal hook responsible for processing the subsystems before the agents status changes."""
    self.internal_systems.process(characteristics, AgentLifeCyclePhase.POST_STATE_CHANGE, other_agents)