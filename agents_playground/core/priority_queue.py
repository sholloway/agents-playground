from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from heapq import heappop, heappush
import itertools
from typing import Dict, Generic, List, Optional, Tuple, TypeVar, Union

# Represents an item that is prioritized by the queue. Could be a callable or data structure.
# It may be better to do something like Union[Callable, Any]
PriorityItem = TypeVar('PriorityItem')

# Represents the lookup ID of the PriorityItem. Used for deletion or updates.
ItemId = TypeVar('ItemId')

# Represents a priority value in the Priority Queue.
QueuePriority = Union[int, float]

# A constant that represents an item that has been removed from the queue.
class PriorityQueueCharacteristics(Enum):
  REMOVED_ITEM = 'REMOVED_ITEM'

@dataclass(order=True)
class PriorityItemDecorator(Generic[PriorityItem, ItemId]):
  """
  Wraps an item stored in the priority queue to enable heap comparisons.

  Comparison is done with the generated __lt__() method. 
  a(priority, count) < b(priority, count)
  """
  #Note: The order of the fields matters for the __lt__ method.
  priority: float 
  count: int
  id: ItemId = field(compare=False)
  item: Union[PriorityItem, PriorityQueueCharacteristics] = field(compare=False)

class PriorityQueue:
  """A generic priority queue implemented with a min heap."""
  def __init__(self):
    self._items: List[PriorityItemDecorator] = [] # A min heap.
    self._index: Dict[ItemId, PriorityItemDecorator] = {} # An index of the items in the heap.
    self._counter = itertools.count() # A counter for tracking the sequence of items.
    
  def push(self, item: PriorityItem, item_id: ItemId, priority: QueuePriority=0) -> PriorityQueue:
    """
    Add an item to the priority queue. Items are arranged in the queue 
    by their associated priority. The item with the smallest priority is listed first.
    If an item is already in the queue, it is removed first before adding it which 
    serves as an update.

    Returns
    The instance of the priority queue.
    """

    if item_id in self._index:
      self.remove(item_id)

    count = next(self._counter)
    entry = PriorityItemDecorator(priority, count, item_id, item)
    self._index[item_id] = entry
    heappush(self._items, entry) 
    return self

  def pop(self) -> Tuple[float, PriorityItem]:
    """
    Removes the item in the queue with the highest priority (smallest value).

    Returns
    A tuple of the priority and item.

    Throws
    Raises a KeyError if called on an empty queue.
    """

    # There could be removed items, so keep popping until an item is found.
    while len(self._items) > 0:
      entity:PriorityItemDecorator = heappop(self._items)
      if entity.item is not PriorityQueueCharacteristics.REMOVED_ITEM:
        self._remove_from_index(entity.id)
        return (entity.priority, entity.item)
    # If the queue is exhausted, then throw an exception.
    raise KeyError('Cannot pop from an empty priority queue.')

  def remove(self, item_id: ItemId) -> PriorityQueue:
    """
    Removes an item from the queue if it exists. Does nothing if the item 
    doesn't exist in the queue.

    Returns
    The instance of the priority queue.
    """
    entry: Optional[PriorityItemDecorator] = self._remove_from_index(item_id)

    # Update the PriorityBundle (which is still in self._items) to point to the REMOVED_ITEM
    # value. The bundle will be removed from the list of PriorityBundle items
    # during the PriorityQueue.pop() calls.   
    if entry is not None:
      entry.item = PriorityQueueCharacteristics.REMOVED_ITEM
    return self

  def index(self, item_id: ItemId) -> Optional[PriorityItemDecorator]:
    """Enables looking up an item in the queue by it's ID."""
    return self._index[item_id] if item_id in self._index else None
  
  def __str__(self) -> str:
    return self._items.__str__()
    
  def __contains__(self, item_id: ItemId) -> bool:
    """
    Determines if an item is already in the queue.

    Example
    item_id in queue
    """
    return item_id in self._index

  def __len__(self) -> int:
    """
    Supports using the len() with the priority queue.
    
    Returns
    The length of the queue. This includes items marked as removed.
    """
    return len(self._items)

  def _remove_from_index(self, item_id: ItemId) -> Optional[PriorityItemDecorator]:
    return self._index.pop(item_id) if item_id in self._index else None