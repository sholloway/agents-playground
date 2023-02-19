from typing import Callable, Dict, Final

import agents_playground.tasks.agent_movement as am 
import agents_playground.tasks.generate_agents as ga

TASKS_REGISTRY: Final[Dict[str,Callable]] = {
  'agent_traverse_linear_path' : am.agent_traverse_linear_path,
  'agent_traverse_circular_path' : am.agent_traverse_circular_path,
  'agent_pacing': am.agent_pacing,
  'agents_spinning' : am.agents_spinning,
  'agent_random_navigation' : am.agent_random_navigation,
  
  'generate_agents': ga.generate_agents
}