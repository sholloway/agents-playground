import pytest

from agents_playground.fp import (
  Either, 
  EitherException
)

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