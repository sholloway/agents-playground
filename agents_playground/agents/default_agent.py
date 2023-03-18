
from typing import Callable
from agents_playground.agents.agent_spec import (
  AgentActionSelector,
  AgentActionStateLike,
  AgentActionStateLike,
  AgentIdentityLike, 
  AgentLike, 
  AgentMovementAttributes, 
  AgentPhysicalityLike, 
  AgentPositionLike, 
  AgentStateLike, 
  AgentStyleLike
)
from agents_playground.agents.direction import Vector2d
from agents_playground.core.types import AABBox, Coordinate, EmptyAABBox, Size
from agents_playground.funcs import map_get_or_raise
from agents_playground.renderers.color import BasicColors, Color
from agents_playground.simulation.tag import Tag

class NamedAgentState(AgentActionStateLike):
  def __init__(self, name: str) -> None:
    self.name = name

class MapAgentActionSelectorException(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

class MapAgentActionSelector(AgentActionSelector):
  def __init__(
    self, 
    state_map: dict[AgentActionStateLike, AgentActionStateLike]
  ) -> None:
    self._state_map: dict[AgentActionStateLike, AgentActionStateLike] = state_map

  def next_action(self, current_action: AgentActionStateLike) -> AgentActionStateLike:
    return map_get_or_raise(
      self._state_map, 
      current_action, 
      MapAgentActionSelectorException(
        f'The Agent state map does not have a registered state named {current_action}'
      )
    ) 

  def __repr__(self) -> str:
    """An implementation of the dunder __repr__ method. Used for debugging."""
    model_rep = ''
    for k,v in self.model.items():
      model_rep = model_rep + f'{k} -> {v}\n'
    return f'{self.__class__.__name__}\n{model_rep}' 

class DefaultAgentState(AgentStateLike):
  def __init__(
    self, 
    initial_state: AgentActionStateLike, 
    action_selector: AgentActionSelector,
    agent_is_selected: bool = False,
    initially_requires_scene_graph_update: bool = False,
    initially_requires_render: bool             = False,
    is_visible: bool                            = True
  ) -> None:
    self.current_action_state: AgentActionStateLike     = initial_state   
    self.last_action_state: AgentActionStateLike | None = None
    self.action_selector: AgentActionSelector           = action_selector        
    self.selected: bool                                 = agent_is_selected                      
    self.require_scene_graph_update: bool               = initially_requires_scene_graph_update      
    self.require_render: bool                           = initially_requires_render                   
    self.visible: bool                                  = is_visible  

  def reset(self) -> None:
    self.require_scene_graph_update = False
    self.require_render = False

  def transition_to_next_action(self) -> None:
    self.last_action_state    = self.current_action_state
    self.current_action_state = self.action_selector.next_action(self.current_action_state)

  def assign_action_state(self, next_state: AgentActionStateLike) -> None:
    self.last_action_state    = self.current_action_state
    self.current_action_state = next_state

class DefaultAgentStyle(AgentStyleLike):
  def __init__(
    self, 
    stroke_thickness: float      = 1.0, 
    stroke_color: Color          = BasicColors.black.value,
    fill_color: Color            = BasicColors.blue.value,
    aabb_stroke_color: Color     = BasicColors.red.value,
    aabb_stroke_thickness: float = 1.0
  ) -> None:
    self.stroke_thickness       = stroke_thickness
    self.stroke_color           = stroke_color
    self.fill_color             = fill_color
    self.aabb_stroke_color      = aabb_stroke_color
    self.aabb_stroke_thickness  = aabb_stroke_thickness

class DefaultAgentIdentity(AgentIdentityLike):
  def __init__(self, id_generator: Callable[...,Tag]) -> None:
    self.id         = id_generator()
    self.render_id  = id_generator()
    self.toml_id    = id_generator()
    self.aabb_id    = id_generator()  

class DefaultAgentPhysicality(AgentPhysicalityLike):
  def __init__(self, size: Size, aabb: AABBox = EmptyAABBox()) -> None:
    self.size = size
    self.aabb = aabb

class DefaultAgentPosition(AgentPositionLike):
  def __init__(
    self, 
    facing: Vector2d, 
    location: Coordinate, 
    last_location: Coordinate, 
    desired_location: Coordinate
  ) -> None:
    self.facing           = facing
    self.location         = location
    self.last_location    = last_location
    self.desired_location = desired_location

  def move_to(self, new_location: Coordinate) -> None:
    self.last_location = self.location
    self.location = new_location


class DefaultAgentMovementAttributes(AgentMovementAttributes):
  """By default there aren't any movement specific attributes"""
  def __init__(self) -> None:
    ...

class DefaultAgent(AgentLike):
  def __init__(
    self, 
    initial_state: AgentStateLike, 
    style: AgentStyleLike,
    identity: AgentIdentityLike,
    physicality: AgentPhysicalityLike,
    position: AgentPositionLike,
    movement: AgentMovementAttributes
  ) -> None:
    """Creates a new instance of an agent.
    
    Args:
      initial_state - The initial configuration for the various state fields.
      style - Define's the agent's look.
      identity - All of the agent's IDs.
      physicality - The agent's physical attributes.
      position - All the attributes related to where the agent is.
      movement - Attributes used for movement.
    """
    self.agent_state = initial_state
    self.style       = style
    self.identity    = identity
    self.physicality = physicality
    self.position    = position
    self.movement    = movement
 
  def before_state_change(self) -> None:
    """Optional hook to trigger behavior when an agent is selected."""
    pass

  def post_state_change(self) -> None:
    """Optional hook to trigger behavior when an agent is selected."""
    pass
 
  def handle_agent_selected(self) -> None:
    """Optional hook to trigger behavior when an agent is selected."""
    pass
  
  def handle_agent_deselected(self) -> None:
    """Optional hook to trigger behavior when an agent is deselected."""
    pass