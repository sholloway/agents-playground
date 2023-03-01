
"""
Important!!!
Reloading modules only works if they're in the same folder as the __init__.py file.
"""
import project_pkg.renderers
import project_pkg.entities
import project_pkg.generate_agents
import project_pkg.agent_movement

import importlib
def reload():
  importlib.reload(project_pkg.renderers)
  importlib.reload(project_pkg.entities)
  importlib.reload(project_pkg.generate_agents)
  importlib.reload(project_pkg.agent_movement)