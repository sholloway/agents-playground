from typing import Callable, Dict, Final


def do_nothing_update_method(*args, **kwargs):
    return


ENTITIES_REGISTRY: Final[Dict[str, Callable]] = {
    "do_nothing_update_method": do_nothing_update_method
}
