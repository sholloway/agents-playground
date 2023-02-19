from typing import Callable, Dict, Final

import agents_playground.entities.our_town_entities 

do_nothing_update_method = lambda *args, **kargs: None

ENTITIES_REGISTRY: Final[Dict[str, Callable]] = {
  'do_nothing_update_method': do_nothing_update_method,
  'ot_update_building': agents_playground.entities.our_town_entities.update_building,
  'ot_update_interstate': agents_playground.entities.our_town_entities.update_interstate,
  'ot_update_junction_nodes': agents_playground.entities.our_town_entities.update_junction_nodes
}