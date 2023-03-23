
from types import SimpleNamespace

from pytest_mock import MockFixture
from agents_playground.agents.agent_spec import AgentLifeCyclePhase
from agents_playground.agents.default_agent import DefaultAgentSystem

class TestAgentInternalSystems:
  def test_systems_have_names(self) -> None:
    system_name = 'a_system'
    agent_system = DefaultAgentSystem(
      name = system_name, 
      subsystems = SimpleNamespace()
    )
    assert agent_system.name == system_name

  def test_processing_subsystems(self, mocker: MockFixture) -> None:
    root_system = DefaultAgentSystem(name = 'root_system',  subsystems = SimpleNamespace())
    root_system.before_subsystems_processed = mocker.Mock()
    root_system.after_subsystems_processed = mocker.Mock()

    sub_system_a = DefaultAgentSystem(name='sub_system_a',  subsystems = SimpleNamespace())
    sub_system_b = DefaultAgentSystem(name='sub_system_b',  subsystems = SimpleNamespace())
    root_system.register_system(sub_system_a)
    root_system.register_system(sub_system_b)

    root_system.process(agent = mocker.Mock(), agent_phase=AgentLifeCyclePhase.PRE_STATE_CHANGE)
    root_system.before_subsystems_processed.assert_called_once
    root_system.after_subsystems_processed.assert_called_once