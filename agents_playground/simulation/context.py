from dataclasses import dataclass

from typing import Any, Callable, Union

from agents_playground.agents.structures import Size
from agents_playground.scene.scene import Scene
from agents_playground.simulation.statistics import SimulationStatistics
from agents_playground.simulation.tag import Tag
from agents_playground.styles.agent_style import AgentStyle

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
  # FIXME AgentStyle should probably be on the agent or scene.
  agent_style: AgentStyle
  stats: SimulationStatistics
  details: dict[Any, Any]

  def __init__(self, id_generator: Callable[..., Tag]) -> None:
    self.parent_window = Size()
    self.canvas = Size()
    self.agent_style = AgentStyle()
    self.details = dict()
    self.stats = SimulationStatistics(id_generator)