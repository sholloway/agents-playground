from typing import Type

from agents_playground.tasks.predefined.generic_task import GenericTask
from agents_playground.tasks.registry import global_task_registry
from agents_playground.tasks.resources import TaskResource, TaskResourceStatus, global_task_resource_registry
from agents_playground.tasks.types import ResourceId, ResourceType, TaskDef


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
        global_task_registry().register(self._name, task_def)
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
        global_task_resource_registry().register(
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
        global_task_resource_registry().register(
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