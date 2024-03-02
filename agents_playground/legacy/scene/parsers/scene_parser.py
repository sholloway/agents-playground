from __future__ import annotations

from abc import abstractmethod
from types import SimpleNamespace
from typing import Protocol

from agents_playground.legacy.scene.scene import Scene

class SceneParser(Protocol):
  def parse(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    if self.is_fit(scene_data):
      self.process(scene_data, scene)
    else:
      self.default_process(scene_data, scene)
      
  @abstractmethod
  def is_fit(self, scene_data:SimpleNamespace) -> bool:
    ...

  @abstractmethod
  def process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    ...

  def default_process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    return