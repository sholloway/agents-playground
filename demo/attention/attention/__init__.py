
"""
Important!!!: 
Reloading modules only works if they're in the same folder as the __init__.py file.
"""
import attention.scene

import importlib
def reload():
  importlib.reload(attention.scene)