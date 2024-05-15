"""
Module that defines a set of collection protocols that include
the additional methods required for the memory model.

This merges the contacts of the collections.abc abstract classes
with the Agent focused protocols.
"""

from __future__ import annotations
from math import inf
import sys
from typing import (
    AbstractSet,
    Any,
    Callable,
    ItemsView,
    Iterable,
    Iterator,
    KeysView,
    SupportsIndex,
    Tuple,
    ValuesView,
    Protocol,
    TypeVar,
    Collection as BaseCollection,
    cast,
    overload,
)
from typing_extensions import Self

from agents_playground.agents.spec.tick import Tick


class SupportsMemoryMethods(Tick, Protocol):
    """
    This is the extension point for any additional methods
    required by the memory container.
    """

    ...


T = TypeVar("T")
S = TypeVar("S")
T_co = TypeVar("T_co", covariant=True)


class Collection(SupportsMemoryMethods, BaseCollection[T_co], Protocol[T_co]): ...


SequenceStorageItem = TypeVar("SequenceStorageItem", covariant=True)


class Sequence(SupportsMemoryMethods, Protocol[SequenceStorageItem]):
    """Contract that mixes Tick with collections.abc.Sequence."""

    def count(self, value: Any) -> int: ...

    def __contains__(self, key: object) -> bool: ...

    def __getitem__(self, key: SupportsIndex) -> SequenceStorageItem: ...

    def __len__(self) -> int: ...

    def __iter__(self) -> Iterator[SequenceStorageItem]: ...

    def __reversed__(self) -> Iterator[SequenceStorageItem]: ...

    def index(
        self, item: Any, start: SupportsIndex = 0, stop: SupportsIndex = sys.maxsize
    ) -> int: ...


class MutableSequence(Sequence[T], Protocol[T]):
    def __setitem__(self, key: SupportsIndex, value: T) -> None: ...

    def __delitem__(self, key: SupportsIndex | slice) -> None: ...

    def __iadd__(self, value: Iterable[T]) -> Self: ...

    def append(self, __object: T) -> None: ...

    def insert(self, index: SupportsIndex, item: T) -> None: ...

    def extend(self, __iterable: Iterable[T]) -> None: ...

    def pop(self, index: SupportsIndex = -1) -> T: ...

    def remove(self, value: T) -> None: ...

    def reverse(self) -> None: ...


class Set(SupportsMemoryMethods, Protocol[T]):
    def isdisjoint(self, __s: Iterable[T]) -> bool: ...

    def __contains__(self, __o: object) -> bool: ...

    def __and__(self, value: AbstractSet[object]) -> Set[T]: ...

    def __eq__(self, other: object) -> bool: ...

    def __ge__(self, value: AbstractSet[object]) -> bool: ...

    def __gt__(self, value: AbstractSet[object]) -> bool: ...

    def __iter__(self) -> Iterator[T]: ...

    def __le__(self, value: AbstractSet[object]) -> bool: ...

    def __len__(self) -> int: ...

    def __lt__(self, value: AbstractSet[object]) -> bool: ...

    def __ne__(self, value: object) -> bool: ...

    def __or__(self, value: AbstractSet[S]) -> Set[T | S]: ...

    def __sub__(self, value: AbstractSet[T | None]) -> Set[T]: ...

    def __xor__(self, value: AbstractSet[S]) -> Set[T | S]: ...


class MutableSet(Set, Protocol[T]):
    def add(self, __element: T) -> None: ...

    def clear(self) -> None: ...

    def discard(self, element: T) -> None: ...

    def pop(self, index: SupportsIndex = -1) -> T: ...

    def remove(self, element: T) -> None: ...

    def __ior__(self, value: AbstractSet[S]) -> MutableSet[T | S]: ...

    def __iand__(self, value: AbstractSet[S]) -> MutableSet[T | S]: ...

    def __isub__(self, value: AbstractSet[S]) -> MutableSet[T | S]: ...

    def __ixor__(self, value: AbstractSet[S]) -> MutableSet[T | S]: ...


KT = TypeVar("KT")
VT = TypeVar("VT", covariant=True)


class Mapping(SupportsMemoryMethods, Protocol[KT, VT]):
    @overload
    def get(self, key: KT) -> VT | None: ...

    @overload
    def get(self, key: KT, default: VT | T) -> VT | T: ...

    def items(self) -> ItemsView[KT, VT]: ...

    def keys(self) -> KeysView[KT]: ...

    def values(self) -> ValuesView[VT]: ...

    def __contains__(self, key: object) -> bool: ...

    def __eq__(self, other: object) -> bool: ...

    def __getitem__(self, key: KT) -> VT: ...

    def __iter__(self) -> Iterator[KT]: ...

    def __len__(self) -> int: ...

    def __ne__(self, other: object) -> bool: ...


VT_co = TypeVar("VT_co", covariant=True)


class SupportsKeysAndGetItem(Protocol[KT, VT_co]):
    def keys(self) -> Iterable[KT]: ...

    def __getitem__(self, key: KT) -> VT_co: ...


MV = TypeVar("MV")


class MutableMapping(Mapping[KT, MV], Protocol[KT, MV]):
    def clear(self) -> None: ...

    def pop(self, key: KT) -> MV: ...

    def popitem(self) -> Tuple[KT, MV]: ...

    def setdefault(self, key: KT, default: MV) -> MV: ...

    @overload
    def update(self, m: SupportsKeysAndGetItem[KT, MV], **kwargs: MV) -> None: ...

    @overload
    def update(self, m: Iterable[tuple[KT, MV]], **kwargs: MV) -> None: ...

    @overload
    def update(self, **kwargs: MV) -> None: ...

    def __setitem__(self, key: KT, value: MV) -> None: ...

    def __delitem__(self, key: KT) -> None: ...


INT_INFINITY: int = cast(int, inf)


def do_nothing(**kwargs) -> None:
    """A pass through function used to simplify defaults."""
    return


TTLItem = TypeVar("TTLItem", contravariant=True)


class SupportsTTL(SupportsMemoryMethods, BaseCollection, Protocol[TTLItem]):
    def store(
        self, item: TTLItem, ttl: int = INT_INFINITY, tick_action: Callable = do_nothing
    ) -> None: ...

    def ttl(self, item: TTLItem) -> int: ...

    def clear(self) -> None: ...
