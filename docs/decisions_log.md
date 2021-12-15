Decisions Log

---

This file serves as a log of decisions made in the course of development.

- [Decisions](#decisions)
  - [Foundational Tooling](#foundational-tooling)
    - [Use Python](#use-python)
    - [Use Poetry for Dependency Management](#use-poetry-for-dependency-management)
    - [Makefile for Automation](#makefile-for-automation)
  - [Project Tooling](#project-tooling)
    - [bpython vs ptpython](#bpython-vs-ptpython)
    - [mypy](#mypy)
    - [pudb](#pudb)
    - [py-spy](#py-spy)
    - [pytest](#pytest)
    - [pytest-mock](#pytest-mock)
  - [Ignore DearPYGui Types](#ignore-dearpygui-types)
  - [Leveraging Composition for Agents](#leveraging-composition-for-agents)

## Decisions

### Foundational Tooling

#### Use Python

#### Use Poetry for Dependency Management

#### Makefile for Automation

### Project Tooling

#### bpython vs ptpython

#### mypy

#### pudb

#### py-spy

#### pytest

#### pytest-mock

### Ignore DearPYGui Types

Date: 11/23/2021
DearPyGUI doesn't [currently](https://github.com/hoffstadt/DearPyGui/issues/922)
export types. As such, I've configured the project to ignore them.

### Leveraging Composition for Agents

Date: 11/23/2021
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
