"""
This is a temporary test to help work through creating a frame graph/render graph based 
rendering pipeline. It'll probably need to be removed after that is established.
"""
import pytest

from enum import IntEnum
from dataclasses import dataclass, field
from functools import wraps
from itertools import chain
from operator import itemgetter, add
from typing import Any, Callable, Generator, NamedTuple, Protocol, Type
from deprecated import deprecated

from agents_playground.counter.counter import Counter, CounterBuilder
from agents_playground.fp import Maybe, Nothing  # type: ignore

def uniform(cls):
    class Uniform:
        x = 14 

        def __init__(self) -> None:
            self._internal_state = 42
        
        def has_changed(self) -> bool:
            return self._internal_state != 42
    return Uniform

@uniform
class Overlay:
    pass 

"""
PEP 318: Introduced decorators
PEP 3102: Keyword-Only Arguments
PEP 612: Parameter Specification Variables
PEP 695: Type Parameter Syntax
PEP 646: Variadic Generics (typing.TypeVarTuple for functions with variable-length args)

Python 3.12 introduced the "type" keyword.
This is an alternative to typing.TypeAlias

These two lines are equivalent. 
Url: TypeAlias = str # Pre v3.12
type Url = str       # Post v3.12
"""

type TaskId = int
type TaskName = str
type ResourceId = str
type ResourceType = str

class TaskResourceStatus(IntEnum):
    """
    Enumerated status for the life cycle of a task resource.
    """
    RESERVED = 0    # Registered but not allocated.
    ALLOCATED = 1   # The resource has had it's memory allocated.
    

class TaskResource(NamedTuple):
    id: ResourceId
    type: ResourceType
    label: str
    status: TaskResourceStatus


def pending_task_counter() -> Counter:
    return CounterBuilder.count_up_from_zero()

def init_nothing() -> Maybe:
    return Nothing()

def do_nothing(*args, **kwargs) -> None:
    return

class TaskLike(Protocol):
    task_id: TaskId         # Unique Identifier of the task.
    task_ref: Callable      # A pointer to a function or a generator that hasn't been initialized.
    args: list[Any]         # Positional parameters for the task.
    kwargs: dict[str, Any]  # Named parameters for the task.

    # required_before_tasks: list[TaskId]
    # inputs: dict[ResourceId, TaskResource]
    # outputs: dict[ResourceId, TaskResource]

    # The number of tasks this task needs to complete before it can be run again.
    waiting_on_count: Counter

    # Indicates if task has been initialized.
    initialized: bool

    # A coroutine that is suspended. This is used to store the coroutine that was originally
    # stored on self.task_ref
    coroutine: Maybe[Generator]

    def reduce_task_dependency(self) -> None:
        ...

    def read_to_run(self) -> bool:
        ...

@dataclass(init=True)
class GenericTask:
    task_ref: Callable      # A pointer to a function or a generator that hasn't been initialized.
    args: list[Any]         # Positional parameters for the task.
    kwargs: dict[str, Any]  # Named parameters for the task.
    
    task_id: TaskId = field(default=-1) # Unique Identifier of the task.

    # The number of tasks this task needs to complete before it can be run again.
    waiting_on_count: Counter = field(default_factory=pending_task_counter)

    # Indicates if task has been initialized.
    initialized: bool = field(default=False)  

    # A coroutine that is suspended. This is used to store the coroutine that was originally
    # stored on self.task_ref
    coroutine: Maybe[Generator] = field(default_factory=init_nothing)  

    def reduce_task_dependency(self) -> None:
        self.waiting_on_count.decrement()

    def read_to_run(self) -> bool:
        return self.waiting_on_count.at_min_value()
    
@dataclass
class TaskGraphNode:
    """
    Represents a task that has been provisioned and could possibly be run.
    """
    task_id: TaskId # The ID of the provisioned task.
    task_name: TaskName # The name that was used to provision the task. Used for debugging.
    parent_ids: list[TaskId] # The list of tasks that must run before this task.
    inputs: list[ResourceId] # The list of inputs that must be allocated before the this task can run.


class TaskGraph:
    """
    Represents a collection of interdependent tasks. Loops are not permitted.
    """
    def __init__(self) -> None:
        self._ready_to_run: list[TaskId] = []
        self._blocked_to_run: list[TaskId] = []

    def ready_to_run(self, id: TaskId) -> None:
        if id not in self._ready_to_run:
            self._ready_to_run.append(id)
            
class TaskRegistryError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

