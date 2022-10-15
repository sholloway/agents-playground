from dataclasses import dataclass
from agents_playground.core.types import Size
from agents_playground.renderers.color import Color

@dataclass(init=False)
class AgentStyle:
  stroke_thickness: float
  stroke_color: Color
  fill_color: Color 
  size: Size 

  def __init__(self) -> None:
    self.size = Size(-1, -1)