# from typing import Callable, Dict

# import my_sim.entities.pulsing_circle
# import my_sim.renderers.simple_circle_renderer
# import my_sim.tasks.pulse_circle_coroutine 

from math import sin, pi
from time import  perf_counter
from typing import Generator

import dearpygui.dearpygui as dpg

from agents_playground.simulation.context import SimulationContext
from agents_playground.legacy.project.extensions import register_renderer
from agents_playground.legacy.scene.scene import Scene
from agents_playground.legacy.project.extensions import register_entity

from agents_playground.core.task_scheduler import ScheduleTraps
from agents_playground.sys.logger import get_default_logger
from agents_playground.legacy.project.extensions import register_task

logger = get_default_logger()

@register_renderer(label='simple_circle_renderer')
def simple_circle_renderer(self, context: SimulationContext) -> None:
  dpg.draw_circle(
    tag=self.id, 
    center = self.location, 
    radius=self.active_radius, 
    color=self.color, 
    fill=self.fill)
  
@register_entity(label='update_active_radius')
def update_active_radius(self, scene: Scene) -> None:
  circle = scene.entities[self.entity_grouping][self.toml_id]
  if dpg.does_item_exist(circle.id):
    dpg.configure_item(circle.id, radius = circle.active_radius)

@register_task(label = 'pulse_circle_coroutine')
def pulse_circle_coroutine(*args, **kwargs) -> Generator:
  """A task that makes a 2D circle radius oscillate.

  Args:
    - scene: The scene to take action on.
    - circle_id: The agent to move along the path.
  """
  logger.info('pulse_circle: Starting task.')
  scene = kwargs['scene']
  circle_id = kwargs['circle_id']
  speed: float = kwargs['speed'] 

  # TODO: What should the access pattern be?
  # Searching an array is less than ideal
  # circle = first_true(scene.entities.circles, None, lambda c: c.id == circle_id)
  circle = scene.entities['circles'][circle_id]
  
  if circle:
    try:
      while True:
        inflate_amount:float = 0.5*(1+sin(2 * pi * perf_counter()))
        circle.active_radius = circle.default_radius + circle.scale * inflate_amount
        yield ScheduleTraps.NEXT_FRAME
    except GeneratorExit:
      logger.info('Task: pulse_circle - GeneratorExit')
    finally:
      logger.info('Task: pulse_circle - Task Completed')
  else:
    raise Exception(f"Could not find circle: {circle_id}")  
  
print('Loaded my sim')