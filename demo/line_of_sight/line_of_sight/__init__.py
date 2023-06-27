
"""
Important!!!: 
Reloading modules only works if they're in the same folder as the __init__.py file.
"""
import line_of_sight.scene

import importlib
def reload():
  importlib.reload(line_of_sight.scene)