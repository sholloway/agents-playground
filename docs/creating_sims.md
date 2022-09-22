# Creating Simulations

---

Simulations are small programs that process some scenario one "tick" at at time.

## How to Create a Simulation

### Creating an Empty Scene

1. Create a TOML file. TOML files are used for organizing a simulation. Place the TOML file in _agents_playground/sims_.
2. Add a title, description, and instructions to the TOML file.

```toml
[simulation.ui]
title = 'My Example Simulation'
description = 'A simple simulation.'
instructions = 'Click the start button to begin the simulation.'
```

3. Register the simulation with the app.
   1. Open `agents_playground/app/playgound_app.py`.
   2. Add an ID for the new simulation to `self._menu_items.`
   3. Add a new menu item in the _setup_menu_bar_ method.

At this point you should be able to start the app via `make run` and launch your simulation. It will be just an empty window with the default menu items.

### Adding Entities

An entity is an item that can be rendered and have some per frame logic associated
with it. Four components need to be coordinated to create an entity:

- The entity definition.
- The entity's initial renderer function.
- The entity's update render function.
- Any tasks that affect the behavior of the entity.

1. Define the entity. This is the data associated with the entity. The data is
   anything we'll use in the renderer or update method.

```python
# Define a circle
[[scene.entities.circles]]
id = 1
description='pulsing circle'
default_radius = 20
active_radius = 20
scale = 10
location=[100, 100]
color=[0, 0, 0]
fill=[0, 0, 255]
renderer='simple_circle_renderer'
update_method='update_active_radius'
```

2. Create a renderer.
   In the folder `agents_playground/renderers/` add a new Python file. In it create the renderer. A renderer is a simple method that controls how the entity should be initially displayed. Here is an example of one of the existing renderers.

```python
import dearpygui.dearpygui as dpg

from agents_playground.scene.scene import Scene
from agents_playground.simulation.context import SimulationContext


def simple_circle_renderer(self, context: SimulationContext) -> None:
  dpg.draw_circle(
    tag=self.id,
    center = self.location,
    radius=self.active_radius,
    color=self.color,
    fill=self.fill)
```

3. Register the renderer.
   Once a renderer function exists, then you need to register it in two places.
1. `agents_playground/renderers/renders_registry.py`
1. In your TOML file add the following.

```toml
[registered_functions]
renderers = ['simple_circle_renderer']
```

4. Create an update function for the entity.
   In the folder `agents_playground/entities` add a new Python file.
   In this folder create a function that is responsible for updating any render-able changes. Here is an example.

```python
import dearpygui.dearpygui as dpg
from agents_playground.scene.scene import Scene

def update_active_radius(self, scene: Scene) -> None:
  circle = scene.entities[self.entity_grouping][self.toml_id]
  dpg.configure_item(circle.id, radius = circle.active_radius)
```

5. Register the update function in `agents_playground/entities/entities_registry.py`.

6. Create a task to manipulate the entity.
   In the folder `agents_playground/tasks/` create a new Python file. In this file
   create a coroutine that is responsible for updating the entity. Here is an example.

```python
from agents_playground.core.task_scheduler import ScheduleTraps
from agents_playground.sys.logger import get_default_logger

logger = get_default_logger()

def pulse_circle_coroutine(*args, **kwargs) -> Generator:
  """A task that makes a 2D circle radius oscillate.

  Args:
    - scene: The scene to take action on.
    - circle_id: The agent to move along the path.
  """
  logger.info('pulse_circle: Starting task.')
  scene = kwargs['scene']
  circle_id = kwargs['circle_id']
  speed: float = kwargs['speed']

  circle = scene.entities['circles'][circle_id]

  if circle:
    try:
      while True:
        inflate_amount:float = 0.5*(1+sin(2 * pi * perf_counter()))
        circle.active_radius = circle.default_radius + circle.scale * inflate_amount
        yield ScheduleTraps.NEXT_FRAME
    except GeneratorExit:
      logger.info('Task: pulse_circle - GeneratorExit')
    finally:
      logger.info('Task: pulse_circle - Task Completed')
  else:
    raise Exception(f"Could not find circle: {circle_id}")
```

5. Register the update method.
   Once the update method exists you need to register it in two places.
1. `agents_playground/tasks/tasks_registry.py`
1. In your toml file add the following to the _registered_functions_ section.

```toml
[registered_functions]
renderers = ['simple_circle_renderer']
tasks = ['pulse_circle_coroutine']
```
