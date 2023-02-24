import os
from pathlib import Path
from agents_playground.app.playground_app import PlaygroundApp
from agents_playground.core.observe import Observer

from pytest_mock import MockerFixture

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

  def test_app_can_open_sim_project(self, mocker: MockerFixture) -> None:
    app = PlaygroundApp()

    # Mock creating a simulation to avoid invoking DPG UI components.
    magic_sim = mocker.MagicMock()
    primary_window_mock = mocker.PropertyMock()
    type(magic_sim).primary_window = primary_window_mock
    app._build_simulation = mocker.MagicMock(return_value = magic_sim)

    # Setup the data required to load a project.
    demo_dir: str = os.path.join(Path.cwd(), 'demo')
    project_name = 'pulsing_circle'
    project_path = os.path.join(demo_dir, project_name)
    app_data = {
      'file_path_name': project_path, 
      'selections': {'pulsing_circle': project_path}}
    
    # Load the sim
    app._handle_sim_selected(None, app_data)

    assert app.active_simulation is not None

    primary_window_mock.assert_called_once()
    magic_sim.attach.assert_called_once()
    magic_sim.launch.assert_called_once()

  def test_app_can_reload_sim_project(self, mocker: MockerFixture):
    app = PlaygroundApp()

    # Mock creating a simulation to avoid invoking DPG UI components.
    magic_sim = mocker.MagicMock()
    primary_window_mock = mocker.PropertyMock()
    type(magic_sim).primary_window = primary_window_mock
    app._build_simulation = mocker.MagicMock(return_value = magic_sim)

    # Setup the data required to load a project.
    demo_dir: str = os.path.join(Path.cwd(), 'demo')
    project_name = 'pulsing_circle'
    project_path = os.path.join(demo_dir, project_name)
    app_data = {
      'file_path_name': project_path, 
      'selections': {'pulsing_circle': project_path}}
    
    # Load the sim
    app._handle_sim_selected(None, app_data)
    
    # Reload the Sim
    app._handle_sim_selected(None, app_data)

    assert app.active_simulation is not None
    assert primary_window_mock.call_count == 2
    assert magic_sim.attach.call_count == 2
    assert magic_sim.launch.call_count == 2