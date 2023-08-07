from pytest_mock import MockerFixture
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