@dataclass
class TaskDef:
    """
    A container class. Responsible for containing the metadata 
    required to provision a task instance.
    """
    name: TaskName
    type: Type # The type of task to provision.

    # The list of tasks that must run before this type of task.
    required_before_tasks: list[TaskName] = field(default_factory=list)

    # The list of required inputs that must be allocated for 
    # this type of task to run.
    inputs: list[ResourceId] = field(default_factory=list)

    # The list of outputs this task must produce.
    outputs: list[ResourceId] = field(default_factory=list)

class TaskRegistry:
    """
    Responsible for maintaining a registry of tasks that can be provisioned.
    When a task is provisioned it is stored in the TaskRegistry.
    """
    def __init__(self) -> None:
        # Storage and indices for task type declarations
        self._registered_tasks: list[TaskDef] = []
        self._aliases_index: dict[TaskName, int] = {}

        # Storage and indices for provisioned tasks.
        self._task_counter: Counter[int] = CounterBuilder.count_up_from_zero()
        self._provisioned_tasks: list[TaskLike] = []
        self._provisioned_task_ids: dict[TaskId, int] = {}

    def register(self, alias:str, task_def: TaskDef) -> None:
        """Alternative to tr[alias] = task_def."""
        self[alias] = task_def

    def clear(self) -> None:
        self._aliases_index.clear()
        self._registered_tasks.clear()
        self._provisioned_tasks.clear()
        self._provisioned_task_ids.clear()

    def provision(self, alias: str, *args, **kwargs) -> TaskLike:
        if alias not in self._aliases_index:
            raise TaskRegistryError(f"Attempted to provision a task that was not registered. Could not find task alias {alias}.")
        
        task_def_index = self._aliases_index[alias]
        task_def = self._registered_tasks[task_def_index]
        task: TaskLike = task_def.type(*args, **kwargs)
        task.task_id = self._task_counter.increment()
                
        self._provisioned_tasks.append(task)
        self._provisioned_task_ids[task.task_id] = len(self._provisioned_tasks) - 1
        return task

    def task_graph(self) -> TaskGraph:
        graph = TaskGraph()
        for task in self._provisioned_tasks:
            pass
            # task.required_before_tasks
            # graph.
        return graph
    
    def add_requirement(
        self, 
        before_tasks: tuple[TaskName,...], 
        later_tasks: tuple[TaskName,...]
    ) -> None:
        """
        Set a task dependency. Task A (B, C,...) must run before task X, (Y, Z).

        Args:
        - before_tasks: The list of tasks that must run before the later tasks.
        - later_tasks: The list of tasks that can run after the list of tasks in the before tuple.
        """
        # Verify that all tasks are in the registry.
        for task_name in chain(before_tasks, later_tasks):
            if task_name not in self._registered_tasks:
                raise TaskRegistryError(f"Attempted to add a requirement on a task that is not registered.\nThe task name {task_name} is not associated with a registered task.")
        
        # Add the before tasks as requirements to the later tasks.
        for later_task_name in later_tasks:
            later_task: TaskDef = self[later_task_name]
            later_task.required_before_tasks.extend(before_tasks)

    @property
    def provisioned_tasks_count(self) -> int:
        return len(self._provisioned_tasks)

    def __setitem__(self, key: str, value: TaskDef) -> None:
        if key in self._aliases_index:
            raise TaskRegistryError(
                f"The alias {key} is already assigned to a Task definition."
            )
        if value in self._registered_tasks:
            index = self._registered_tasks.index(value)
        else:
            self._registered_tasks.append(value)
            index = len(self._registered_tasks) - 1
        self._aliases_index[key] = index 
      

    def __getitem__(self, key: TaskName) -> TaskDef:
        """Finds a TaskLike definition by its alias."""
        index = self._aliases_index[key]
        return self._registered_tasks[index]
    
    def __len__(self) -> int:
        return len(self._aliases_index)
    
    def __contains__(self, key: str) -> bool:
        """Enables 'my_alias' in task_registry."""
        return key in self._aliases_index

    
