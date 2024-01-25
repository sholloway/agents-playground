from pytest_mock import MockFixture

from types import SimpleNamespace

from agents_playground.core.sim_loop import SimLoop
from agents_playground.core.waiter import Waiter
from agents_playground.legacy.scene.scene import Scene
from agents_playground.simulation.context import SimulationContext
from agents_playground.simulation.sim_state import SimulationState

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

  def test_process_sim_cycle(self, mocker: MockFixture) -> None:
    scheduler = SimpleNamespace(queue_holding_tasks=mocker.Mock(), consume=mocker.Mock())
    context = mocker.Mock()
    
    mock_waiter = Waiter()
    mock_waiter.wait_until_deadline = mocker.Mock()

    looper = SimLoop(scheduler, waiter=mock_waiter)
    looper._update_render = mocker.Mock()
    looper._process_sim_cycle(context)

    scheduler.queue_holding_tasks.assert_called_once()
    scheduler.consume.assert_called_once()

    mock_waiter.wait_until_deadline.assert_called_once()
    looper._update_render.assert_called_once()


  def test_update_renderer(self, mocker: MockFixture) -> None:
    looper = SimLoop()
    scene = Scene()
    scene.add_entity('fake_entity', SimpleNamespace(toml_id=1, update=mocker.Mock()))
    scene.add_entity('fake_entity', SimpleNamespace(toml_id=2, update=mocker.Mock()))
    scene.add_entity('fake_entity', SimpleNamespace(toml_id=3, update=mocker.Mock()))
    
    looper._update_render(scene)

    for _, entity_grouping in scene.entities.items():
      for _, entity in entity_grouping.items():
        entity.update.assert_called_once()