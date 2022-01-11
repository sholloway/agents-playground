from dataclasses import dataclass
from typing import Callable

from agents_playground.simulation.context import Tag

@dataclass
class RenderLayer:
  id: Tag
  label: str
  menu_item: Tag
  layer: Callable