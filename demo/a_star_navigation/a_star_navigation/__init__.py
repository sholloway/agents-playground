
"""
Important!!!
Reloading modules only works if they're in the same folder as the __init__.py file.
"""
import a_star_navigation.renderers
import a_star_navigation.entities
import a_star_navigation.generate_agents
import a_star_navigation.agent_movement

import importlib
def reload():
  importlib.reload(a_star_navigation.renderers)
  importlib.reload(a_star_navigation.entities)
  importlib.reload(a_star_navigation.generate_agents)
  importlib.reload(a_star_navigation.agent_movement)