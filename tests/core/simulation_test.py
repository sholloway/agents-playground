from cgi import test
from http.client import NotConnected
from types import SimpleNamespace
from pytest_mock import MockFixture
import dearpygui.dearpygui as dpg
from agents_playground.core.callable_utils import CallableUtility

from agents_playground.core.simulation import Simulation, SimulationDefaults
from agents_playground.scene.scene_builder import SceneBuilder
from agents_playground.scene.scene_reader import SceneReader
from agents_playground.simulation.sim_events import SimulationEvents
from agents_playground.simulation.sim_state import SimulationState

class FakeSimulation(Simulation):
  def __init__(self, scene_reader = SceneReader()) -> None:
    super().__init__('fake_file', scene_reader)

class FakeSceneReader(SceneReader):
  def __init__(self):
    super().__init__()
      
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


  def test_default_layers_initialized(self, mocker: MockFixture) -> None:
    fake = FakeSimulation()
    assert len(fake._layers) == 5
    layer_labels = map(lambda rl: rl.label, fake._layers.values())
    assert 'Statistics' in layer_labels
    assert 'Terrain' in layer_labels
    assert 'Entities' in layer_labels
    assert 'Path' in layer_labels
    assert 'Agents' in layer_labels

  def test_add_layer(self, mocker: MockFixture) -> None:
    fake = FakeSimulation()
    fake.add_layer(lambda i: i, "Fake Layer")
    assert len(fake._layers) == 6
    layer_labels = map(lambda rl: rl.label, fake._layers.values())
    assert 'Fake Layer' in layer_labels

  def test_load_scene_on_launch(self, mocker: MockFixture) -> None:
    # Need to mock dpg methods
    mocker.patch('dearpygui.dearpygui.get_item_width')
    mocker.patch('dearpygui.dearpygui.get_item_height')
    mocker.patch('dearpygui.dearpygui.window')
    mocker.patch('dearpygui.dearpygui.menu_bar')
    mocker.patch('dearpygui.dearpygui.add_button')
    mocker.patch('dearpygui.dearpygui.menu')
    mocker.patch('dearpygui.dearpygui.add_menu_item')
    mocker.patch('dearpygui.dearpygui.drawlist')
    mocker.patch('dearpygui.dearpygui.draw_text')

    fake = FakeSimulation()
    fake._load_scene = mocker.Mock()
    fake.primary_window = dpg.generate_uuid()
    fake.launch()
    fake._load_scene.assert_called_once()

  def test_initial_render_when_initializing(self, mocker: MockFixture) -> None:
    mocker.patch('dearpygui.dearpygui.get_item_width')
    mocker.patch('dearpygui.dearpygui.get_item_height')
    mocker.patch('dearpygui.dearpygui.window')
    mocker.patch('dearpygui.dearpygui.menu_bar')
    mocker.patch('dearpygui.dearpygui.add_button')
    mocker.patch('dearpygui.dearpygui.menu')
    mocker.patch('dearpygui.dearpygui.add_menu_item')

    fake = FakeSimulation()
    fake._load_scene = mocker.Mock()
    fake._initial_render = mocker.Mock()
    fake.primary_window = dpg.generate_uuid()
    fake.launch()
    fake._load_scene.assert_called_once()
    fake._initial_render.assert_called_once()

  def test_start_sim_when_not_initializing(self, mocker: MockFixture) -> None:
    mocker.patch('dearpygui.dearpygui.get_item_width')
    mocker.patch('dearpygui.dearpygui.get_item_height')
    mocker.patch('dearpygui.dearpygui.window')
    mocker.patch('dearpygui.dearpygui.menu_bar')
    mocker.patch('dearpygui.dearpygui.add_button')
    mocker.patch('dearpygui.dearpygui.menu')
    mocker.patch('dearpygui.dearpygui.add_menu_item')

    fake = FakeSimulation()
    fake._load_scene = mocker.Mock()
    fake._start_simulation = mocker.Mock()
    fake.primary_window = dpg.generate_uuid()
    fake.simulation_state = SimulationState.RUNNING
    fake.launch()
    fake._load_scene.assert_called_once()
    fake._start_simulation.assert_called_once()

  def test_load_scene(self, mocker: MockFixture) -> None:
    mocker.patch('os.path.abspath')
    fake_sr = FakeSceneReader()
    fake_sr.load = mocker.Mock()
    fake = FakeSimulation(scene_reader=fake_sr)
    fake_scene_builder = SimpleNamespace(build=mocker.Mock())
    fake._init_scene_builder = mocker.Mock(return_value=fake_scene_builder)

    fake._load_scene()

    fake_sr.load.assert_called_once()
    fake._init_scene_builder.assert_called_once()
    fake_scene_builder.build.assert_called_once()

  def test_initializing_the_scene_builder(self, mocker: MockFixture) -> None:
    fake = FakeSimulation()
    scene_builder = fake._init_scene_builder()
    assert isinstance(scene_builder, SceneBuilder)

  def test_starting_the_sim(self, mocker: MockFixture) -> None:
    fake = FakeSimulation()
    fake._establish_context =  mocker.Mock()
    fake._initialize_layers =  mocker.Mock()
    fake._sim_loop.start =  mocker.Mock()

    fake._start_simulation()

    fake._establish_context.assert_called_once()
    fake._initialize_layers.assert_called_once()
    fake._sim_loop.start.assert_called_once()

  def test_establish_sim_context(self, mocker: MockFixture) -> None:
    mocker.patch('dearpygui.dearpygui.get_item_width', return_value = 1)
    mocker.patch('dearpygui.dearpygui.get_item_height', return_value = 2)
    fake = FakeSimulation()
    fake.primary_window = dpg.generate_uuid()

    fake._establish_context()

    assert fake._context.parent_window.width == 1
    assert fake._context.parent_window.height == 2
    assert fake._context.canvas.width == 1
    assert fake._context.canvas.height == fake._context.parent_window.height - SimulationDefaults.CANVAS_HEIGHT_BUFFER
    assert fake._context.agent_style.stroke_thickness == SimulationDefaults.AGENT_STYLE_STROKE_THICKNESS
    assert fake._context.agent_style.stroke_color == SimulationDefaults.AGENT_STYLE_STROKE_COLOR
    assert fake._context.agent_style.fill_color == SimulationDefaults.AGENT_STYLE_FILL_COLOR
    assert fake._context.agent_style.size.width == SimulationDefaults.AGENT_STYLE_SIZE_WIDTH
    assert fake._context.agent_style.size.height == SimulationDefaults.AGENT_STYLE_SIZE_HEIGHT

  def test_initialize_layers(self, mocker: MockFixture) -> None:
    mocker.patch('dearpygui.dearpygui.drawlist')
    mocker.patch('dearpygui.dearpygui.draw_layer')
    mocker.patch('agents_playground.core.callable_utils.CallableUtility.invoke')
    fake = FakeSimulation()

    fake._initialize_layers()

    dpg.drawlist.assert_called_once()
    
    # These functions are both called once for each layer initialized in the constructor.
    num_layers = len(fake._layers)
    assert dpg.draw_layer.call_count == num_layers
    assert CallableUtility.invoke.call_count == num_layers

  def test_updating_ui_default_call(self, mocker: MockFixture) -> None:
    mocker.patch('dearpygui.dearpygui.set_item_label')
    mocker.patch('dearpygui.dearpygui.does_item_exist', return_value = False)
    mocker.patch('dearpygui.dearpygui.delete_item')
    fake = FakeSimulation()
    fake._start_simulation = mocker.Mock()

    fake_sender = None
    fake_label = "Fake Label"
    fake._update_ui(fake_sender, fake_label)

    dpg.set_item_label.assert_called_once_with(fake_sender, fake_label)
    fake._start_simulation.assert_called_once()
    dpg.does_item_exist.assert_called_once()
    dpg.delete_item.assert_not_called()

  def test_updating_ui_on_later_calls(self, mocker: MockFixture) -> None:
    mocker.patch('dearpygui.dearpygui.set_item_label')
    mocker.patch('dearpygui.dearpygui.does_item_exist', return_value = True)
    mocker.patch('dearpygui.dearpygui.delete_item')
    fake = FakeSimulation()
    fake._start_simulation = mocker.Mock()

    fake_sender = None
    fake_label = "Fake Label"
    fake._update_ui(fake_sender, fake_label)

    dpg.set_item_label.assert_called_once_with(fake_sender, fake_label)
    fake._start_simulation.assert_called_once()
    dpg.does_item_exist.assert_called_once()
    dpg.delete_item.assert_called_once()

  def test_toggling_on_layer(self, mocker: MockFixture) -> None:
    mocker.patch('dearpygui.dearpygui.show_item')
    mocker.patch('dearpygui.dearpygui.hide_item')
    fake = FakeSimulation()
    menu_item = NotConnected
    show_item = True
    layer_id = "fake layer id"

    fake._toggle_layer(menu_item, show_item, layer_id)

    dpg.show_item.called_once_with(layer_id)
    dpg.hide_item.assert_not_called()
  
  def test_toggling_off_layer(self, mocker: MockFixture) -> None:
    mocker.patch('dearpygui.dearpygui.show_item')
    mocker.patch('dearpygui.dearpygui.hide_item')
    fake = FakeSimulation()
    menu_item = NotConnected
    show_item = False
    layer_id = "fake layer id"

    fake._toggle_layer(menu_item, show_item, layer_id)

    dpg.show_item.assert_not_called()
    dpg.hide_item.called_once_with(layer_id)

