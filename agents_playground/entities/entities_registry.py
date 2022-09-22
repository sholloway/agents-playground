from typing import Callable, Dict, Final

from agents_playground.entities.pulsing_circle import update_active_radius
import agents_playground.entities.our_town_entities 

do_nothing_update_method = lambda *args, **kargs: None

ENTITIES_REGISTRY: Final[Dict[str, Callable]] = {
  'do_nothing_update_method': do_nothing_update_method,
  'update_active_radius': update_active_radius,
  'ot_update_building': agents_playground.entities.our_town_entities.update_building,
  'ot_update_interstate': agents_playground.entities.our_town_entities.update_interstate,
  'ot_update_junction_nodes': agents_playground.entities.our_town_entities.update_junction_nodes
}