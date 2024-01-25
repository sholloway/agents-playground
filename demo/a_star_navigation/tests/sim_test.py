import os
from types import SimpleNamespace
from typing import Tuple

from pytest_mock import MockFixture
from unittest.mock import Mock as UnitTestMock

from agents_playground.entities.entities_registry import ENTITIES_REGISTRY
from agents_playground.navigation.navigation_mesh import Junction
from agents_playground.navigation.navigator import NavigationResultStatus, NavigationRouteResult, Navigator
from agents_playground.project.extensions import simulation_extensions
from agents_playground.renderers.renderers_registry import RENDERERS_REGISTRY
from agents_playground.legacy.scene.scene import Scene
from agents_playground.legacy.scene.scene_builder import SceneBuilder
from agents_playground.legacy.scene.scene_reader import SceneReader
from agents_playground.tasks.tasks_registry import TASKS_REGISTRY

import a_star_navigation

def load_town_scene() -> Scene:
  scene_path = os.path.abspath('./a_star_navigation/scene.toml')
  scene_reader = SceneReader()
  scene_data:SimpleNamespace = scene_reader.load(scene_path)

  global current_id
  current_id = 0
  def id_generator(): 
    global current_id
    current_id += 1 
    return current_id
  
  se = simulation_extensions()

  scene_builder = SceneBuilder(
    id_generator = id_generator, 
    task_scheduler = UnitTestMock(),
    pre_sim_scheduler = UnitTestMock(),
    render_map = RENDERERS_REGISTRY | se.renderer_extensions, 
    task_map = TASKS_REGISTRY | se.task_extensions,
    entities_map = ENTITIES_REGISTRY | se.entity_extensions
  )

  scene: Scene = scene_builder.build(scene_data)
  return scene

class TestOurTownNavigation:
  def setup_class(self):
    self.scene = load_town_scene()
    self.navigator = Navigator()

  def test_route_to_factory_entrance(self, mocker: MockFixture) -> None:
    starting_junction: Junction = self.scene.nav_mesh.get_junction_by_toml_id('tower-1-apt-exit')
    target_junction: Junction = self.scene.nav_mesh.get_junction_by_toml_id('factory-entrance')
    result: Tuple[NavigationResultStatus, NavigationRouteResult] = \
      self.navigator.find_route(
        starting_junction.location, 
        target_junction.location, 
        self.scene.nav_mesh)
    assert result[0] == NavigationResultStatus.SUCCESS
  
  def test_route_to_el_school_entrance(self, mocker: MockFixture) -> None:
    starting_junction: Junction = self.scene.nav_mesh.get_junction_by_toml_id('tower-1-apt-exit')
    target_junction: Junction = self.scene.nav_mesh.get_junction_by_toml_id('el-school-entrance')
    result: Tuple[NavigationResultStatus, NavigationRouteResult] = \
      self.navigator.find_route(
        starting_junction.location, 
        target_junction.location, 
        self.scene.nav_mesh)
    assert result[0] == NavigationResultStatus.SUCCESS
  
  def test_route_to_temple_entrance(self, mocker: MockFixture) -> None:
    starting_junction: Junction = self.scene.nav_mesh.get_junction_by_toml_id('tower-1-apt-exit')
    target_junction: Junction = self.scene.nav_mesh.get_junction_by_toml_id('t-church-entrance')
    result: Tuple[NavigationResultStatus, NavigationRouteResult] = \
      self.navigator.find_route(
        starting_junction.location, 
        target_junction.location, 
        self.scene.nav_mesh)
    assert result[0] == NavigationResultStatus.SUCCESS
  
  def test_route_to_diner_entrance(self, mocker: MockFixture) -> None:
    starting_junction: Junction = self.scene.nav_mesh.get_junction_by_toml_id('tower-1-apt-exit')
    target_junction: Junction = self.scene.nav_mesh.get_junction_by_toml_id('diner-business-entrance')
    result: Tuple[NavigationResultStatus, NavigationRouteResult] = \
      self.navigator.find_route(
        starting_junction.location, 
        target_junction.location, 
        self.scene.nav_mesh)
    assert result[0] == NavigationResultStatus.SUCCESS
  
  def test_from_factory_to_apts(self, mocker: MockFixture) -> None:
    starting_junction: Junction = self.scene.nav_mesh.get_junction_by_toml_id('factory-exit')
    apts = ['tower-1-apt-entrance','tower-2-apt-entrance','tower-3-apt-entrance','tower-4-apt-entrance']
    for apt in apts:
      target_junction: Junction = self.scene.nav_mesh.get_junction_by_toml_id(apt)
      result: Tuple[NavigationResultStatus, NavigationRouteResult] = \
        self.navigator.find_route(
          starting_junction.location, 
          target_junction.location, 
          self.scene.nav_mesh)
      assert result[0] == NavigationResultStatus.SUCCESS

  def test_from_factory_to_middle_school(self, mocker: MockFixture) -> None:
    starting_junction: Junction = self.scene.nav_mesh.get_junction_by_toml_id('factory-exit')
    target_junction: Junction = self.scene.nav_mesh.get_junction_by_toml_id('m-school-entrance')
    result: Tuple[NavigationResultStatus, NavigationRouteResult] = \
      self.navigator.find_route(
        starting_junction.location, 
        target_junction.location, 
        self.scene.nav_mesh)
    assert result[0] == NavigationResultStatus.SUCCESS