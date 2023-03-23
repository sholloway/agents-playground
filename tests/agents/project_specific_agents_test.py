from types import SimpleNamespace
from pytest_mock import MockerFixture

from agents_playground.agents.agent_spec import AgentActionStateLike
from agents_playground.agents.default_agent import (
  DefaultAgent,
  DefaultAgentState,
  DefaultAgentSystem, 
  MapAgentActionSelector, 
  NamedAgentState
)
from agents_playground.core.types import Coordinate, Size

class TestProjectSpecificAgents:
  def test_agent_selection(self, mocker: MockerFixture) -> None:
    agent = DefaultAgent(
      initial_state = DefaultAgentState(
        initial_state = NamedAgentState('IDLE'),
        action_selector = MapAgentActionSelector(state_map = {}),
        agent_is_selected = False,
      ),
      style            = mocker.Mock(),
      identity         = mocker.Mock(),
      physicality      = mocker.Mock(),
      position         = mocker.Mock(),
      movement         = mocker.Mock(),
      internal_systems = mocker.Mock()
    )

    agent.handle_agent_selected = mocker.Mock()
    agent.handle_agent_deselected = mocker.Mock()

    assert not agent.selected
    agent.handle_agent_selected.assert_not_called()
    
    agent.select()
    
    assert agent.selected
    agent.handle_agent_selected.assert_called_once()

    agent.deselect()
    agent.handle_agent_deselected.assert_called_once()

  def test_moving_the_agent(self, mocker: MockerFixture) -> None:
    agent = DefaultAgent(
      initial_state = DefaultAgentState(
        initial_state = NamedAgentState('IDLE'),
        action_selector = MapAgentActionSelector(state_map = {}),
        agent_is_selected = False,
      ),
      style            = mocker.Mock(),
      identity         = mocker.Mock(),
      physicality      = mocker.Mock(),
      position         = mocker.Mock(),
      movement         = mocker.Mock(),
      internal_systems = mocker.Mock()
    )

    assert not agent.agent_scene_graph_changed
    agent.position.move_to.assert_not_called()
    agent.physicality.calculate_aabb.assert_not_called()

    agent.move_to(new_location = Coordinate(14, 22), cell_size = Size(10, 10))

    assert agent.agent_scene_graph_changed
    agent.position.move_to.assert_called_once()
    agent.physicality.calculate_aabb.assert_called_once()

  def test_changing_to_next_state(self, mocker: MockerFixture) -> None:
    root_system = DefaultAgentSystem(name = 'root_system',  subsystems = SimpleNamespace())
    root_system.before_subsystems_processed = mocker.Mock()
    root_system.after_subsystems_processed = mocker.Mock()

    agent = DefaultAgent(
      initial_state = DefaultAgentState(
        initial_state = NamedAgentState('IDLE'),
        action_selector = MapAgentActionSelector(state_map = {}),
        agent_is_selected = False,
      ),
      style            = mocker.Mock(),
      identity         = mocker.Mock(),
      physicality      = mocker.Mock(),
      position         = mocker.Mock(),
      movement         = mocker.Mock(),
      internal_systems = mocker.Mock()
    )

    # TODO: Finish this test.
    # Verify the before/after methods on the root_system are invoked when calling
    # agent.transition_state. Need to verify the entire life cycle of transition state.
    # Verify the AgentLifeCyclePhase is being passed in correctly.
    assert False
  