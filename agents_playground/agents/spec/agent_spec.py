"""
Experimental module for having loosely defined agents to support project extensions.
"""
from typing import Protocol
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics

from agents_playground.agents.spec.agent_identity_spec import AgentIdentityLike
from agents_playground.agents.spec.agent_life_cycle_phase import AgentLifeCyclePhase
from agents_playground.agents.spec.agent_movement_attributes import AgentMovementAttributes
from agents_playground.agents.spec.agent_physicality_spec import AgentPhysicalityLike
from agents_playground.agents.spec.agent_position_spec import AgentPositionLike
from agents_playground.agents.spec.agent_state_spec import AgentStateLike
from agents_playground.agents.spec.agent_style_spec import AgentStyleLike
from agents_playground.agents.spec.agent_system import AgentSystem
from agents_playground.agents.direction import Vector2d
from agents_playground.core.types import Coordinate, Size

class AgentLike(Protocol):
  """Behaves like an autonomous agent."""
  agent_state: AgentStateLike        # The internal state of the agent.
  internal_systems: AgentSystem      # The subsystems that compose the agent.
  
  identity: AgentIdentityLike        # All of the agent's IDs.
  physicality: AgentPhysicalityLike  # The agent's physical attributes.
  position: AgentPositionLike        # All the attributes related to where the agent is.     
  movement: AgentMovementAttributes  # Attributes used for movement.
  style: AgentStyleLike              # Define's the agent's look.
  
  def transition_state(self) -> None:
    characteristics = self.agent_characteristics()
    self.before_state_change(characteristics)
    self.pre_state_change_process_subsystems(characteristics)
    self.change_state(characteristics)
    self.post_state_change_process_subsystems(characteristics)
    self.post_state_change(characteristics)

  def change_state(self, characteristics: AgentCharacteristics) -> None:
    self.agent_state.transition_to_next_action(characteristics)

  def agent_characteristics(self) -> AgentCharacteristics:
    return AgentCharacteristics(
        self.identity, 
        self.physicality,
        self.position,
        self.movement,
        self.style
      )

  def reset(self) -> None:
    self.agent_state.reset()

  def select(self) -> None:
    self.agent_state.selected = True
    self.handle_agent_selected()

  def deselect(self) -> None:
    self.agent_state.selected = False
    self.handle_agent_deselected()

  def face(self, direction: Vector2d) -> None:
    """Set the direction the agent is facing."""
    self.position.facing = direction
    self.agent_state.require_scene_graph_update = True

  def move_to(self, new_location: Coordinate, cell_size: Size) -> None:
    """Update the agent's location."""
    self.position.move_to(new_location)
    self.agent_state.require_scene_graph_update = True
    self.physicality.calculate_aabb(self.position.location, cell_size)
  
  @property
  def selected(self) -> bool:
    return self.agent_state.selected
  
  @property
  def agent_scene_graph_changed(self) -> bool:
    return self.agent_state.require_scene_graph_update
  
  @property
  def agent_render_changed(self) -> bool:
    return self.agent_state.require_render
  
  def before_state_change(self, characteristics: AgentCharacteristics) -> None:
    """Optional hook to trigger behavior when an agent is selected."""
    return

  def post_state_change(self, characteristics: AgentCharacteristics) -> None:
    """Optional hook to trigger behavior when an agent is selected."""
    return 
 
  def handle_agent_selected(self) -> None:
    """Optional hook to trigger behavior when an agent is selected."""
    return
  
  def handle_agent_deselected(self) -> None:
    """Optional hook to trigger behavior when an agent is deselected."""
    return
  
  def pre_state_change_process_subsystems(self, characteristics: AgentCharacteristics) -> None:
    self.internal_systems.process(characteristics, AgentLifeCyclePhase.PRE_STATE_CHANGE)
  
  def post_state_change_process_subsystems(self, characteristics: AgentCharacteristics) -> None:
    self.internal_systems.process(characteristics, AgentLifeCyclePhase.POST_STATE_CHANGE)