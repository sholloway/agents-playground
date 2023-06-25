
import pytest
from agents_playground.containers.ttl_store import TTLStore

@pytest.fixture
def ttl_store() -> TTLStore:
  ttl_store = TTLStore()
  ttl_store.store('A',3)
  ttl_store.store('B',2)
  ttl_store.store('C',1)
  return ttl_store

class TestTTLStore:
  def test_store_size(self, ttl_store: TTLStore) -> None:
    assert len(ttl_store) == 3

  def test_store_membership(self, ttl_store: TTLStore) -> None:
    assert 'A' in ttl_store
    assert 'B' in ttl_store
    assert 'C' in ttl_store
    assert 'D' not in ttl_store
    assert 'a' not in ttl_store

  def test_store_iteration(self, ttl_store: TTLStore) -> None:
    count = 0
    for item in ttl_store:
      count += 1

    assert count == 3

    store_iter = ttl_store.__iter__()
    assert 'A' == next(store_iter)
    assert 'B' == next(store_iter)
    assert 'C' == next(store_iter)

  def test_ttl(self, ttl_store: TTLStore) -> None:
    """
    Calling the tick function reduces the TTL of every item by 1. 
    Items are removed when their TTL reaches 0.
    """
    assert len(ttl_store) == 3
    assert 'A' in ttl_store
    assert 'B' in ttl_store
    assert 'C' in ttl_store

    ttl_store.tick()
    assert len(ttl_store) == 3
    assert 'A' in ttl_store
    assert 'B' in ttl_store
    assert 'C' in ttl_store
    
    ttl_store.tick()
    assert len(ttl_store) == 2
    assert 'A' in ttl_store
    assert 'B' in ttl_store
    assert 'C' not in ttl_store
    
    ttl_store.tick()
    assert len(ttl_store) == 1
    assert 'A' in ttl_store
    assert 'B' not in ttl_store
    assert 'C' not in ttl_store
   
    ttl_store.tick()
    assert len(ttl_store) == 0
    assert 'A' not in ttl_store
    assert 'B' not in ttl_store
    assert 'C' not in ttl_store

    ttl_store.tick()
    assert len(ttl_store) == 0

  def test_storing_an_item_twice(self, ttl_store: TTLStore) -> None:
    ttl_store.store('D', 4)
    assert ttl_store.ttl('D') == 4

    ttl_store.store('D', 7)
    assert ttl_store.ttl('D') == 7

  def test_clearing_the_store(self, ttl_store: TTLStore) -> None:
    assert len(ttl_store) == 3
    ttl_store.clear()
    assert len(ttl_store) == 0

  def test_removing_an_item(self, ttl_store: TTLStore) -> None:
    assert 'A' in ttl_store
    assert len(ttl_store) == 3
    
    ttl_store.remove('A')
    assert len(ttl_store) == 2
    assert 'A' not in ttl_store