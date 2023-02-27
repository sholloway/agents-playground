
"""
Important!!!: 
Reloading modules only works if they're in the same folder as the __init__.py file.
"""
import project_pkg.scene

import importlib
def reload():
  importlib.reload(project_pkg.scene)