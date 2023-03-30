
"""
Important!!!: 
Reloading modules only works if they're in the same folder as the __init__.py file.
"""

import fsm_movement.entities
import fsm_movement.renderers
import fsm_movement.tasks

import importlib
def reload():
  importlib.reload(fsm_movement.entities)
  importlib.reload(fsm_movement.renderers)
  importlib.reload(fsm_movement.tasks)