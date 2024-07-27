from pytest_mock import MockFixture
from agents_playground.core.time_utilities import MS_PER_SEC

from agents_playground.core.waiter import Waiter


class TestWaiter:
    def test_waiting(self, mocker: MockFixture) -> None:
        patched_sleep = mocker.patch("agents_playground.core.waiter.sleep")
        waiter = Waiter()
        waiter.wait(5)
        patched_sleep.assert_called_once_with(5)

    def test_waiting_until_deadline(self, mocker: MockFixture) -> None:
        RIGHT_NOW = 15000
        DEADLINE = 33000
        TIME_TO_WAIT = (DEADLINE - RIGHT_NOW) / MS_PER_SEC
        mocker.patch(
            "agents_playground.core.time_utilities.TimeUtilities.now",
            return_value=RIGHT_NOW,
        )
        waiter = Waiter()
        waiter.wait = mocker.Mock()
        waiter.wait_until_deadline(DEADLINE)
        waiter.wait.assert_called_once_with(TIME_TO_WAIT)

    def test_not_waiting_for_the_past(self, mocker: MockFixture) -> None:
        RIGHT_NOW = 15000
        DEADLINE = 13000  # In the past
        TIME_TO_WAIT = (DEADLINE - RIGHT_NOW) / MS_PER_SEC
        mocker.patch(
            "agents_playground.core.time_utilities.TimeUtilities.now",
            return_value=RIGHT_NOW,
        )
        waiter = Waiter()
        waiter.wait = mocker.Mock()
        waiter.wait_until_deadline(DEADLINE)
        waiter.wait.assert_not_called()
