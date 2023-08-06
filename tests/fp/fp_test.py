
from agents_playground.fp import Just, Maybe, Nothing, Something, identity


class TestJust:
  def test_unwrap_returns_inner_value(self) -> None: 
    value: int = 5
    wrapped = Just(value)
    assert wrapped.unwrap() == value 

  def test_just_equality(self) -> None:
    assert Just(5) == Just(5)
    assert Just(72.123) == Just(72.123)
    assert Just(7) == Just(7.0)
    assert Just('abc') == Just('abc')
    assert Just(True) == Just(True)
    assert Just(True) != Just(False)

class TestMaybe:
  def test_maybe_can_be_something(self) -> None:
    maybe = Something(5)
    assert isinstance(maybe, Maybe)
  
  def test_maybe_can_be_nothing(self) -> None:
    maybe = Nothing()
    assert isinstance(maybe, Maybe)

  def test_maybe_is_a_functor(self) -> None:
    list_of_maybe_instances = [
      Something(5),
      Something('abc'),
      Nothing(),
      Something(True),
      Nothing()
    ]

    mapped_maybe_instances = [maybe.map(identity) for maybe in list_of_maybe_instances]
    unwrapped_values = [maybe.unwrap() for maybe in mapped_maybe_instances]
      
    assert unwrapped_values == [5, 'abc', None, True, None]