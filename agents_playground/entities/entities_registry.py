from typing import Callable, Dict, Final

from agents_playground.entities.pulsing_circle import update_active_radius
from agents_playground.entities.our_town_entities import ot_update_building

ENTITIES_REGISTRY: Final[Dict[str, Callable]] = {
  'update_active_radius': update_active_radius,
  'ot_update_building': ot_update_building
}