class TaskResourceRegistryError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class TaskResourceRegistry:
    """
    Responsible for maintaining a registry of resources that can be provisioned.
    Dynamically populated by the decorators when a simulation is initialized.
    """
    def __init__(self) -> None:
        self._registered_resources: list[TaskResource] = []
        self._aliases: dict[str, int] = {}

    def register(self, alias:str, resource_def: TaskResource) -> None:
        """Alternative to trr[alias] = task_def."""
        self[alias] = resource_def

    def clear(self) -> None:
        self._aliases.clear()
        self._registered_resources.clear()

    def __setitem__(self, key: str, value: TaskResource) -> None:
        if key in self._aliases:
            # It is valid that a resource be registered more than once. 
            # For example, a buffer could be the output of one task and the input of another.
            return
        if value in self._registered_resources:
            index = self._registered_resources.index(value)
        else:
            self._registered_resources.append(value)
            index = len(self._registered_resources) - 1
        self._aliases[key] = index 
      
    def __getitem__(self, key: str) -> TaskResource:
        """Finds a TaskResource definition by its alias."""
        index = self._aliases[key]
        return self._registered_resources[index]
    
    def __len__(self) -> int:
        return len(self._aliases)
    
    def __contains__(self, key: str) -> bool:
        """Enables 'my_alias' in task_resource_registry."""
        return key in self._aliases
    

task_registry: TaskRegistry = TaskRegistry()
task_resource_registry: TaskResourceRegistry = TaskResourceRegistry()

class task:
    """
    Marks a class as a task type. This has the following effects:
    - Registering a task in the task registry so it can be referenced in a scene.json file.
    - The task can be dynamically provisioned when a simulation is loaded.
    - The class marked with @task is replaced at run time with an instance of TaskDef.

    TODO: Either make this have a type parameter (e.g. Computer, General, Render) 
          or have different decorators for different types.
    """
    def __init__(self, name:str) -> None:
        self._name = name

    def __call__(self, cls: Type) -> TaskDef:         
        task_def = TaskDef(name=self._name, type=GenericTask)
        task_registry.register(self._name, task_def)
        return task_def          

class task_input:
    """
    Marks a task definition as requiring a registered input. This has the following effects:
    - A TaskResource instance is instantiated with a status of RESERVED. 
    - The TaskResource instance is registered in the task resource registry. Existing tasks are not replaced.
    - The task marked with @task_input has its metadata assigned the TaskResource in its list of inputs.
    """
    def __init__(self, type: ResourceType, id: ResourceId, label: str) -> None:
        self._resource_type = type
        self._resource_id = id
        self._resource_label = label  

    def __call__(self, task_def: TaskDef) -> TaskDef:
        # Register the input resource.
        task_resource_registry.register(
            self._resource_id, 
            TaskResource(self._resource_id, 
                self._resource_type, 
                self._resource_label, 
                TaskResourceStatus.RESERVED
            )
        )

        # Associate the resource with the task definition.
        if self._resource_id not in task_def.inputs:
            task_def.inputs.append(self._resource_id)

        return task_def

class task_output:
    """
    Marks a task as requiring a registered output. This has the following effects:
    - The a TaskResource instance is instantiated with a status of RESERVED. 
    - The TaskResource instance is registered in the task resource registry. Existing tasks are not replaced.
    - The task marked with @task_output has its task definition assigned the TaskResource in its list of outputs.
    """
    def __init__(self, type: ResourceType, id: ResourceId, label: str) -> None:
        self._resource_type = type
        self._resource_id = id
        self._resource_label = label 

    def __call__(self, task_def: TaskDef) -> TaskDef:
        task_resource_registry.register(
            self._resource_id, 
            TaskResource(
                self._resource_id, 
                self._resource_type, 
                self._resource_label, 
                TaskResourceStatus.RESERVED
            )
        )
        if self._resource_id not in task_def.outputs:
            task_def.outputs.append(self._resource_id)
        return task_def

@task_input(type='Texture', id='font_atlas_1', label='Font Atlas')
@task_input(type='Buffer', id='buffer_1', label='Some kind of buffer')
@task_output(type='GPUBuffer', id='font_atlas_buffer', label='Packed Font Atlas')
@task(name="my_cool_task")
class MyTask:
    pass

@task(name="my_task_with_no_deps")
class MyLonelyTask:
    pass

