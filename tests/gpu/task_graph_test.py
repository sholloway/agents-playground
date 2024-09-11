"""
This is a temporary test to help work through creating a frame graph/render graph based 
rendering pipeline. It'll probably need to be removed after that is established.
"""
import pytest

from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable, Generator, Protocol
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

type TaskId = str
type ResourceId = str
type ResourceType = str

@dataclass
class TaskResource:
    id: ResourceId
    type: ResourceType
    label: str


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

    parent_ids: list[TaskId]
    inputs: dict[ResourceId, TaskResource]
    outputs: dict[ResourceId, TaskResource]

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
    task_id: TaskId         # Unique Identifier of the task.
    task_ref: Callable      # A pointer to a function or a generator that hasn't been initialized.
    args: list[Any]         # Positional parameters for the task.
    kwargs: dict[str, Any]  # Named parameters for the task.

    parent_ids: list[TaskId] = field(default_factory=list)
    inputs: dict[ResourceId, TaskResource] = field(default_factory=dict)
    outputs: dict[ResourceId, TaskResource] = field(default_factory=dict)

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
            
class TaskRegistryError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class TaskRegistry:
    """
    Responsible for maintaining a registry of tasks that can be provisioned.
    Dynamically populated when a simulation is initialized by the decorators.
    """
    def __init__(self) -> None:
        self._registered_tasks: list[Callable] = []
        self._aliases: dict[str, int] = {}

    def register(self, alias:str, task_def: Callable) -> None:
        """Alternative to tr[alias] = task_def."""
        self[alias] = task_def

    def clear(self) -> None:
        self._aliases.clear()
        self._registered_tasks.clear()

    def provision(self, alias: str, *args, **kwargs) -> TaskLike:
        if alias not in self._aliases:
            raise TaskRegistryError(f"Attempted to provision a task that was not registered. Could not find task alias {alias}.")
        task_def_index = self._aliases[alias]
        task_def = self._registered_tasks[task_def_index]
        return task_def(*args, **kwargs)

    def __setitem__(self, key: str, value: Callable) -> None:
        if key in self._aliases:
            raise TaskRegistryError(
                f"The alias {key} is already assigned to a Task definition."
            )
        if value in self._registered_tasks:
            index = self._registered_tasks.index(value)
        else:
            self._registered_tasks.append(value)
            index = len(self._registered_tasks) - 1
        self._aliases[key] = index 
      
    def __getitem__(self, key: str) -> Callable:
        """Finds a TaskLike definition by its alias."""
        index = self._aliases[key]
        return self._registered_tasks[index]
    
    def __len__(self) -> int:
        return len(self._aliases)
    
    def __contains__(self, key: str) -> bool:
        """Enables 'my_alias' in task_registry."""
        return key in self._aliases
    

task_registry: TaskRegistry = TaskRegistry()

class task:
    def __init__(self, name:str) -> None:
        self._name = name

    def __call__(self, cls) -> Any:            
        task_registry.register(self._name, GenericTask)
        return GenericTask          
        
def task_input(type: ResourceType, id: ResourceId, label: str) -> Callable:
    """
    Marks a task as requiring a registered input.
    """
    def decorator(cls: Callable) -> Callable:
        @wraps(cls)
        def wrapper(*args, **kwargs):
            instance = cls(*args, **kwargs)
            instance.inputs[id] = TaskResource(id, type, label)
            return instance
        return wrapper
    return decorator

def task_output(type: ResourceType, id: ResourceId, label: str) -> Callable:
    """
    Marks a task as requiring a registered input.
    """
    def decorator(cls: Callable) -> Callable:
        @wraps(cls)
        def wrapper(*args, **kwargs):
            instance = cls(*args, **kwargs)
            instance.outputs[id] = TaskResource(id, type, label)
            return instance
        return wrapper
    return decorator

@task_input(type='Texture', id='abc123', label='Font Atlas')
@task_input(type='Buffer', id='qrs456', label='Some kind of buffer')
@task_output(type='GPUBuffer', id='qrs72', label='Packed Font Atlas')
@task(name="my_cool_task")
class MyTask:
    pass

@task(name="my_task_with_no_deps")
class MyLonelyTask:
    pass

class TestTaskGraph:
    def test_task_creation(self) -> None:
        task = MyTask(task_id='123', task_ref=do_nothing, args=[], kwargs={})
        assert len(task.parent_ids) == 0
        assert len(task.inputs) == 2
        assert len(task.outputs) == 1

    def test_task_was_registered(self) -> None:
        # Test that a task is registered with it's name.
        assert "my_cool_task" in task_registry
        assert "my_task_with_no_deps" in task_registry

    def test_task_can_have_multiple_aliases(self) -> None:
        """
        GenericTask should only be in the registry once. 
        However, there could be many aliases that can provision 
        a GenericTask.
        """
        assert len(task_registry._registered_tasks) == 1

    def test_multiple_instances_of_a_task(self) -> None:
        """
        How do I want to handle creating multiple instances of 
        a task type?
        
        For example, you might have multiple Compute tasks.
        It may make sense that for every task in a Task Graph 
        there is a corresponding class definition (e.g. MyTask).
        """
        assert False

    def test_dynamic_task_creation(self) -> None:
        """
        The entire point of having @task(name) is to enable 
        specifying the task names in a scene file. Then the engine
        should dynamically provision the task based on the name.

        How should this work?
        """
        task = task_registry.provision(
            'my_task_with_no_deps', 
            task_id='123', 
            task_ref=do_nothing,
            args=[],
            kwargs={}
        )
        assert task.task_id == '123'

    def test_cannot_provision_unregistered_tasks(self) -> None:
        with pytest.raises(TaskRegistryError) as tre:
            task_registry.provision('unregistered_task_alias')
        assert "Attempted to provision a task that was not registered. Could not find task alias unregistered_task_alias." == str(tre.value)

    def test_prepare_execution_plan(self) -> None:
        """
        Given a list of tasks, create the optimal execution plan.
        """
        assert False