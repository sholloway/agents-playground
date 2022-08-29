from typing import Callable, Dict, Final

from agents_playground.renderers.path import (
  circle_renderer, 
  line_segment_renderer
)

import agents_playground.renderers.agent as agent_renderers
from agents_playground.renderers.grid import render_grid
from agents_playground.renderers.path import render_interpolated_paths
import agents_playground.renderers.stats as rendering_stats
import agents_playground.renderers.entities as entities_renderers

from agents_playground.renderers.circle import simple_circle_renderer
import agents_playground.renderers.our_town_renderers as ot

do_nothing_renderer = lambda *args, **kargs: None

RENDERERS_REGISTRY: Final[Dict[str, Callable]] = {
  'do_nothing_render': do_nothing_renderer,

  # Renderers for Layers
  'render_agents_layer': agent_renderers.render_agents_scene,
  'render_grid_layer': render_grid,
  'render_paths_layer': render_interpolated_paths,
  'render_stats_layer': rendering_stats.render_stats,
  'render_entities_layer': entities_renderers.render_entities,

  # Renderers for Simulation Components
  'line_segment_renderer': line_segment_renderer,
  'circular_path_renderer': circle_renderer,
  'simple_circle_renderer': simple_circle_renderer,
  'ot_building_renderer': ot.building_renderer,
  'ot_street_renderer': ot.street_renderer,
  'ot_interstate_renderer': ot.interstate_renderer,
  'ot_draw_junction_node': ot.draw_junction_node,
  'ot_draw_nav_mesh_segment': ot.draw_nav_mesh_segment
}