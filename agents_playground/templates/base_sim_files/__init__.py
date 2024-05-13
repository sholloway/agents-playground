
"""
Important!!!: 
Reloading modules only works if they're in the same folder as the __init__.py file.
"""
import importlib
import sys 

import ${project_pkg}.scene

def reload():
  """Don't change unless you know what you're doing.
  This is responsible for reloading the project. It will automatically reload
  any module in the $project_pkg package that is imported above.
  """
  [ 
    importlib.reload(sys.modules[module_name]) 
    for module_name in list( 
      filter(
        lambda i: i.startswith('${project_pkg}.'), 
        sys.modules.keys()
      )
    ) 
  ]