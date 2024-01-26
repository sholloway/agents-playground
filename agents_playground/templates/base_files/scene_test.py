import os
from types import SimpleNamespace
from typing import Tuple

from pytest_mock import MockFixture
from unittest.mock import Mock as UnitTestMock


from agents_playground.entities.entities_registry import ENTITIES_REGISTRY
from agents_playground.navigation.navigation_mesh import Junction
from agents_playground.project.extensions import simulation_extensions
from agents_playground.renderers.renderers_registry import RENDERERS_REGISTRY
from agents_playground.legacy.scene.scene import Scene
from agents_playground.legacy.scene.scene_builder import SceneBuilder
from agents_playground.legacy.scene.scene_reader import SceneReader
from agents_playground.simulation.tag import Tag
from agents_playground.spatial.vector.vector2d import Vector2d
from agents_playground.tasks.tasks_registry import TASKS_REGISTRY
from agents_playground.legacy.scene.id_map import IdMap

from ${project_pkg}.scene import agents_spinning

current_id: int = 0

def id_generator(): 
  global current_id
  current_id += 1 
  return current_id

def load_scene() -> Tuple[Scene, IdMap]:
  scene_path                  = os.path.abspath('./${project_pkg}/scene.toml')
  scene_reader                = SceneReader()
  scene_data: SimpleNamespace = scene_reader.load(scene_path)
  
  se = simulation_extensions()
  id_map: IdMap = IdMap()
  scene_builder = SceneBuilder(
    id_generator      = id_generator, 
    id_map            = id_map,
    task_scheduler    = UnitTestMock(),
    pre_sim_scheduler = UnitTestMock(),
    render_map        = RENDERERS_REGISTRY | se.renderer_extensions, 
    task_map          = TASKS_REGISTRY | se.task_extensions,
    entities_map      = ENTITIES_REGISTRY | se.entity_extensions
  )

  scene: Scene = scene_builder.build(scene_data)
  return scene, id_map

class TestScene:
  scene: Scene
  id_map: IdMap

  def setup_class(self):
    self.scene, self.id_map = load_scene()

  def test_agents_spinning(self, mocker: MockFixture) -> None:
    agent_id_toml_id: int = 1
    agent_id: Tag = self.id_map.lookup_agent_by_toml(agent_id_toml_id)
    kwargs = {
      'scene': self.scene,
      'agent_ids': (agent_id,),
      'speeds': (0.01,) 
    }
    agent = self.scene.agents[agent_id]
    assert agent is not None
    agent.face(Vector2d(1,0), self.scene.cell_size)

    # initialize the 
    coroutine = agents_spinning(*[], **kwargs)
    assert agent.position.facing.i == 1
    assert agent.position.facing.j == 0

    next(coroutine)
    assert agent.position.facing.i == 0.9961946980917455
    assert agent.position.facing.j == 0.08715574274765817