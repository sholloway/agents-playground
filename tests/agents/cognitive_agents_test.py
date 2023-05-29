
import pytest
from pytest_mock import MockerFixture

from agents_playground.agents.default.default_agent import DefaultAgent
from agents_playground.agents.default.default_agent_memory import DefaultAgentMemory
from agents_playground.agents.default.default_agent_state import DefaultAgentState
from agents_playground.agents.default.default_agent_system import DefaultAgentSystem
from agents_playground.agents.default.named_agent_state import NamedAgentActionState
from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.agents.systems.agent_nervous_system import AgentNervousSystem
from agents_playground.agents.systems.agent_perception_system import AgentPerceptionSystem

"""
Test an agent's ability to have cognition (i.e. mental capacity).
"""

@pytest.fixture
def nervous_agent(mocker: MockerFixture) -> AgentLike:
  """
  Create an agent that has a nervous system wired up.
  """
  root_system = DefaultAgentSystem(name = 'root-system')
  root_system.register_system(AgentNervousSystem())
  return DefaultAgent(
    initial_state = mocker.Mock(),
    style = mocker.Mock(),
    identity=mocker.Mock(),
    physicality=mocker.Mock(),
    position=mocker.Mock(),
    movement         = mocker.Mock(),
    agent_memory     = DefaultAgentMemory(),
    internal_systems = root_system
  )

@pytest.fixture
def perceptive_agent(nervous_agent: AgentLike) -> AgentLike:
  nervous_agent.internal_systems.register_system(AgentPerceptionSystem())
  return nervous_agent

class TestAgentPerception:
  def test_agent_sees_something(self, mocker: MockerFixture, perceptive_agent: AgentLike) -> None:
    assert True
  
  def test_agent_hears_something(self, mocker: MockerFixture, perceptive_agent: AgentLike) -> None:
    assert True
  
  def test_agent_touches_something(self, mocker: MockerFixture, perceptive_agent: AgentLike) -> None:
    assert True
  
  def test_agent_smells_something(self, mocker: MockerFixture, perceptive_agent: AgentLike) -> None:
    assert True
  
  def test_agent_tastes_something(self, mocker: MockerFixture, perceptive_agent: AgentLike) -> None:
    assert True
  
  def test_agent_vestibular(self, mocker: MockerFixture, perceptive_agent: AgentLike) -> None:
    assert True



class TestAgentAttention:
  ...


  