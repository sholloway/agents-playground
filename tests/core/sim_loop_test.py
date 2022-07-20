from pytest_mock import MockFixture

import time

from agents_playground.core.sim_loop import SimLoop
from agents_playground.core.waiter import Waiter
from agents_playground.simulation.context import SimulationContext
from agents_playground.simulation.sim_state import SimulationState
from agents_playground.styles.agent_style import AgentStyle

class TestSimLoop:
  def test_initialization(self, mocker: MockFixture) -> None:
    scheduler = mocker.Mock()
    loop = SimLoop(scheduler)
    assert loop.simulation_state == SimulationState.INITIAL

  def test_stop_looping(self, mocker: MockFixture) -> None:
    scheduler = mocker.Mock()
    context = mocker.Mock()
    mock_waiter = Waiter()
    mock_waiter.wait = mocker.Mock()
    looper = SimLoop(scheduler, waiter=mock_waiter)

    def stop_looping(*args) -> None:
      looper.simulation_state = SimulationState.ENDED

    looper._process_sim_cycle = mocker.Mock(side_effect=stop_looping)
    looper.simulation_state = SimulationState.RUNNING
    looper._sim_loop(context)

    looper._process_sim_cycle.assert_called_once()
    mock_waiter.wait.assert_not_called()

  def test_looping(self, mocker: MockFixture) -> None:
    scheduler = mocker.Mock()
    context = mocker.Mock()
    mock_waiter = Waiter()
    mock_waiter.wait = mocker.Mock()
    looper = SimLoop(scheduler, waiter=mock_waiter)

    def stop_looping(*args) -> None:
      looper.simulation_state = SimulationState.ENDED

    def pause_looping(*args) -> None:
      looper.simulation_state = SimulationState.STOPPED

    mock_waiter.wait.side_effect = stop_looping
    looper._process_sim_cycle = mocker.Mock(side_effect=pause_looping)
    looper.simulation_state = SimulationState.RUNNING

    looper._sim_loop(context)

    looper._process_sim_cycle.assert_called_once()
    mock_waiter.wait.assert_called_once()