# Use Prototypes for passing around Callables 

- Status: Rejected
- Date: 2022-01-24

## Context and Problem Statement

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

## Decision Drivers <!-- optional -->

- {driver 1, e.g., a force, facing concern, …}
- {driver 2, e.g., a force, facing concern, …}
- … <!-- numbers of drivers can vary -->

## Considered Options

- {option 1}
- {option 2}
- {option 3}
- … <!-- numbers of options can vary -->

## Decision Outcome

Rejected in favor of using coroutines as tasks based approach.

### Positive Consequences <!-- optional -->

- {e.g., improvement of quality attribute satisfaction, follow-up decisions required, …}
- …

### Negative Consequences <!-- optional -->

- {e.g., compromising quality attribute, follow-up decisions required, …}
- …

## Pros and Cons of the Options <!-- optional -->

### {option 1}

{example | description | pointer to more information | …} <!-- optional -->

- Good, because {argument a}
- Good, because {argument b}
- Bad, because {argument c}
- … <!-- numbers of pros and cons can vary -->

### {option 2}

{example | description | pointer to more information | …} <!-- optional -->

- Good, because {argument a}
- Good, because {argument b}
- Bad, because {argument c}
- … <!-- numbers of pros and cons can vary -->

### {option 3}

{example | description | pointer to more information | …} <!-- optional -->

- Good, because {argument a}
- Good, because {argument b}
- Bad, because {argument c}
- … <!-- numbers of pros and cons can vary -->

## Links <!-- optional -->

- {Link type} {Link to ADR} <!-- example: Refined by [ADR-0005](0005-example.md) -->
- … <!-- numbers of links can vary -->

<!-- markdownlint-disable-file MD013 -->
