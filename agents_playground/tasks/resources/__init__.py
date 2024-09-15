from agents_playground.tasks.types import (
    ResourceId,
    ResourceName,
    TaskResourceDef,
    TaskResourceLike,
)


class TaskResourceRegistry:
    """
    Responsible for maintaining a registry of resources that can be provisioned.
    Dynamically populated by the decorators when a simulation is initialized.
    """

    def __init__(self) -> None:
        self._registered_resources: list[TaskResourceDef] = []
        self._name_index: dict[ResourceName, int] = {}

    def register(self, alias: str, resource_def: TaskResourceDef) -> None:
        """Alternative to trr[alias] = task_def."""
        self[alias] = resource_def

    def clear(self) -> None:
        self._name_index.clear()
        self._registered_resources.clear()

    def __setitem__(self, key: str, value: TaskResourceDef) -> None:
        if key in self._name_index:
            # It is valid that a resource be registered more than once.
            # For example, a buffer could be the output of one task and the input of another.
            return
        if value in self._registered_resources:
            index = self._registered_resources.index(value)
        else:
            self._registered_resources.append(value)
            index = len(self._registered_resources) - 1
        self._name_index[key] = index

    def __getitem__(self, key: str) -> TaskResourceDef:
        """Finds a TaskResource definition by its alias."""
        index = self._name_index[key]
        return self._registered_resources[index]

    def __len__(self) -> int:
        return len(self._name_index)

    def __contains__(self, key: str) -> bool:
        """Enables 'my_alias' in task_resource_registry."""
        return key in self._name_index


_task_resource_registry: TaskResourceRegistry = TaskResourceRegistry()


def global_task_resource_registry() -> TaskResourceRegistry:
    return _task_resource_registry


class TaskResourceTrackerError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class TaskResourceTracker:
    """
    Responsible for maintaining provisioned task resources.
    """

    def __init__(self) -> None:
        self._provisioned_resources: list[TaskResourceLike] = []
        self._id_index: dict[ResourceId, int] = {}
        self._name_index: dict[ResourceName, int] = {}

    def clear(self) -> None:
        self._id_index.clear()
        self._name_index.clear()
        self._provisioned_resources.clear()

    def track(self, resource: TaskResourceLike) -> ResourceId:
        if resource.id in self._id_index:
            raise TaskResourceTrackerError(
                f"The resource {resource.id} is already being tracked."
            )

        self._provisioned_resources.append(resource)
        resource_index = len(self._provisioned_resources) - 1
        self._id_index[resource.id] = resource_index
        self._name_index[resource.name] = resource_index
        return resource.id

    def __getitem__(self, key: ResourceId) -> TaskResourceLike:
        """Finds a TaskLike definition by its alias."""
        index = self._id_index[key]
        return self._provisioned_resources[index]

    def __len__(self) -> int:
        return len(self._provisioned_resources)

    def __contains__(self, key: ResourceId | ResourceName) -> bool:
        if isinstance(key, int):
            return key in self._id_index
        elif isinstance(key, str):
            return key in self._name_index