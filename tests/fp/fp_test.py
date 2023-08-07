
from typing import List
import pytest
from pytest_mock import MockerFixture
from agents_playground.fp import (
  Either, 
  EitherException, 
  Just, 
  Maybe, 
  Nothing, 
  Something
)
from agents_playground.fp.functions import chain, compose, curry, identity

class TestFPFunctions:
  def test_identity(self) -> None:
    assert identity(5) == 5
    assert identity(7.8) == 7.8
    assert identity(False) == False
    assert identity(True) == True
    assert identity('abc') == 'abc'

  def test_curry(self) -> None:
    @curry
    def add(a: int, b: int, c: int, d: int, e: int) -> int:
      return a + b + c + d + e
    assert add(1)(2)(3)(4)(5) == 15 # type: ignore

  def test_compose_calls_all(self, mocker: MockerFixture) -> None: 
    step_1 = mocker.Mock()
    step_2 = mocker.Mock()
    step_3 = mocker.Mock()
    step_4 = mocker.Mock()

    all_steps = compose(step_1, step_2, step_3, step_4)
    all_steps()

    step_1.assert_called_once()
    step_2.assert_called_once()
    step_3.assert_called_once()
    step_4.assert_called_once()

  def test_compose_vs_chain(self) -> None:
    step_1 = lambda i: i + 'step_1 '
    step_2 = lambda i: i + 'step_2 '
    step_3 = lambda i: i + 'step_3 '
    step_4 = lambda i: i + 'step_4 '

    composed_steps = compose(step_1, step_2, step_3, step_4)
    chained_steps = chain(step_1, step_2, step_3, step_4)

    assert composed_steps('').strip() == 'step_4 step_3 step_2 step_1'
    assert chained_steps('').strip() == 'step_1 step_2 step_3 step_4'



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

  def test_just_is_a_monad(self) -> None:
    just_some_monads = [
      Just(7),
      Just(True),
      Just('abc')
    ]
    
    results = [monad.bind(lambda i: Just(i)) for monad in just_some_monads]
    unwrapped_values = [maybe.unwrap() for maybe in results]
    assert unwrapped_values == [7, True, 'abc']

class TestMaybe:
  def test_maybe_can_be_something(self) -> None:
    maybe = Maybe.from_optional(5)
    assert isinstance(maybe, Something)
  
  def test_maybe_can_be_nothing(self) -> None:
    maybe = Maybe.from_optional(None)
    assert isinstance(maybe, Nothing)

  def test_maybe_is_a_functor(self) -> None:
    list_of_maybe_instances = [
      Maybe.from_optional(5),
      Something('abc'),
      Maybe.from_optional(None),
      Something(True),
      Nothing()
    ]

    mapped_maybe_instances = [maybe.map(identity) for maybe in list_of_maybe_instances]
    unwrapped_values = [maybe.unwrap() for maybe in mapped_maybe_instances]
      
    assert unwrapped_values == [5, 'abc', None, True, None]

double = lambda i: i*2
double_either = lambda i: Either.right(i*2)

class TestEither:
  def test_is_right(self) -> None:
    right = Either.right(5)
    assert right.is_right()
    assert not right.is_left()
  
  def test_is_left(self) -> None:
    left = Either.left(5)
    assert not left.is_right()
    assert left.is_left()

  def test_right_handed_wrap(self) -> None:
    assert Either.right(5).wrap(7).is_right()
  
  def test_left_handed_wrap(self) -> None:
    assert Either.left(5).wrap(7).is_left()

  def test_unwrap(self) -> None:
    assert Either.right(5).unwrap() == 5
    assert Either.left(7).unwrap() == 7

  def test_apply(self) -> None:
    # Use Case: Apply a Right Handed side that contains a function.
    assert Either.right(double).apply(Either.right(5)).unwrap() == 10

    ############################################################################
    # Error propagation use cases.
    # Use Case: Apply a left handed side.
    # This enables passing the existing error down the chain.
    # Applying a Left side, just returns the left side.
    assert Either.left(5).apply(Either.right(11)).unwrap() == 5

    # Use Case: Applying a right sided function to a left sided Either.
    # If there wasn't already an error, but the Either that is 
    # being applied to is an error, then propagate the error.
    assert Either.right(double).apply(Either.left('an error')).unwrap() == 'an error'

    ############################################################################
    # Use Case: Calling apply on an Either that doesn't contain a function.
    with pytest.raises(EitherException):
      Either.right('not a function').apply(Either.right(123)) # type: ignore

  def test_bind(self) -> None:
    # Use Case: The happy path.
    assert Either.right(5).bind(double_either).unwrap() == 10

    # Use Case: Propagate error.
    assert Either.left('an error').bind(double_either).unwrap() == 'an error'