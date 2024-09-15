from typing import Callable, Type

from agents_playground.tasks.predefined.generic_task import GenericTask
from agents_playground.tasks.registry import global_task_registry
from agents_playground.tasks.resources import global_task_resource_registry
from agents_playground.tasks.types import (
    ResourceId,
    ResourceName,
    ResourceType,
    TaskDef,
    TaskResourceDef,
)


class task:
    """
    Marks a class as a task type. This has the following effects:
    - Registering a task in the task registry so it can be referenced in a scene.json file.
    - The task can be dynamically provisioned when a simulation is loaded.
    - The class marked with @task is replaced at run time with an instance of TaskDef.

    TODO: Either make this have a type parameter (e.g. Computer, General, Render)
          or have different decorators for different types.
    """

    def __init__(self, name: str | None = None) -> None:
        self._name = name

    def __call__(self, func: Callable) -> TaskDef:
        name: str = self._name if self._name else func.__qualname__
        task_def = TaskDef(name=name, type=GenericTask, action=func)
        global_task_registry().register(name, task_def)
        return task_def


class task_input:
    """
    Marks a task definition as requiring a registered input. This has the following effects:
    - A TaskResource instance is instantiated with a status of RESERVED.
    - The TaskResource instance is registered in the task resource registry. Existing tasks are not replaced.
    - The task marked with @task_input has its metadata assigned the TaskResource in its list of inputs.
    """

    def __init__(self, type: ResourceType, name: ResourceName) -> None:
        self._resource_type = type
        self._resource_name = name

    def __call__(self, task_def: TaskDef) -> TaskDef:
        # Register the input resource.
        global_task_resource_registry().register(
            self._resource_name,
            TaskResourceDef(self._resource_name, type=self._resource_type),
        )

        # Associate the resource with the task definition.
        if self._resource_name not in task_def.inputs:
            task_def.inputs.append(self._resource_name)

        return task_def


class task_output:
    """
    Marks a task as requiring a registered output. This has the following effects:
    - The a TaskResource instance is instantiated with a status of RESERVED.
    - The TaskResource instance is registered in the task resource registry. Existing tasks are not replaced.
    - The task marked with @task_output has its task definition assigned the TaskResource in its list of outputs.
    """

    def __init__(self, type: ResourceType, name: ResourceName) -> None:
        self._resource_type = type
        self._resource_name = name

    def __call__(self, task_def: TaskDef) -> TaskDef:
        global_task_resource_registry().register(
            self._resource_name,
            TaskResourceDef(self._resource_name, self._resource_type),
        )
        if self._resource_name not in task_def.outputs:
            task_def.outputs.append(self._resource_name)
        return task_def
