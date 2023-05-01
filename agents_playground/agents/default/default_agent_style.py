from agents_playground.agents.spec.agent_style_spec import AgentStyleLike
from agents_playground.renderers.color import BasicColors, Color

class DefaultAgentStyle(AgentStyleLike):
  def __init__(
    self, 
    stroke_thickness: float      = 1.0, 
    stroke_color: Color          = BasicColors.black.value,
    fill_color: Color            = BasicColors.blue.value,
    aabb_stroke_color: Color     = BasicColors.red.value,
    aabb_stroke_thickness: float = 1.0
  ) -> None:
    self.stroke_thickness       = stroke_thickness
    self.stroke_color           = stroke_color
    self.fill_color             = fill_color
    self.aabb_stroke_color      = aabb_stroke_color
    self.aabb_stroke_thickness  = aabb_stroke_thickness