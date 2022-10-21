from dataclasses import dataclass

from typing import Any, Callable, Dict, Union, cast
from agents_playground.core.types import Size

from agents_playground.scene.scene import Scene
from agents_playground.simulation.statistics import SimulationStatistics
from agents_playground.simulation.tag import Tag
from agents_playground.styles.agent_style import AgentStyle

from agents_playground.sys.logger import get_default_logger
logger = get_default_logger()

"""
This is a mess. What am I really trying to do here?
- I need a generic way to pass in the simulation data into a set renderers.
- The renderers are dynamically ran using CallableUtilities.invoke.
- agent_style is to wide.
- Is there anything better about having this class than just using a 
  dict to capture everything? 
    I like having properties to access the common attributes.

"""

@dataclass(init=False)
class SimulationContext:
  parent_window: Size
  canvas: Size
  scene: Scene
  stats: SimulationStatistics
  details: Dict[Any, Any]

  def __init__(self, id_generator: Callable[..., Tag]) -> None:
    self.parent_window = Size()
    self.canvas = Size()
    self.details = dict()
    self.stats = SimulationStatistics()

  def __del__(self) -> None:
    logger.info('SimulationContext is deleted.')

  def purge(self) -> None:
    self.scene.purge()
    self.details.clear()
    self.scene = cast(Scene, None)
    self.parent_window = cast(Size, None)
    self.canvas = cast(Size, None)
    self.agent_style = cast(AgentStyle, None)
    self.stats = cast(SimulationStatistics, None)
    self.details = cast(Dict[Any, Any], None)