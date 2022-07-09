from typing import Callable, Dict, Final

from agents_playground.entities.pulsing_circle import update_active_radius

ENTITIES_REGISTRY: Final[Dict[str, Callable]] = {
  'update_active_radius': update_active_radius
}