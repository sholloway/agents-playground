from pytest_mock import MockFixture
import dearpygui.dearpygui as dpg
from agents_playground.core.simulation import (
  Simulation, 
  SimulationEvents, 
  SimulationState, 
  SimulationStateTable, 
  SimulationStateToLabelMap, 
  RUN_SIM_TOGGLE_BTN_START_LABEL, 
  RUN_SIM_TOGGLE_BTN_STOP_LABEL
)

class FakeSimulation(Simulation):
  def _initial_render(self) -> None:
    pass

  def _bootstrap_simulation_render(self) -> None:
    pass

  def _sim_loop(self, **args):
    pass

  def _setup_menu_bar_ext(self) -> None:
    pass
class TestSimulation:
  dpg.create_context()
  
  def test_initial_state(self, mocker: MockFixture) -> None:  
    fake = FakeSimulation()
    # fake._initial_render = mocker.MagicMock()
    # fake._bootstrap_simulation_render = mocker.MagicMock()
    # fake._sim_loop = mocker.MagicMock()
    # fake._setup_menu_bar_ext = mocker.MagicMock()

    assert fake.simulation_state is SimulationState.INITIAL

  def test_window_closed_event(self, mocker: MockFixture) -> None:
    mocker.patch('agents_playground.core.observe.Observable.notify')
    fake = FakeSimulation()
    fake._handle_sim_closed(None, None, None)
    assert fake.simulation_state is SimulationState.ENDED
    fake.notify.assert_called_once()
    fake.notify.assert_called_with(SimulationEvents.WINDOW_CLOSED.value)