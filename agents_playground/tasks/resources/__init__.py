from collections import defaultdict
from operator import itemgetter
from typing import Any
from agents_playground.counter.counter import Counter, CounterBuilder
from agents_playground.fp import Something
from agents_playground.tasks.types import (
    ResourceId,
    ResourceIndex,
    ResourceName,
    ResourceTag,
    TaskResourceDef,
    TaskResource,
    TaskResourceStatus,
)


class TaskResourceRegistryError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class TaskResourceRegistry:
    """
    Responsible for maintaining a registry of resources that can be provisioned.
    Dynamically populated by the decorators when a simulation is initialized.

    """

    def __init__(self) -> None:
        self._registered_resources: list[TaskResourceDef] = []
        self._name_index: dict[ResourceName, ResourceIndex] = {}
        self._resource_counter: Counter[int] = CounterBuilder.count_up_from_zero()

    def register(self, alias: str, resource_def: TaskResourceDef) -> None:
        """Alternative to trr[alias] = task_def."""
        self[alias] = resource_def

    def provision(
        self, alias: str, instance: Any | None = None, *args, **kwargs
    ) -> TaskResource:
        """
        Provision a resource for use in tasks.

        Args:
            - alias: The name of the resource to provision.
            - instance: An optional argument. If provided the value is assigned as the resource. If None is provided then an new instance of the mapped type is created.
            - args: Any positional parameters to pass to the resource being provisioned.
            - kwargs: Any named parameters to pass to the resource being provisioned.
        """
        if alias not in self._name_index:
            raise TaskResourceRegistryError(
                f"Attempted to provision a resource that was not registered. Could not find resource alias {alias}."
            )
        resource_def_index = self._name_index[alias]
        resource_def = self._registered_resources[resource_def_index]
        if instance is None:
            resource = resource_def.type(*args, **kwargs)
        else:
            resource = instance
        tr = TaskResource(
            resource_id=self._resource_counter.increment(),
            resource_name=alias,
            resource_status=TaskResourceStatus.ALLOCATED,
            resource=Something(resource),
        )
        return tr

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

    Resources have a name that identifies then in the registry.
    They can also be "tagged". A tag is a way to specify that a
    resource has a selectable characteristic.
    """

    def __init__(self) -> None:
        self._provisioned_resources: list[TaskResource] = []
        self._id_index: dict[ResourceId, ResourceIndex] = {}
        self._name_index: dict[ResourceName, ResourceIndex] = {}
        self._tags: dict[ResourceTag, list[ResourceIndex]] = defaultdict(list)

    def clear(self) -> None:
        self._id_index.clear()
        self._name_index.clear()
        self._tags.clear()
        self._provisioned_resources.clear()

    def track(self, resource: TaskResource) -> ResourceId:
        if resource.resource_id in self._id_index:
            raise TaskResourceTrackerError(
                f"The resource {resource.resource_id} is already being tracked."
            )

        self._provisioned_resources.append(resource)
        resource_index = len(self._provisioned_resources) - 1
        self._id_index[resource.resource_id] = resource_index
        self._name_index[resource.resource_name] = resource_index
        return resource.resource_id

    def tag(self, name: ResourceName, tag: ResourceTag) -> None:
        """Associates a tag with a MeshData instance.
        Prevents double tagging.
        """
        index: ResourceIndex = self._name_index[name]
        if index not in self._tags[tag]:
            self._tags[tag].append(index)

    def remove_tag(self, name: ResourceName, tag: ResourceTag) -> None:
        """Removes a tag from being associated with a resource."""
        index: ResourceIndex = self._name_index[name]
        if tag not in self._tags or index not in self._tags[tag]:
            return
        self._tags[tag].remove(index)

    def delete_tag(self, tag: str) -> None:
        """Removes a tag completely from the resource registry."""
        if tag in self._tags:
            del self._tags[tag]

    def filter(self, *tags: str) -> list[TaskResource]:
        """Finds all MeshData instances with the provided tags."""
        # Build a set of all the indexes of the meshes to be returned.
        resource_indexes: set[ResourceIndex] = set()
        for tag in tags:
            if tag in self._tags:
                resource_indexes.update(self._tags[tag])

        if len(resource_indexes) < 1:
            return []

        # Collect the meshes by their index.
        results = itemgetter(*resource_indexes)(self._provisioned_resources)
        return list(results) if isinstance(results, tuple) else [results]

    def __getitem__(self, key: ResourceId | ResourceName) -> TaskResource:
        """Finds a resource instance by its alias."""
        if isinstance(key, int):
            index = self._id_index[key]
        elif isinstance(key, str):
            index = self._name_index[key]
        return self._provisioned_resources[index]

    def __len__(self) -> int:
        return len(self._provisioned_resources)

    def __contains__(self, key: ResourceId | ResourceName) -> bool:
        if isinstance(key, int):
            return key in self._id_index
        elif isinstance(key, str):
            return key in self._name_index
