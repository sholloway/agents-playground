from types import SimpleNamespace
from typing import Any, Callable, Union

from agents_playground.simulation.render_layer import RenderLayer


class LayerBuilder:
  @staticmethod
  def build(
    id_generator: Callable, 
    renderer_map: dict, 
    layer_def: SimpleNamespace) -> RenderLayer:
    renderer: Union[Any, None] = renderer_map.get(layer_def.renderer)
    show_layer_initially: bool = layer_def.show if hasattr(layer_def, 'show') else True
      
    if renderer:
      rl: RenderLayer = RenderLayer(
        id = id_generator(), 
        label= layer_def.label,
        menu_item=id_generator(),
        layer=renderer,
        show = show_layer_initially
      )
      return rl
    else:
      raise Exception(f'Error Loading the scene. No registered layer renderer named {layer_def.renderer}.')