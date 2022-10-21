from dataclasses import dataclass
from agents_playground.core.types import Size
from agents_playground.renderers.color import Color

@dataclass(init=False)
class AgentStyle:
  stroke_thickness: float
  stroke_color: Color
  fill_color: Color 
  size: Size 
  aabb_stroke_color: Color
  aabb_stroke_thickness: float

  def __init__(self) -> None:
    self.size = Size(-1, -1)