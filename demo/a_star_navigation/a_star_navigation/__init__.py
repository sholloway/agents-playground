
"""
Important!!!
Reloading modules only works if they're in the same folder as the __init__.py file.
"""

import importlib
import sys

import a_star_navigation.renderers
import a_star_navigation.entities
import a_star_navigation.generate_agents
import a_star_navigation.agent_movement

def reload():
  [ 
    importlib.reload(sys.modules[module_name]) 
    for module_name in list( 
      filter(
        lambda i: i.startswith('a_star_navigation.'), 
        sys.modules.keys()
      )
    ) 
  ]