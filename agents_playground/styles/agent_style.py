from dataclasses import dataclass, field
from agents_playground.core.types import Size
from agents_playground.renderers.color import BasicColors, Color

@dataclass
class AgentStyle:
  stroke_thickness: float = field(default = 1.0)
  stroke_color: Color = field(default = BasicColors.black.value)
  fill_color: Color = field(default = BasicColors.blue.value) 
  aabb_stroke_color: Color = field(default = BasicColors.red.value)
  aabb_stroke_thickness: float = field(default = 1.0)
  size: Size = field(default = Size(-1,-1))