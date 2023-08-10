
from agents_playground.fp import Just
from agents_playground.fp.containers import FPDict, FPList, FPSet


class TestFPList:
  def test_behaves_like_a_list(self) -> None:
    fpl = FPList([1,2,3,4])
    assert fpl == FPList([1,2,3,4])

    fpl.append(5)
    fpl.append(6)
    fpl.append(7)
    assert fpl == FPList([1,2,3,4,5,6,7])

    fpl.pop()
    fpl.pop()
    assert fpl == FPList([1,2,3,4,5])

    assert fpl[2] == 3
    assert fpl.index(3) == 2
    assert len(fpl) == 5
    assert fpl.count(3) == 1
    
    fpl_copy = fpl.copy()
    assert fpl_copy == FPList([1,2,3,4,5])

    fpl.extend([6,7,8,9])
    assert fpl == FPList([1,2,3,4,5,6,7,8,9])

    fpl.insert(5, 123)
    assert fpl == FPList([1,2,3,4,5,123,6,7,8,9])

    fpl.reverse()
    assert fpl == FPList([9,8,7,6,123,5,4,3,2,1])

    sorted = FPList([7,2,4,1,5,6])
    sorted.sort()
    assert sorted == FPList([1,2,4,5,6, 7])

    fpl.clear()
    assert len(fpl) == 0

  def test_can_map(self) -> None:
    """
    Test that FPList implements the Functor protocol.
    """
    fpl = FPList([1,2,3,4,5])
    squared = fpl.map(lambda i: i*i)
    assert squared == FPList([1,4,9, 16, 25])

  def test_is_wrappable(self) -> None:
    wrapped = FPList([]).wrap([1,2,3])
    assert wrapped == FPList([1,2,3])
    assert wrapped.unwrap() == [1,2,3]

  def test_it_can_apply(self) -> None:
    # Apply should work on wrappables. 
    operations = FPList([
      lambda i: i*i,
      lambda i: i*2,
      lambda i: i+1
    ])

    result: FPList[int] = operations.apply(Just(5))
    assert len(result) == 1 and result[0] == 51

  def test_it_can_apply_to_iterators(self) -> None:
    # Apply should work on wrap-ables that are also iterators.
    some_values = FPList([Just(3), Just(4), Just(5)])
    
    operations = FPList([
      lambda i: i*i,
      lambda i: i*2,
      lambda i: i+1
    ])

    results = operations.apply(some_values)
    assert results == FPList([19, 33, 51])

class TestFPDict:
  def test_behaves_like_a_dict(self) -> None:
    assert len(FPDict()) == 0
    assert len(FPDict({'a':123, 'b':456})) == 2

    dynamic = FPDict()
    dynamic['a'] = 22
    dynamic['b'] = 75
    dynamic['a'] = 14
    assert 'a' in dynamic
    assert 'b' in dynamic
    assert dynamic['a'] == 14
    assert dynamic['b'] == 75
  
    assert dynamic.copy() == FPDict({'a': 14, 'b': 75})
    assert FPDict.fromkeys(dynamic, 0) == FPDict({'a': 0, 'b': 0})
    assert dynamic.get('a') == dynamic['a']
    assert dynamic.get('b') == dynamic['b']
    assert dynamic.get('c', default='missing_value') == 'missing_value'

    assert list(dynamic.items()) == [('a', 14), ('b', 75)]
    assert list(dynamic.keys()) == ['a', 'b']
    assert list(dynamic.values()) == [14,75]

    assert 'd' not in dynamic
    dynamic.setdefault('d', 77)
    assert 'd' in dynamic
    assert dynamic['d'] == 77
    dynamic.setdefault('d', 100)
    assert dynamic['d'] == 77

    assert dynamic.pop('a') == 14
    assert 'a' not in dynamic

    assert dynamic.popitem() == ('b', 75)
    assert 'b' not in dynamic

    dynamic.update({'a': 'a is back', 'b': 'b is also back'})
    assert 'a' in dynamic
    assert 'b' in dynamic
    assert dynamic['a'] == 'a is back'
    assert dynamic['b'] == 'b is also back'
    
    dynamic.clear()
    assert len(dynamic) == 0

  def test_can_map(self) -> None:
    """
    Test that FPList implements the Functor protocol.
    """
    fp_dict = FPDict({'a':1, 'b':2, 'c':3, 'd':4})
    squared_dict = fp_dict.map(lambda v: v*v)
    assert squared_dict == FPDict({'a':1, 'b':4, 'c':9, 'd':16})

  def test_is_wrappable(self) -> None:
    wrapped = FPDict().wrap({'a': 123})
    assert wrapped == FPDict({'a': 123})
    assert wrapped.unwrap() == {'a': 123}

class TestFPSet:
  def test_behaves_like_a_set(self) -> None:
    assert len(FPSet()) == 0 
    assert len(FPSet([1,2,3])) == 3 
    assert len(FPSet([1,2,1,1,2,3])) == 3 
    assert FPSet([1,2,3]) == FPSet([3,2,1])

    fps = FPSet([1,2,3])
    fps.add(72)
    assert len(fps) == 4
    assert 72 in fps

    fps.discard(72)
    assert len(fps) == 3
    assert 72 not in fps

    item = fps.pop()
    assert item == 1
    assert 1 not in fps

    fps.remove(2)
    assert 2 not in fps

    assert fps.isdisjoint([4,5,6])
    assert not fps.isdisjoint([3, 4,5,6])

    fps.clear()
    assert len(fps) == 0
    
  def test_can_map(self) -> None:
    fps = FPSet([1,2,3,4])
    squared_set = fps.map(lambda v: v*v)
    assert squared_set == FPSet([1,4, 9, 16])

  def test_can_wrap(self) -> None:
    wrapped = FPSet().wrap(set([7,8,9]))
    assert wrapped == FPSet(set([7,9,8]))
    assert wrapped.unwrap() == set([8,7,9])

  def test_it_can_apply(self) -> None:
    # Apply should work on wrappables. 
    operations = FPSet([
      lambda i: i*i,
      lambda i: i*2,
      lambda i: i+1
    ])

    result: FPSet[int] = operations.apply(Just(5))
    assert len(result) == 1 
    assert result == FPSet([51])
    assert 51 in result

  def test_it_can_apply_to_iterators(self) -> None:
    # Apply should work on wrap-ables that are also iterators.
    some_values = FPList([Just(3), Just(4), Just(5)])
    
    operations = FPSet([
      lambda i: i*i,
      lambda i: i*2,
      lambda i: i+1
    ])

    results = operations.apply(some_values)
    assert results == FPSet([19, 33, 51])