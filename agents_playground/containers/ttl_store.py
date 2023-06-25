from typing import Any, Dict, Iterator, cast
from collections.abc import Collection
from agents_playground.agents.spec.tick import Tick
from agents_playground.counter.counter import Counter, CounterBuilder


def expire(store: Dict[Any, Counter], item: Any) -> None:
  store.pop(item, None)

class TTLStore(Tick, Collection):
  """
  A container that automatically removes items with their time to live expires.
  Items must be hashable.
  """
  def __init__(self) -> None:
    self._store: Dict[Any, Counter] = {}

  def store(self, item: Any, ttl: int) -> None:
    """
    Stores an item with a TTL. If the item already exists, 
    then it's TTL countdown is reset to the new ttl.

    Args:
      - item: The item to store. This must be hashable.
      - ttl: The number of ticks the item will be retained.
    """
    if item in self._store:
      self._store[item].start = ttl
      self._store[item].reset()
    else:
      self._store[item] = CounterBuilder.integer_counter_with_defaults(
          start=ttl, 
          min_value=0,
          min_value_reached = expire
        )

  def tick(self) -> None:
    """Decrements the TTL of all the items in the store by 1."""
    item: Any
    items = list(self._store.keys())
    for item in items:
      self._store[item].decrement(store = self._store, item = item)

  def ttl(self, item: Any) -> int:
    """Returns the time to live for an item. Throws KeyError if the item doesn't exist."""
    return cast(int, self._store[item].value())
  
  def clear(self) -> None:
    """Removes all items from the store."""
    self._store.clear()

  def remove(self, item: Any) -> None:
    """Removes an item if it is in the store."""
    self._store.pop(item, None)

  def __len__(self) -> int:
    """Enables finding the size of the store with len(store)."""
    return self._store.__len__()
  
  def __iter__(self) -> Iterator:
    """Enables iterating over the items in the store."""
    return self._store.__iter__()
    ## TODO: Should this iterate over just the keys?

  def __contains__(self, __x: object) -> bool:
    """Enables doing membership tests with the 'in' keyword."""
    return self._store.__contains__(__x)
  
  def __repr__(self) -> str:
    header = f"Type: {self.__class__.__name__}"
    contains = [f'\tItem: {item}, TTL: {ttl.value()}' for item, ttl in self._store.items()]
    contains_str = '\n'.join(contains)
    return f"""
    {header}
    {contains_str}
    """.strip()