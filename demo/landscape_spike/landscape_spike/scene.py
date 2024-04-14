from math import copysign, radians
from typing import cast, Generator, Tuple

from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.legacy.project.extensions import (
  register_entity, 
  register_renderer, 
  register_task
)

from agents_playground.core.task_scheduler import ScheduleTraps
from agents_playground.legacy.scene.scene import Scene
from agents_playground.simulation.tag import Tag

@register_task(label = 'agents_spinning')
def agents_spinning(*args, **kwargs) -> Generator:
  """ Rotate a group of agents individually in place. 
        
  Rotation is done by updating the agent's facing direction at a given speed
  per frame.
  """  
  scene: Scene = kwargs['scene']      
  agent_ids: Tuple[Tag, ...] = kwargs['agent_ids']
  speeds: Tuple[float, ...] = kwargs['speeds']

  # build a structure of the form: want = { 'id' : {'speed': 0.3}
  values = list(map(lambda i: {'speed': i[0]}, list(zip(speeds))))
  group_motion = dict(zip(agent_ids, values))
  rotation_amount = radians(5)

  try:
    while True:
      agent_id: Tag
      for agent_id in agent_ids:
        rot_dir = int(copysign(1, group_motion[agent_id]['speed']))
        agent: AgentLike = scene.agents[agent_id]
        new_orientation = agent.position.facing.rotate(rotation_amount * rot_dir)
        agent.face(new_orientation, scene.cell_size)
      yield ScheduleTraps.NEXT_FRAME
  except GeneratorExit:
    pass
  finally:
    pass