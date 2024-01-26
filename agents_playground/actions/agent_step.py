from agents_playground.actions.agent_action import AgentAction
from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.legacy.scene.scene import Scene
from agents_playground.spatial.coordinate import Coordinate

from agents_playground.spatial.vector.vector2d import Vector2d

class AgentStep(AgentAction):
  """A waypoint in a path.
  
  A step represents a change in an agent along a path. This could be a 
  change in location or orientation or both.
  """
  def __init__(self, 
    location: Coordinate | None = None, 
    orientation: Vector2d | None = None) -> None:
    super().__init__()
    self._location: Coordinate | None = location
    self._orientation: Vector2d | None = orientation

  def _perform(self, agent: AgentLike, **data):
    """
    Implements AgentAction.perform.
    Moves the agent to an optional location and orientates the agent to an 
    optional direction.
    """
    scene: Scene = data['scene']
    if self._location :
      agent.move_to(self._location, scene.cell_size)
    if self._orientation:
      agent.face(self._orientation, scene.cell_size)

  @property
  def location(self) -> Coordinate | None:
    return self._location
