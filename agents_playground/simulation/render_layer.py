from dataclasses import dataclass
from typing import Callable

from agents_playground.simulation.tag import Tag


@dataclass
class RenderLayer:
    id: Tag
    label: str
    menu_item: Tag
    layer: Callable
    show: bool
