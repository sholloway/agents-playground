import pytest

from agents_playground.fp import MaybeMutator, MutatorException, NothingMutator, SomethingMutator
from agents_playground.fp.functions import identity

class Calculator:
  """
  A simple calculator class for testing mutations.
  """
  def __init__(self) -> None:
    self._sub_total: float = 0.0

  def add(self, value: float) -> float:
    self._sub_total += value 
    return self._sub_total
  
  def add_many(self, *args: float) -> float:
    self._sub_total += sum(args) 
    return self._sub_total
  
  def subtract(self, value: float) -> float:
    self._sub_total -= value 
    return self._sub_total
  
  def total(self) -> float:
    return self._sub_total
  
  def clear(self) -> float:
    self._sub_total = 0.0
    return self._sub_total
      
class TestMaybeMutator:
  def test_maybe_can_be_something(self) -> None:
    maybe = MaybeMutator.from_optional(5)
    assert isinstance(maybe, SomethingMutator)

  def test_maybe_can_be_nothing(self) -> None:
    maybe = MaybeMutator.from_optional(None)
    assert isinstance(maybe, NothingMutator)

  def test_maybe_is_a_functor(self) -> None:
    list_of_maybe_instances = [
      MaybeMutator.from_optional(5),
      SomethingMutator('abc'),
      MaybeMutator.from_optional(None),
      SomethingMutator(True),
      NothingMutator()
    ]

    mapped_maybe_instances = [maybe.map(identity) for maybe in list_of_maybe_instances]
    unwrapped_values = [maybe.unwrap() for maybe in mapped_maybe_instances]
      
    assert unwrapped_values == [5, 'abc', None, True, None]

  def test_something_can_mutate(self) -> None:
    maybe = MaybeMutator.from_optional(Calculator())
    maybe.mutate([('add', 1)])
    assert maybe.unwrap().total() == 1

    maybe.mutate([('subtract', 2)])
    assert maybe.unwrap().total() == -1
    
    maybe.mutate([('add_many', 1, 2, 3, 4, 5)])
    assert maybe.unwrap().total() == 14
    
    maybe.mutate([('clear',), ('add', 4), ('add_many', 1, 2)])
    assert maybe.unwrap().total() == 7

  def test_mutators_throws_exceptions(self) -> None:
    maybe = MaybeMutator.from_optional(Calculator())
    with pytest.raises(MutatorException) as mutate_error:
      maybe.mutate([('bad_method_name',)])

    assert str(mutate_error.value) == 'Method bad_method_name not found.'

    

