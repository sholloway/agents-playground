from typing import Callable, Dict, Final

do_nothing_update_method = lambda *args, **kargs: None

ENTITIES_REGISTRY: Final[Dict[str, Callable]] = {
  'do_nothing_update_method': do_nothing_update_method
}