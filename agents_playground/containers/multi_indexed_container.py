from collections import defaultdict
from collections.abc import Sequence
from operator import itemgetter
import sys
from typing import Iterator, TypeVar

from agents_playground.containers.types import MultiIndexedContainerLike
from agents_playground.fp import Maybe, Nothing, Something
from agents_playground.sys.logger import get_default_logger
from agents_playground.sys.profile_tools import total_size


D = TypeVar("D")
I = TypeVar("I")
N = TypeVar("N")

type _Index = int
type _Id = int
type _Name = str
type _Tag = str


class MultiIndexedContainerError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class MultiIndexedContainer(MultiIndexedContainerLike[D]):
    """
    A collection of items that are indexed by an ID and a Name.
    """

    def __init__(self) -> None:
        super().__init__()
        self._data: list[D | None] = []
        self._id_index: dict[_Id, _Index] = {}
        self._name_index: dict[_Name, _Index] = {}

        # Track indexes that can be reused.
        self._recycle_bin: set[_Index] = set()

    def clear(self) -> None:
        """
        Purge all items in the collection.
        """
        self._id_index.clear()
        self._name_index.clear()
        self._recycle_bin.clear()
        self._data.clear()

    def track(self, item: D, id: int, name: str) -> None:
        """
        Add an item to the collection and index it by both an ID type and a Name type.
        """
        if id in self._id_index:
            raise MultiIndexedContainerError(f"The Item {id} is already being tracked.")

        # Is there an index that can be recycled?
        if len(self._recycle_bin) > 0:
            index = self._recycle_bin.pop()
            self._data[index] = item
        else:
            self._data.append(item)
            index = len(self._data) - 1

        # Index the item by ID and Name.
        self._id_index[id] = index
        self._name_index[name] = index

    def filter(
        self, attr_name: str, filter: Sequence, inclusive: bool = True
    ) -> tuple[D, ...]:
        """
        Find all items in the collection that has an attribute with a value specified in the
        filter.

        Args:
            - attr_name: The name of the attribute to filter by.
            - filter: The list of values to compare to attribute to.
            - inclusive: If True, then find items whose attribute's value is in the filter.
              If False, find the items whose attribute's value is NOT in the filter.

        Returns:
        A tuple of the found items.
        """
        if inclusive:
            items = [
                item
                for item in self._data
                if item is not None
                and hasattr(item, attr_name)
                and getattr(item, attr_name) in filter
            ]
        else:
            items = [
                item
                for item in self._data
                if item is not None
                and hasattr(item, attr_name)
                and getattr(item, attr_name) not in filter
            ]
        return tuple(items)

    def release(self, ids: Sequence[I]) -> int:
        """
        Given a list of IDs, remove the corresponding items from the collection.
        IDs that aren't in the collection are ignored.

        Returns
        The method returns the number of items there were removed.
        """
        count = 0
        for id in ids:
            if id not in self._id_index:
                # Bad ID, skip and continue.
                get_default_logger().debug(
                    f"The ID {id} was not found in the MultiIndexedContainer."
                )
                continue

            # Find the location of the task and fetch it.
            index = self._id_index[id]
            item = self[id]

            # Remove the item from the collection.
            name = getattr(item, "name")  # TODO: Find a better way to do this.
            get_default_logger().debug(
                f"Removing the item {name} (with id {id}) the MultiIndexedContainer."
            )
            del self._name_index[name]
            del self._id_index[id]
            self._data[index] = None
            self._recycle_bin.add(index)
            count += 1
        return count

    def get(self, key: int | str) -> Maybe[D]:
        """
        Similar to task_resource["my_resource"] but returns the result
        wrapped in a Maybe. If the resource is not tracked then returns
        a Nothing instance.
        """
        if key in self:
            return Something(self[key])
        else:
            return Nothing()

    def __getitem__(self, key: int | str) -> D:
        """Finds an item definition by its alias."""
        index: int
        match key:
            case int(key):
                index = self._id_index[key]
            case str(key):
                index = self._name_index[key]
            case _:
                raise MultiIndexedContainerError("Unhandled key type.")
        item = self._data[index]
        if item is None:
            raise MultiIndexedContainerError("No item with key {key} was found.")
        return item

    def __len__(self) -> int:
        return len(self._id_index)

    def __contains__(self, key: int | str) -> bool:
        """
        Determine if a key is used to index an item.
        """
        does_contain: bool
        match key:
            case int(key):
                does_contain = key in self._id_index
            case str(key):
                does_contain = key in self._name_index
            case _:
                raise MultiIndexedContainerError("Unhandled key type.")

        return does_contain

    def __iter__(self) -> Iterator:
        """Enables iterating over all the items."""
        return self._data.__iter__()

    def __sizeof__(self) -> int:
        """
        Calculate the size (in bytes) of the collection.
        """
        base_size: int = sys.getsizeof(super())
        return (
            base_size
            + total_size(self._data)
            + total_size(self._id_index)
            + total_size(self._name_index)
            + total_size(self._recycle_bin)
        )