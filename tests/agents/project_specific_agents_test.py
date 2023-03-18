from pytest_mock import MockerFixture

from agents_playground.agents.agent_spec import AgentActionStateLike
from agents_playground.agents.default_agent import (
  DefaultAgent,
  DefaultAgentState, 
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
      style         = mocker.Mock(),
      identity      = mocker.Mock(),
      physicality   = mocker.Mock(),
      position      = mocker.Mock(),
      movement      = mocker.Mock()
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
      style         = mocker.Mock(),
      identity      = mocker.Mock(),
      physicality   = mocker.Mock(),
      position      = mocker.Mock(),
      movement      = mocker.Mock()
    )

    assert not agent.agent_scene_graph_changed
    agent.position.move_to.assert_not_called()
    agent.physicality.calculate_aabb.assert_not_called()

    agent.move_to(new_location = Coordinate(14, 22), cell_size = Size(10, 10))

    assert agent.agent_scene_graph_changed
    agent.position.move_to.assert_called_once()
    agent.physicality.calculate_aabb.assert_called_once()