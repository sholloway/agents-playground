
from agents_playground.agents.agent_spec import AgentActionSelector, AgentActionStateLike, AgentIdentityLike, AgentLike, AgentMovementAttributes, AgentPhysicalityLike, AgentPositionLike, AgentStateLike, AgentStyleLike
from agents_playground.agents.default_agent import DefaultAgentState, MapAgentActionSelector, NamedAgentState
from agents_playground.agents.direction import Direction
from agents_playground.core.types import Coordinate, EmptyAABBox, Size
from agents_playground.renderers.color import BasicColors


EMPTY_STATE = NamedAgentState('EMPTY')

class EmptyAgentState(DefaultAgentState):
  def __init__(self) -> None:
    super().__init__(
      initial_state                         = EMPTY_STATE,   
      action_selector                       = MapAgentActionSelector({}),        
      agent_is_selected                     = False,                      
      initially_requires_scene_graph_update = False,      
      initially_requires_render             = False,                   
      is_visible                            = False 
    )

class EmptyAgentStyle(AgentStyleLike):
  def __init__(self) -> None:
    self.stroke_thickness       = 0.0
    self.stroke_color           = BasicColors.black.value
    self.fill_color             = BasicColors.black.value
    self.aabb_stroke_color      = BasicColors.black.value
    self.aabb_stroke_thickness  = 0.0

class EmptyAgentIdentity(AgentIdentityLike):
  def __init__(self) -> None:
    self.id        = 0
    self.render_id = 0
    self.toml_id   = 0
    self.aabb_id   = 0
     
class EmptyAgentPhysicality(AgentPhysicalityLike):
  def __init__(self) -> None:
    self.size = Size(0,0)
    self.aabb = EmptyAABBox()

class EmptyAgentPosition(AgentPositionLike):
  def __init__(self) -> None:
    off_canvas = Coordinate(-1,-1)
    self.facing           = Direction.EAST
    self.location         = off_canvas
    self.last_location    = off_canvas
    self.desired_location = off_canvas

  def move_to(self, new_location: Coordinate) -> None:
    pass

class EmptyAgentMovementAttributes(AgentMovementAttributes):
  pass

class NoAgent(AgentLike):
  """Convenience class for declaring no agent. (Null object pattern.)"""
  def __init__(self) -> None:
    self.agent_state = EmptyAgentState()
    self.style       = EmptyAgentStyle()
    self.identity    = EmptyAgentIdentity()
    self.physicality = EmptyAgentPhysicality()
    self.position    = EmptyAgentPosition()
    self.movement    = EmptyAgentMovementAttributes()

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