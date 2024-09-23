from collections.abc import Callable

from agents_playground.tasks.graph.types import TaskGraphLike
from agents_playground.tasks.predefined.generic_task import GenericTask
from agents_playground.tasks.registry import global_task_registry
from agents_playground.tasks.resources import (
    TaskResourceRegistry,
    global_task_resource_registry,
)
from agents_playground.tasks.types import (
    ResourceName,
    ResourceType,
    TaskDef,
    TaskName,
    TaskResourceDef,
)


class task:
    """
    Marks a class as a task type. This has the following effects:
    - Registering a task in the task registry so it can be referenced in a scene.json file.
    - The task can be dynamically provisioned when a simulation is loaded.
    - The function marked with @task is bound with an instance of TaskDef.
    """

    def __init__(
        self,
        name: str | None = None,
        require_before: list[TaskName] = [],
        run_if: Callable[[], bool] = lambda: True,
        pin_to_main_thread: bool = False,
    ) -> None:
        """
        Register a function as a task.

        Args:
            - name (Optional): The name to register the task as. If none is provided the name of the decorated function is used.
            - require_before (Optional): A list of tasks that must be run before this task may run.
            - run_if (Optional): A function that is evaluated before the task is run. If it returns a False value then the task is not run.
            - pin_to_main_thread (Optional): Signals to the task runner that this task must only be run in the main thread.
        """
        self._name = name
        self._require_before = require_before
        self._run_if = run_if
        self._pin_to_main_thread = pin_to_main_thread

    def __call__(self, func: Callable[[TaskGraphLike], None]) -> TaskDef:
        name: str = self._name if self._name else func.__qualname__
        task_def = TaskDef(
            name=name,
            type=GenericTask,
            action=func,
            run_if=self._run_if,
            pin_to_main_thread=self._pin_to_main_thread,
        )
        task_def.required_before_tasks = self._require_before
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
        registry: TaskResourceRegistry = global_task_resource_registry()
        if self._resource_name not in registry:
            registry.register(
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
        registry: TaskResourceRegistry = global_task_resource_registry()
        if self._resource_name not in registry:
            registry.register(
                self._resource_name,
                TaskResourceDef(self._resource_name, self._resource_type),
            )

        if self._resource_name not in task_def.outputs:
            task_def.outputs.append(self._resource_name)
        return task_def