@pytest.fixture
def populated_task_registry(self) -> TaskRegistry:
    """Create a registry that is populated outside of using decorators.
    The Desired Hierarchy is:
    load_scene_file
        load_landscape | load_agent_meshes | load_entity_meshes | load_textures
    init_graphics_pipeline
        prep_landscape_render | prep_agent_renderer | prep_ui_renderer
    start_simulation_loop
    """
    tr = TaskRegistry()

    # Register the tasks
    for task_name in [
        "load_scene_file",
        "load_landscape",
        "load_agent_meshes",
        "load_entity_meshes",
        "load_textures",
        "init_graphics_pipeline",
        "prep_landscape_render",
        "prep_agent_renderer",
        "prep_ui_renderer",
        "start_simulation_loop",
    ]:
        tr.register(task_name, TaskDef(name=task_name, type=GenericTask))

    # Establish inter-task dependencies.
    
    # Run load_scene_file -> before -> load_landscape | load_agent_meshes | load_entity_meshes | load_textures
    tr.add_requirement(("load_scene_file",), ("load_landscape", "load_agent_meshes", "load_entity_meshes","load_textures"))
   
    # run load_landscape & load_agent_meshes & load_entity_meshes & load_textures -> before -> init_graphics_pipeline
    tr.add_requirement(("load_landscape", "load_agent_meshes", "load_entity_meshes", "load_textures"), ("init_graphics_pipeline",))

    # run init_graphics_pipeline -> before -> prep_landscape_render | prep_agent_renderer | prep_ui_renderer
    tr.add_requirement(("init_graphics_pipeline",), ("prep_landscape_render", "prep_agent_renderer", "prep_ui_renderer"))
    
    # run prep_landscape_render & prep_agent_renderer & prep_ui_renderer -> before -> start_simulation_loop
    tr.add_requirement(("prep_landscape_render", "prep_agent_renderer", "prep_ui_renderer"),("start_simulation_loop",))

    # Get the above working before adding Input/Output complexities.
    return tr

class TestTaskGraph:
    def test_task_creation(self) -> None:
        assert task_registry.provisioned_tasks_count == 0
        task = task_registry.provision("my_cool_task", task_ref=do_nothing, args=[], kwargs={})
        assert task.task_id == 1

    def test_task_was_registered(self) -> None:
        # Test that a task is registered with it's name.
        assert "my_cool_task" in task_registry
        assert "my_task_with_no_deps" in task_registry

    def test_dynamic_task_creation(self) -> None:
        task = task_registry.provision(
            'my_task_with_no_deps', 
            task_ref=do_nothing,
            args=[],
            kwargs={}
        )
        assert task.task_id == 1

    def test_cannot_provision_unregistered_tasks(self) -> None:
        with pytest.raises(TaskRegistryError) as tre:
            task_registry.provision('unregistered_task_alias')
        assert "Attempted to provision a task that was not registered. Could not find task alias unregistered_task_alias." == str(tre.value)

    def test_register_task_resources(self) -> None:
        """
        Task declarations that are marked with @task_input or @task_output have their 
        associated resources added to the task resource registry when an instance of 
        the task is provisioned.
        """
        task = task_registry.provision("my_cool_task", task_id="123", task_ref=do_nothing, args=[], kwargs={}) 

        # Verify that the resources are registered.
        assert len(task_resource_registry) == 3
        assert "font_atlas_1" in task_resource_registry
        assert "buffer_1" in task_resource_registry
        assert "font_atlas_buffer" in task_resource_registry

        # Verify that the task instance has the resources associated.
        task_def = task_registry["my_cool_task"]
        assert "font_atlas_1" in task_def.inputs
        assert "buffer_1" in task_def.inputs
        assert "font_atlas_buffer" in task_def.outputs

    def test_prepare_task_graph(self, populated_task_registry: TaskRegistry) -> None:
        """
        With the tasks that have been provisioned, create a task graph that can be 
        handed off to be optimized or executed.

        I've used a "smart" queue in the 2D engine to schedule things to work. 
        That version of the TaskScheduler makes use of counters to decrement blocking things. 

        The idea of optimizing a graph is more complicated but may be a better option 
        long term. 

        With this capability, the goal is to produce a list of tasks that can be run
        """

        # The scene.json determines the general intent. 
        # This is an example of what might be listed in a simulation file.
        initial_tasks: list[TaskName] = [
            "load_scene_file",
            "load_landscape",
            "load_agent_meshes",
            "load_entity_meshes",
            "load_textures",
            "init_graphics_pipeline",
            "prep_landscape_render",
            "prep_agent_renderer",
            "prep_ui_renderer",
            "dynamically_generate_agents",
            "set_agents_initial_state",
            "start_simulation_loop",
        ]

        task_registry.provision("my_cool_task", task_id=123, task_ref=do_nothing, args=[], kwargs={})
        task_registry.provision("my_task_with_no_deps", task_id=456, task_ref=do_nothing, args=[], kwargs={})
        task_graph: TaskGraph = task_registry.task_graph()


    def test_prepare_execution_plan(self) -> None:
        """
        Given a list of tasks, create the optimal execution plan.
        """
        assert False
