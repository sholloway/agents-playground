from collections.abc import Sequence
from typing import Iterator, Protocol, TypeVar

from agents_playground.fp import Maybe

D = TypeVar("D")
I = TypeVar("I")
N = TypeVar("N")


class TaggableContainerLike(Protocol[D]):
    def track(self, item: D, id: int, name: str) -> None:
        """
        Add an item to the collection and index it by both an ID type and a Name type.
        """

    def tagged_items(self, tag_or_tags: str | Sequence[str]) -> tuple[D]:
        """
        Given a tag or sequence of tags, find all of the tagged items.
        Ignores tags that don't exist.
        """
        ...

    def tag(self, key: int | str, tag: str) -> None:
        """Associates a tag with an item. Prevents double tagging.

        Args:
            - key: Either the ID or Name of the item.
            - tag: The alias to index the item by.
        """

    def remove_tag(self, key: int | str, tag: str) -> None:
        """Removes a tag from being associated with an item."""
        ...

    def delete_tag(self, tag: str) -> None:
        """
        Removes a tag completely from the resource registry.
        Note that this does not remove any items associated with the tag.
        """


class MultiIndexedContainerLike(Protocol[D]):
    def clear(self) -> None:
        """
        Purge all items in the collection.
        """

    def track(self, item: D, id: int, name: str) -> None:
        """
        Add an item to the collection and index it by both an ID type and a Name type.
        """

    def filter(
        self, attr_name: str, filter: Sequence, inclusive: bool = True
    ) -> tuple[D, ...]:
        """
        Find all items in the collection that has an attribute with a value specified in the
        filter.

        Args:
            - attr_name: The name of the attribute to filter by.
            - filter: The list of values to compare to attribute to.
            - inclusive: If True, then find items whose attribute's value is in the filter. If False, find the items whose attribute's value is NOT in the filter.

        Returns:
        A tuple of the found items.
        """
        ...

    def release(self, ids: Sequence[I]) -> int:
        """
        Given a list of IDs, remove the corresponding items from the collection.
        IDs that aren't in the collection are ignored.

        Returns
        The method returns the number of items there were removed.
        """
        ...

    def get(self, key: int | str) -> Maybe[D]:
        """
        Similar to task_resource["my_resource"] but returns the result
        wrapped in a Maybe. If the resource is not tracked then returns
        a Nothing instance.
        """
        ...
    
    def __getitem__(self, key: int | str) -> D:
        """Finds an item definition by its alias."""
        ...

    def __len__(self) -> int: ...

    def __contains__(self, key: int | str) -> bool:
        """
        Determine if a key is used to index an item.
        """
        ...

    def __iter__(self) -> Iterator:
        """Enables iterating over all the items."""
        ...

    def __sizeof__(self) -> int:
        """
        Calculate the size (in bytes) of the collection.
        """
        ...