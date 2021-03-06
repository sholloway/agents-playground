from typing import Callable, Dict, Final

from agents_playground.tasks.agent_movement import (
  agent_pacing, 
  agents_spinning, 
  agent_traverse_linear_path,
  agent_traverse_circular_path 
)

from agents_playground.tasks.circle_movement import pulse_circle_coroutine


TASKS_REGISTRY: Final[Dict[str,Callable]] = {
  'agent_traverse_linear_path' : agent_traverse_linear_path,
  'agent_traverse_circular_path' : agent_traverse_circular_path,
  'agent_pacing': agent_pacing,
  'agents_spinning' : agents_spinning,
  'pulse_circle_coroutine': pulse_circle_coroutine
}