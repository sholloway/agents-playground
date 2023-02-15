# Leverage the Entity Component System Pattern for the Engine

- Status: Rejected
- Date: 2022-01-24

## Context and Problem Statement

The engine needs a way to handle updating and rendering large numbers of entities
(e.g. agents). The agents can have individual attributes that drive the stylistic
aspects of how an entity is rendered.

## Decision Drivers

- Memory Management: Thousands of entities need to not reproduce the same instance.
- Ease of Abstraction

## Considered Options

- [Component Pattern](#component-pattern-resources)
- [Entity-Component Patter](#entity-component-resources)
- [Entity Component System Pattern](#ecs-resources)

## Decision Outcome
Rejected in favor of using coroutines as tasks based approach. Currently tasks 
seem to be able to better handle dealing with both individual and hierarchies of entities. 

### Component Pattern 

Composability is a high priority for me.

```python
from dataclasses import dataclass as component

@component
class Velocity:
    x: float = 0.0
    y: float = 0.0

@component
class Position:
    x: int = 0
    y: int = 0

class Entity:
  components: []

  def composed_with(component):
    components.append(component)

class Agent(Entity):
  def __init(self)__:
    super().composed_with(Velocity())
    super().composed_with(Position())


```

### Entity Component System Pattern (Evaluating)

ECS attempts to simplify the process of performing an update on a collection of
items that have shared components. For my schedule based simulation model that
may not be very important.

Sander Mertens has a good [write up](https://ajmmertens.medium.com/why-vanilla-ecs-is-not-enough-d7ed4e3bebe5) 
of the limitations of the classic ECS pattern. In summary, without special 
considerations ECS can make it difficult to deal with:
- Creating Hierarchies
- Sharing components across entities
- Having multiple instances of a component type on an entity.
- Runtime tags
- State Machines
- System Execution Order

Mertens proposes expanding the ECS pattern formally to deal with these limitations.

## Links

### Component Pattern Resources

- Game Programming Patterns Book: [Component Pattern Chapter](http://gameprogrammingpatterns.com/component.html)
- Wiki: [Composability](https://en.wikipedia.org/wiki/Composability)

### Entity Component Resources

- I think this is what Godot does.
- In an EC framework components are classes that contain both data and behavior.
  Behavior is executed directly on the component.

```python
class Component(ABC):
  @abstract
  def update(self):
    pass

class Entity(ABC):
  components: List[Component]

  @abstract
  def add(self, c: Component):
    pass

  def update(self):
    for c in self.component:
      c.update()

```

### ECS Resources

- Wiki: [Entity Component System Pattern](https://en.wikipedia.org/wiki/Entity_component_system)
- Blog: [ECS FAQ](https://github.com/SanderMertens/ecs-faq)
- Python ECS Implementation: [Esper](https://github.com/benmoran56/esper)
