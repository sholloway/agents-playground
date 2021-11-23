Decisions Log

---

This file serves as a log of decisions made in the course of development.

- [Decisions](#decisions)
  - [Ignore DearPYGui Types](#ignore-dearpygui-types)
  - [Leveraging Composition for Agents](#leveraging-composition-for-agents)

## Decisions

### Ignore DearPYGui Types

DearPyGUI doesn't [currently](https://github.com/hoffstadt/DearPyGui/issues/922)
export types. As such, I've configured the project to ignore them.

### Leveraging Composition for Agents

I want Agents to not know anything about physics, path finding, rendering, etc...
To enable this, I use the combination of Protocol classes with **call** methods
defined. This enables creating call-ables with defined type signatures.

```python
from typing import Protocol

class PathFinder(Protocol):
  def __call__(self, parm:str) -> None:
    # do some stuff

pf = PathFinder()

# Can be passed like so...
agent.movement_strategy(pf)

# The instance can be invoked liked so...
pf('an argument')
```

This is preferable to just passing a Callable due to
[limitations](https://github.com/python/mypy/issues/708) with mypy.
