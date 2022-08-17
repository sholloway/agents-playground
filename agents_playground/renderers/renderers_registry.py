from typing import Callable, Dict, Final

from agents_playground.renderers.path import (
  circle_renderer, 
  line_segment_renderer
)

from agents_playground.renderers.circle import simple_circle_renderer
from agents_playground.renderers.our_town_renderers import ot_building_renderer

RENDERERS_REGISTRY: Final[Dict[str, Callable]] = {
  'line_segment_renderer': line_segment_renderer,
  'circular_path_renderer': circle_renderer,
  'simple_circle_renderer': simple_circle_renderer,
  'ot_building_renderer': ot_building_renderer
}