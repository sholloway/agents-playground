## Working with the Codebase

## Exploration

What I'm interested in trying in this code base.
Expand my maze's A\* agent to possible have:

- Traits
- Characteristics
- A personal history that influence decision making (probability weights).
- NPCs and machines that do work.
  - Complex tasks
    - Example:
      1.  Assign workers to harvest raw materials: iron ore, coal, trees, water
      2.  Assign workers to transport raw materials to a processing machine. Workers carry their amount to a place and leave it.
      3.  A machine converts raw material into something else. Iron Ore -> Iron Bars
    - A machine as available inputs, outputs. Throughput rate.
- Configuration based AI or other things could possibly be created/represented
  using a Node based UI (boxes and lines).
- Support loading "scenes" to enable rapidly trying out AI in specific scenarios.

Possible Approaches

- HTN
- Hierarchical state machines

## Goals

This code repo is going to accomplish:

- A desktop app that generates a multi-screen sized environment that agents can
  navigate in (i.e. path finding).
- Algorithms like path finding, decision making, etc will be frame budget based.
  Each systems shall have a budget for how much time they can take. Profiling
  needs to be a consideration from the start. Need to identify the profiling
  tooling early. Add python debugging to this.
- This project should be a workshop app that enables trying out planning
  algorithms, new state machine designs and what not.
- Concurrency needs to be an early consideration.
- Transportation of things is interesting. Trains, Mine Cars, teleporter, etc...

## Use Cases/Scenes

- A\* Path finding of a single agent.
- A\* Path finding of 1000 agents.
- Passing events from agents by proximity?
- JPS+ evaluation

Open Questions

- How to handle concurrency in Python?
- Does an event hub concept work for large volume of subscribers?

### To Run The App

```bash
make run
```

### Perform Static Type Checking

```bash
make check
```

## Additional Documentation

- [Dependencies](./docs/dependencies.md)
- [Debugging](./docs/debugging.md)
- [Decision Log](./docs/decisions_log.md)
- [Profiling](./docs/profiling.md)
- [Testing](./docs/testing.md)
