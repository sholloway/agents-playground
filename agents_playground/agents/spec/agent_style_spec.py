from typing import Protocol

from agents_playground.renderers.color import Color

class AgentStyleLike(Protocol):
  stroke_thickness: float
  stroke_color: Color
  fill_color: Color
  aabb_stroke_color: Color
  aabb_stroke_thickness: float