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
  def __init__(self) -> None:
    super().__init__()
    self._sim_loop_tick_counter = 0
    self._max_sim_ticks = 3

  def _initial_render(self) -> None:
    pass

  def _bootstrap_simulation_render(self) -> None:
    pass

  def _setup_menu_bar_ext(self) -> None:
    pass

  def _sim_loop_tick(self, **args):
    self._sim_loop_tick_counter += 1
    if self._sim_loop_tick_counter >= self._max_sim_ticks:
      self.simulation_state = SimulationState.ENDED



class TestSimulation:
  dpg.create_context()
  
  def test_initial_state(self, mocker: MockFixture) -> None:  
    fake = FakeSimulation()
    assert fake.simulation_state is SimulationState.INITIAL

  def test_window_closed_event(self, mocker: MockFixture) -> None:
    mocker.patch('agents_playground.core.observe.Observable.notify')
    fake = FakeSimulation()
    fake._handle_sim_closed(None, None, None)
    assert fake.simulation_state is SimulationState.ENDED
    fake.notify.assert_called_once()
    fake.notify.assert_called_with(SimulationEvents.WINDOW_CLOSED.value)

  def test_starting_and_stopping_the_sim(self, mocker: MockFixture) -> None:
    fake = FakeSimulation()
    fake._update_ui = mocker.Mock()
    assert fake.simulation_state is SimulationState.INITIAL

    # 1st Call - Start the sim.
    fake._run_sim_toggle_btn_clicked(None, None, None)
    assert fake.simulation_state is SimulationState.RUNNING
    fake._update_ui.assert_called_once()
    
    # 2nd Call - Stop the sim.
    fake._run_sim_toggle_btn_clicked(None, None, None)
    assert fake.simulation_state is SimulationState.STOPPED
    assert fake._update_ui.call_count == 2
    
    # 3rd Call - Restart the sim.
    fake._run_sim_toggle_btn_clicked(None, None, None)
    assert fake.simulation_state is SimulationState.RUNNING
    assert fake._update_ui.call_count == 3

  def test_sim_loop(self, mocker: MockFixture) -> None:
    fake = FakeSimulation()
    fake._sim_run_rate = 0.0
    fake.simulation_state = SimulationState.RUNNING
    fake._sim_loop() # The FakeSimulation does 3 ticks.
    assert fake._sim_loop_tick_counter == 3