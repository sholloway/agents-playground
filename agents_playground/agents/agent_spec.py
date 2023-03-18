"""
Experimental module for having loosely defined agents to support project extensions.
"""

from typing import List, Protocol, Self
from abc import abstractmethod

# TODO: get rid of this. No * imports.
from agents_playground.agents.agent import *
from agents_playground.renderers.color import Color

class AgentActionStateLike(Protocol):
  name: str

class AgentActionableState(Protocol):
  ...

class AgentActionSelector(Protocol):
  @abstractmethod
  def next_action(self, current_action: AgentActionStateLike) -> AgentActionStateLike:
    ...

class AgentStateLike(Protocol):
  current_action_state: AgentActionableState     
  last_action_state: AgentActionableState | None 
  action_selector: AgentActionSelector            
  selected: bool                         
  require_scene_graph_update: bool       
  require_render: bool                   
  visible: bool                          

  @abstractmethod
  def reset(self) -> None:
    ...

  @abstractmethod
  def transition_to_next_action(self) -> None:
    ...

  @abstractmethod
  def assign_action_state(self, next_state: AgentActionableState) -> None:
    ...

  def set_visibility(self, is_visible: bool) -> None:
    self.visible = is_visible
    self.require_render = True

class AgentStyleLike(Protocol):
  stroke_thickness: float
  stroke_color: Color
  fill_color: Color
  aabb_stroke_color: Color
  aabb_stroke_thickness: float

class AgentIdentityLike(Protocol):
  id: Tag         # The ID used for the group node in the scene graph.
  toml_id: Tag    # The ID used in the TOML file.
  render_id: Tag  # The ID used for the triangle in the scene graph.
  aabb_id: Tag    # The ID used rendering the agent's AABB.

class AgentPhysicalityLike(Protocol):
  size: Size 
  aabb: AABBox 

  def calculate_aabb(self, agent_location: Coordinate, cell_size: Size) -> None:
    agent_half_width:float  = self.size.width  / 2.0
    agent_half_height:float = self.size.height / 2.0
    cell_half_width         = cell_size.width  / 2.0
    cell_half_height        = cell_size.height / 2.0

    # 1. Convert the agent's location to a canvas space.
    # agent_loc: Coordinate = cell_to_canvas(agent.location, cell_size)
    agent_loc: Coordinate = agent_location.multiply(Coordinate(cell_size.width, cell_size.height))

    # 2. Agent's are shifted to be drawn in near the center of a grid cell, 
    # the AABB needs to be shifted as well.
    agent_loc = agent_loc.shift(Coordinate(cell_half_width, cell_half_height))

    # 3. Create an AABB for the agent with the agent's location at its centroid.
    min_coord = Coordinate(agent_loc.x - agent_half_width, agent_loc.y - agent_half_height)
    max_coord = Coordinate(agent_loc.x + agent_half_width, agent_loc.y + agent_half_height)
    self.aabb = AABBox(min_coord, max_coord)

class AgentPositionLike(Protocol):
  facing: Vector2d              # The direction the agent is facing.
  location: Coordinate          # The coordinate of where the agent currently is.
  last_location: Coordinate     # The last place the agent remembers it was.
  desired_location: Coordinate  # Where the agent wants to go next.

  @abstractmethod
  def move_to(self, new_location: Coordinate):
    """Moves the agent to to a new location."""
    ...

"""
Replacing AgentMovement is tricky. It's currently using explicit knowledge of 
InterpolatedPath and using a smart counter to trigger actions. 

This needs to get a better API.

The most sophisticated we've gotten with movement is navigating a mesh.

The A* example in demos should implement this for it's linear interpolated path
based implementation.
"""
class AgentMovementAttributes(Protocol):
  """
  Responsible for storing any agent specific attributes related to movement.
  """
  ...

class AgentLike(Protocol):
  visible: bool
  initial_state: AgentStateLike     
  style: AgentStyleLike         
  identity: AgentIdentityLike   
  physicality: AgentPhysicalityLike 
  position: AgentPositionLike       
  movement: AgentMovementAttributes       
  
  def transition_state(self) -> None:
    ...

  def reset(self) -> None:
    ...

  def set_visibility(self, is_visible: bool) -> None:
    self.visible = is_visible
    self.handle_state_changed()

  def select(self) -> None:
    self.handle_agent_selected()

  @abstractmethod
  def handle_state_changed(self) -> None:
    ...

  @abstractmethod
  def handle_agent_selected(self) -> None:
    ...