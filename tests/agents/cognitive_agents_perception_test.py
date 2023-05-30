
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
    # Confirm that the visual system is in place.
    assert perceptive_agent.internal_systems.subsystems.agent_nervous_system.subsystems.visual_system is not None
    
    # Setup something for the agent to see.

    # Process the agent's systems.
    perceptive_agent.transition_state()

    # Confirm the agent saw something.
    # Bug: What's happening is that the stimuli of the nervous system is not
    # getting moved up the root system before perception system is running.
    # so it's never getting added to the sensory memory. 
    # 
    # Rather than have the collect byproducts phase, each time a subsystem is ran
    # it needs to push its byproducts up if it hasn't already. The act of push 
    # them up should clear them out.
    assert len(perceptive_agent.memory.sensory_memory.memory_store) == 1

  
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
  