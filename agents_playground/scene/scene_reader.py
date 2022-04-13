import tomli 
import json
from types import SimpleNamespace
"""

Example
from agents_playground.core.sim_loader import SimLoader
import os
p = os.path.abspath('./agents_playground/sims/simple_movement.toml')
sl = SimLoader()
data = sl.load(p)

import json
print(json.dumps(data, indent=4, sort_keys=True))
"""

class SceneReader:
  """Loads a simulation from a TOML file."""
  def __init__(self):
    pass

  def load(self, path):
    with open(path, "rb") as f:
      data = tomli.load(f)
    
    """
    Based on: https://dev.to/taqkarim/extending-simplenamespace-for-nested-dictionaries-58e8
    Leverage the JSON parser to build up a hierarchy of nested SimpleNamespace instances
    to enable cleaner property access.
    """
    return json.loads(json.dumps(data), object_hook=lambda item: SimpleNamespace(**item))
    
