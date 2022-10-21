
from agents_playground.core.types import Size
from agents_playground.renderers.color import BasicColors, Color


class SceneDefaults:
  CELL_SIZE: Size = Size(20,20)
  AGENT_STYLE_STROKE_THICKNESS: float =2.0
  AGENT_STYLE_STROKE_COLOR: Color = BasicColors.black.value
  AGENT_STYLE_FILL_COLOR: Color = BasicColors.blue.value
  AGENT_STYLE_SIZE_WIDTH: int = 20
  AGENT_STYLE_SIZE_HEIGHT: int = 20