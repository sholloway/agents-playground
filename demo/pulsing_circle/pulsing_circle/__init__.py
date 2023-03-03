
"""
Important!!!: 
Reloading modules only works if they're in the same folder as the __init__.py file.
"""
import pulsing_circle.scene

import importlib
def reload():
  importlib.reload(pulsing_circle.scene)