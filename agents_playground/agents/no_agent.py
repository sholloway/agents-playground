
from types import SimpleNamespace
from typing import Dict, List, Set, Tuple
from agents_playground.agents.byproducts.sensation import Sensation
from agents_playground.agents.default.default_agent_state import DefaultAgentState
from agents_playground.agents.default.map_agent_action_selector import MapAgentActionSelector
from agents_playground.agents.default.named_agent_state import NamedAgentActionState

from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_identity_spec import AgentIdentityLike
from agents_playground.agents.spec.agent_memory_spec import AgentMemoryLike, Fact, LongTermMemoryLike, Memory, Relationship, SensoryMemoryLike, Skill, WorkingMemoryLike
from agents_playground.agents.spec.agent_movement_attributes import AgentMovementAttributes
from agents_playground.agents.spec.agent_physicality_spec import AgentPhysicalityLike
from agents_playground.agents.spec.agent_position_spec import AgentPositionLike
from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.agents.spec.agent_style_spec import AgentStyleLike
from agents_playground.agents.spec.agent_system import AgentSystem
from agents_playground.core.types import Size
from agents_playground.renderers.color import BasicColors
from agents_playground.simulation.tag import Tag
from agents_playground.spatial.aabbox import EmptyAABBox
from agents_playground.spatial.direction import Direction
from agents_playground.spatial.types import Coordinate


EMPTY_STATE = NamedAgentActionState('EMPTY')

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
    self.id         = 0
    self.render_id  = 0
    self.toml_id    = 0
    self.aabb_id    = 0
    self.frustum_id = 0
     
class EmptyAgentPhysicality(AgentPhysicalityLike):
  def __init__(self) -> None:
    self.size = Size(0,0)
    self.aabb = EmptyAABBox()
    self.scale_factor = 1.0

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

class EmptyAgentSystem(AgentSystem):
  def __init__(self) -> None:
    self.name = ''
    self.subsystems = SimpleNamespace()

  def _before_subsystems_processed_pre_state_change(
    self, 
    characteristics: AgentCharacteristics, 
    parent_byproducts: Dict[str, List]) -> None:
    return
  
  def _before_subsystems_processed_post_state_change(
    self, 
    characteristics: AgentCharacteristics, 
    parent_byproducts: Dict[str, List]) -> None:
    return
  
  def _after_subsystems_processed_pre_state_change(
    self, 
    characteristics: AgentCharacteristics, 
    parent_byproducts: Dict[str, List]) -> None:
    return
  
  def _after_subsystems_processed_post_state_change(
    self, 
    characteristics: AgentCharacteristics, 
    parent_byproducts: Dict[str, List]) -> None:
    return

class EmptySensoryMemory(SensoryMemoryLike):
  def __init__(self) -> None:
    self.memory_store: List[Sensation] = []

class EmptyWorkingMemory(WorkingMemoryLike):
  def __init__(self) -> None:
    return
  
class EmptyLongTermMemory(LongTermMemoryLike):
  def __init__(self) -> None:
    super().__init__()
    self.memories: Set[Memory]  = set()
    self.skills: Set[Skill]     = set()
    self.knowledge: Set[Fact]   = set()
    self.relationships: Dict[Tag, Relationship] = {}

  def remember(self, memory: Memory) -> None:
    """Make a long term memory."""
    return

  def learn(self, skill: Skill) -> None:
    """Acquire a skill."""
    return

  def memorize(self, fact: Fact) -> None:
    """Remember a fact."""
    return

  def recognize(self, AgentLike) -> Tuple[bool, Relationship]:
    """Does the agent know another agent?"""
    return (True, Relationship())

class EmptyMemory(AgentMemoryLike):
  def __init__(self) -> None:
    self.sensory_memory: SensoryMemoryLike    = EmptySensoryMemory()
    self.working_memory: WorkingMemoryLike    = EmptyWorkingMemory()
    self.long_term_memory: LongTermMemoryLike = EmptyLongTermMemory()

class NoAgent(AgentLike):
  """Convenience class for declaring no agent. (Null object pattern.)"""
  def __init__(self) -> None:
    self.agent_state      = EmptyAgentState()
    self.style            = EmptyAgentStyle()
    self.identity         = EmptyAgentIdentity()
    self.physicality      = EmptyAgentPhysicality()
    self.position         = EmptyAgentPosition()
    self.movement         = EmptyAgentMovementAttributes()
    self.memory           = EmptyMemory()
    self.internal_systems = EmptyAgentSystem()