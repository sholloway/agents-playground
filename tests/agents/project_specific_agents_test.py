from pytest_mock import MockerFixture
from agents_playground.agents.agent_spec import AgentActionStateLike

from agents_playground.agents.default_agent import DefaultAgentState, DefaultIdleAgentState, MapAgentActionSelector


class TestProjectSpecificAgents:
  def test_agent_state(self, mocker: MockerFixture) -> None:

    idle_state: AgentActionStateLike = DefaultIdleAgentState()
    state_map = {
      idle_state: idle_state
    } 

    agent_state = DefaultAgentState(
      initial_state = DefaultIdleAgentState(), 
      action_selector = MapAgentActionSelector(state_map=state_map)
    )

  def test_initialize_an_agent(self, mocker: MockerFixture) -> None:
    pass