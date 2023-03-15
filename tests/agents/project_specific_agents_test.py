from pytest_mock import MockerFixture

from agents_playground.agents.agent_like import (
  AgentAspect,
  AgentActionStateLike,
  AgentStateLike,
  AgentAspects,
  AgentLike
)

class MyProjectAgent(AgentLike):
  def __init__(self) -> None:
    super().__init__()

class TestProjectSpecificAgents:
  def test_initialize_an_agent(self, mocker: MockerFixture) -> None:
    agent = MyProjectAgent()