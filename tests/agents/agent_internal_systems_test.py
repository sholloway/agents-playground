
from types import SimpleNamespace

from pytest_mock import MockFixture

from agents_playground.agents.default.default_agent_system import DefaultAgentSystem
from agents_playground.agents.spec.agent_life_cycle_phase import AgentLifeCyclePhase

class TestAgentInternalSystems:
  def test_systems_have_names(self) -> None:
    system_name = 'a_system'
    agent_system = DefaultAgentSystem(name = system_name)
    assert agent_system.name == system_name

  def test_processing_subsystems(self, mocker: MockFixture) -> None:
    root_system = DefaultAgentSystem(name = 'root_system')
    root_system._before_subsystems_processed = mocker.Mock()
    root_system._after_subsystems_processed = mocker.Mock()

    sub_system_a = DefaultAgentSystem(name='sub_system_a')
    sub_system_b = DefaultAgentSystem(name='sub_system_b')
    root_system.register_system(sub_system_a)
    root_system.register_system(sub_system_b)

    root_system.process(characteristics = mocker.Mock(), agent_phase=AgentLifeCyclePhase.PRE_STATE_CHANGE, other_agents=[])
    root_system._before_subsystems_processed.assert_called_once()
    root_system._after_subsystems_processed.assert_called_once()