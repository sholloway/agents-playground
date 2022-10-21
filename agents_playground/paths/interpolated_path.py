from typing import Callable
from agents_playground.core.types import Size
from agents_playground.simulation.tag import Tag

class InterpolatedPath:
  def __init__(self, id: Tag, renderer: Callable, toml_id: Tag = None) -> None:
    self._id = id
    self._renderer = renderer
    self._toml_id = toml_id

  @property
  def id(self) -> Tag:
    return self._id
  
  @property
  def toml_id(self) -> Tag:
    return self._toml_id

  def render(self, cell_size: Size, offset: Size) -> None:
    self._renderer(self, cell_size, offset)
