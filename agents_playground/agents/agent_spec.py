"""
Experimental module for having loosely defined agents to support project extensions.
"""

from typing import Protocol
from abc import abstractmethod
from agents_playground.agents.direction import Vector2d
from agents_playground.core.types import AABBox, Coordinate, Size


from agents_playground.renderers.color import Color
from agents_playground.simulation.tag import Tag

class AgentActionStateLike(Protocol):
  name: str

class AgentActionSelector(Protocol):
  @abstractmethod
  def next_action(self, current_action: AgentActionStateLike) -> AgentActionStateLike:
    ...

class AgentStateLike(Protocol):
  current_action_state: AgentActionStateLike     
  last_action_state: AgentActionStateLike | None 
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
  def assign_action_state(self, next_state: AgentActionStateLike) -> None:
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
  """Behaves like an autonomous agent."""
  agent_state: AgentStateLike        # The internal state of the agent.
  style: AgentStyleLike              # Define's the agent's look.
  identity: AgentIdentityLike        # All of the agent's IDs.
  physicality: AgentPhysicalityLike  # The agent's physical attributes.
  position: AgentPositionLike        # All the attributes related to where the agent is.     
  movement: AgentMovementAttributes  # Attributes used for movement.
  
  def transition_state(self) -> None:
    self.before_state_change()
    self.change_state()
    self.post_state_change()

  def reset(self) -> None:
    self.agent_state.reset()

  def select(self) -> None:
    self.agent_state.selected = True
    self.handle_agent_selected()

  def deselect(self) -> None:
    self.agent_state.selected = False
    self.handle_agent_deselected()

  @property
  def selected(self) -> bool:
    return self.agent_state.selected
  
  @property
  def agent_scene_graph_changed(self) -> bool:
    return self.agent_state.require_scene_graph_update
  
  @property
  def agent_render_changed(self) -> bool:
    return self.agent_state.require_render

  def change_state(self) -> None:
    self.agent_state.transition_to_next_action()

  def face(self, direction: Vector2d) -> None:
    """Set the direction the agent is facing."""
    self.position.facing = direction
    self.agent_state.require_scene_graph_update = True

  def move_to(self, new_location: Coordinate, cell_size: Size) -> None:
    """Update the agent's location."""
    self.position.move_to(new_location)
    self.agent_state.require_scene_graph_update = True
    self.physicality.calculate_aabb(self.position.location, cell_size)
  
  @abstractmethod
  def before_state_change(self) -> None:
    """Optional hook to trigger behavior when an agent is selected."""
    ...

  @abstractmethod
  def post_state_change(self) -> None:
    """Optional hook to trigger behavior when an agent is selected."""
    ...
 
  @abstractmethod
  def handle_agent_selected(self) -> None:
    """Optional hook to trigger behavior when an agent is selected."""
    ...
  
  @abstractmethod
  def handle_agent_deselected(self) -> None:
    """Optional hook to trigger behavior when an agent is deselected."""
    ...