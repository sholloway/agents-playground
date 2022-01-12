from dataclasses import dataclass

from typing import Any, Callable, Union

from agents_playground.agents.structures import Size
from agents_playground.simulation.statistics import SimulationStatistics
from agents_playground.simulation.tag import Tag
from agents_playground.styles.agent_style import AgentStyle


@dataclass(init=False)
class SimulationContext:
  parent_window: Size
  canvas: Size
  # FIXME AgentStyle should probably be in details.
  agent_style: AgentStyle
  stats: SimulationStatistics
  details: dict[Any, Any]

  def __init__(self, id_generator: Callable[..., Tag]) -> None:
    self.parent_window = Size()
    self.canvas = Size()
    self.agent_style = AgentStyle()
    self.details = dict()
    self.stats = SimulationStatistics(id_generator)