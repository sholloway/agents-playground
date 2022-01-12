from dataclasses import dataclass

from typing import Any, Union

from agents_playground.agents.structures import Size
from agents_playground.styles.agent_style import AgentStyle


@dataclass(init=False)
class SimulationContext:
  parent_window: Size
  canvas: Size
  agent_style: AgentStyle
  details: dict[Any, Any]

  def __init__(self) -> None:
    self.parent_window = Size()
    self.canvas = Size()
    self.agent_style = AgentStyle()
    self.details = dict()