import tomli 

"""
p = os.path.abspath('./agents_playground/sims/simple_movement.toml')

import json
print(json.dumps(data, indent=4, sort_keys=True))
"""

class SimLoader:
  """"""
  def __init__(self):
    pass

  def load(self, path):
    # p = os.path.abspath('../sims/simple_movement.toml')
    with open(path, "rb") as f:
      data = tomli.load(f)
    return data 