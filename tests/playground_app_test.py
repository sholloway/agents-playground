from agents_playground.app.playground_app import PlaygroundApp
from agents_playground.core.observe import Observer

from pytest_mock import MockerFixture
from agents_playground.sims.pulsing_circle_sim import PulsingCircleSim

from agents_playground.sims.single_agent_simulation import SingleAgentSimulation

class TestPlaygroundAppTest:
  def test_app_is_observer(self):
    assert issubclass(PlaygroundApp, Observer)

  def test_app_can_launch_simulations(self, mocker: MockerFixture) -> None:
    app = PlaygroundApp()
    
    magic_sim = mocker.MagicMock()
    primary_window_mock = mocker.PropertyMock()
    type(magic_sim).primary_window = primary_window_mock
    app._build_simulation = mocker.MagicMock(return_value = magic_sim)
    assert app.active_simulation is None

    app._launch_simulation(app._menu_items['sims']['pulsing_circle_sim'], None, None)
    assert app.active_simulation is not None

    primary_window_mock.assert_called_once()
    magic_sim.attach.assert_called_once()
    magic_sim.launch.assert_called_once()