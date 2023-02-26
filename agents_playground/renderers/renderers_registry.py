from typing import Callable, Dict, Final

import agents_playground.renderers.agent as agent_renderers
from agents_playground.renderers.grid import render_grid
from agents_playground.renderers.path import render_interpolated_paths
import agents_playground.renderers.entities as entities_renderers
import agents_playground.renderers.nav_mesh as nav_mesh

import agents_playground.renderers.console as console

do_nothing_renderer = lambda *args, **kargs: None

RENDERERS_REGISTRY: Final[Dict[str, Callable]] = {
  'do_nothing_render': do_nothing_renderer,

  # Renderers for Layers
  'render_agents_layer': agent_renderers.render_agents_in_scene,
  'render_agents_aabb_layer': agent_renderers.render_agents_aabb,
  'render_grid_layer': render_grid,
  'render_paths_layer': render_interpolated_paths,
  'render_entities_layer': entities_renderers.render_entities,
  'render_nav_mesh_layer': nav_mesh.render_mesh,

  # Renderers for Simulation Components
  'draw_junction_node': nav_mesh.draw_junction_node,
  # 'ot_building_renderer': ot.building_renderer,
  # 'ot_street_renderer': ot.street_renderer,
  # 'ot_interstate_renderer': ot.interstate_renderer,

  # Renderers for Engine Components
  'engine_console_renderer': console.render_console
}