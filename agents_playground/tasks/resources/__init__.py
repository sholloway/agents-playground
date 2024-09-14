from enum import IntEnum
from typing import NamedTuple

from agents_playground.tasks.types import ResourceId, ResourceType

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
    
_task_resource_registry: TaskResourceRegistry = TaskResourceRegistry()

def global_task_resource_registry() -> TaskResourceRegistry:
    return _task_resource_registry