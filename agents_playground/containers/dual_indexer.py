from collections import defaultdict
from collections.abc import Sequence
from operator import itemgetter
import sys
from typing import Iterator, TypeVar

from agents_playground.containers.types import MultiIndexedContainerLike
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

        # Store tags/labels of items. This enables looking up items beyond name/id.
        self._tags: dict[_Tag, set[_Index]] = defaultdict(set)

    def clear(self) -> None:
        """
        Purge all items in the collection.
        """
        self._id_index.clear()
        self._name_index.clear()
        self._tags.clear()
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

    def tagged_items(self, tag_or_tags: str | Sequence[str]) -> tuple[D]:
        """
        Given a tag or sequence of tags, find all of the tagged items.
        Ignores tags that don't exist.
        """
        # Elevate a single tag to be a tuple.
        tags = (tag_or_tags,) if isinstance(tag_or_tags, str) else tag_or_tags

        # Collect the indexes of all the tagged items.
        item_indexes: set[_Index] = set()
        for tag in tags:
            if tag in self._tags:
                item_indexes.update(self._tags[tag])

        if len(item_indexes) < 1:
            return tuple([])

        # Collect the items by their index.
        results = itemgetter(*item_indexes)(self._data)
        return results if isinstance(results, tuple) else tuple(results)

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
                continue

            # Find the location of the task and fetch it.
            index = self._id_index[id]
            item = self[id]

            # Remove the item from any tags.
            for _, tagged in self._tags.items():
                if id in tagged:
                    tagged.remove(id)
        
            # Remove the item from the collection.
            name = getattr(item, "name")  # TODO: Find a better way to do this.
            del self._name_index[name]
            del self._id_index[id]
            self._data[index] = None
            self._recycle_bin.add(index)
            count += 1
        return count

    def tag(self, key: int | str, tag: str) -> None:
        """Associates a tag with an item. Prevents double tagging.

        Args:
            - key: Either the ID or Name of the item.
            - tag: The alias to index the item by.
        """
        index: _Index
        match key:
            case int(key):
                index = self._id_index[key]
            case str(key):
                index = self._name_index[key]
            case _:
                raise MultiIndexedContainerError("Unhandled key type.")
        self._tags[tag].add(index)

    def remove_tag(self, key: int | str, tag: str) -> None:
        """Removes a tag from being associated with an item."""
        index: _Index
        match key:
            case int(key):
                index = self._id_index[key]
            case str(key):
                index = self._name_index[key]
            case _:
                raise MultiIndexedContainerError("Unhandled key type.")

        if tag not in self._tags or index not in self._tags[tag]:
            return

        self._tags[tag].remove(index)

    def delete_tag(self, tag: str) -> None:
        """
        Removes a tag completely from the resource registry.
        Note that this does not remove any items associated with the tag.
        """
        if tag in self._tags:
            del self._tags[tag]

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
