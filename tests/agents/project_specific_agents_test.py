from pytest_mock import MockerFixture

from agents_playground.agents.agent_spec import AgentActionStateLike
from agents_playground.agents.default_agent import (
  DefaultAgent,
  DefaultAgentState, 
  MapAgentActionSelector, 
  NamedAgentState
)

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

    assert not agent.selected
    agent.handle_agent_selected.assert_not_called()
    
    agent.select()
    
    assert agent.selected
    agent.handle_agent_selected.assert_called_once()