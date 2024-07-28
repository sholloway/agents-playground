from typing import Callable, Dict, Final

import agents_playground.renderers.entities as entities_renderers



def do_nothing_renderer(*args, **kwargs):
    return


RENDERERS_REGISTRY: Final[Dict[str, Callable]] = {
    "do_nothing_render": do_nothing_renderer,
    "render_entities_layer": entities_renderers.render_entities,
}
