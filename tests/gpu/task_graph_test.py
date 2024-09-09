"""
This is a temporary test to help work through creating a frame graph/render graph based 
rendering pipeline. It'll probably need to be removed after that is established.
"""
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable, Generator
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

@dataclass(init=True)
class GenericTask:
    task_id: TaskId
    task_ref: Callable      # Can be a pointer to a function or a generator that hasn't been initialized.
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
            
class task:
    def __init__(self, name:str) -> None:
        self._name = name

    def __call__(self, cls) -> Any:            
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
@task(name='my_cool_task')
class MyTask:
    pass
    # def __init__(self, *args, **kwargs) -> None:
    #     pass

class TestTaskGraph:
    @deprecated(reason="This test class is just to help work through the complexities of working with compute shaders. It will be removed after building the render/compute graph system.")
    def test_something(self) -> None:
        overlay = Overlay()
        assert overlay.x == 14
        assert isinstance(overlay, Overlay)
        assert overlay.has_changed() == False
        overlay._internal_state = 92
        assert overlay.has_changed() == True

    def test_task_creation(self) -> None:
        task = MyTask(task_id='123', task_ref=do_nothing, args=[], kwargs={})
        assert len(task.parent_ids) == 0
        assert len(task.inputs) == 2
        assert len(task.outputs) == 1