from types import SimpleNamespace
from typing import List

import pytest
from pytest_mock import MockerFixture

from agents_playground.agents.default.default_agent_system import DefaultAgentSystem
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_life_cycle_phase import AgentLifeCyclePhase

from agents_playground.agents.spec.agent_system import (
  AgentSystem,
  ByproductDefinition,
  ByproductRegistrationError, 
  ByproductStore,
  SystemRegistrationError
)

class FakeByproduct:
  ...

class SystemWithByproducts(AgentSystem):
  def __init__(
    self, name:str, 
    byproduct_defs: List[ByproductDefinition] = [],
    internal_byproduct_defs: List[ByproductDefinition] = []
  ) -> None:
    super().__init__(
      system_name = name, 
      subsystems = SimpleNamespace(), 
      byproducts_store = ByproductStore(),
      byproducts_definitions = byproduct_defs,
      internal_byproducts_definitions = internal_byproduct_defs
    )

class IntegerSystem(SystemWithByproducts):
  """Products a static integer on every tick."""
  def __init__(self, name: str, value: int) -> None:
    super().__init__(name, [ByproductDefinition('integers', int)])
    self.value = value
  
  def before_subsystems_processed(
    self, 
    characteristics: AgentCharacteristics, 
    agent_phase: AgentLifeCyclePhase
  ) -> None:
    self.byproducts_store.store(self, 'integers', self.value)
  

class TestByproductStore:
  def test_register_for_unique_byproduct(self, mocker: MockerFixture) -> None:
    byproducts = ByproductStore()
    byproducts_to_register = [
      ByproductDefinition('a', int),
      ByproductDefinition('b', float),
      ByproductDefinition('c', FakeByproduct)
    ]
    system = mocker.stub()
    subsystem = SystemWithByproducts('subsystem', byproducts_to_register)
    byproducts.register_subsystem_byproducts(system, subsystem)
    assert len(byproducts._byproducts) == 3
    assert len(byproducts._registered_byproducts) == 3

  def test_duplicate_byproducts_of_same_type(self, mocker: MockerFixture) -> None:
    byproducts = ByproductStore()
    byproducts_to_register = [
      ByproductDefinition('a', int),
      ByproductDefinition('b', float),
      ByproductDefinition('a', int)
    ]
    system = mocker.stub()
    subsystem = SystemWithByproducts('subsystem', byproducts_to_register)
    byproducts.register_subsystem_byproducts(system, subsystem)
    assert len(byproducts._byproducts) == 2
    assert len(byproducts._registered_byproducts) == 2

  def test_duplicate_byproducts_of_different_types_not_allowed(self) -> None:
    byproducts = ByproductStore()
    byproducts_to_register = [
      ByproductDefinition('a', int),
      ByproductDefinition('b', float),
      ByproductDefinition('a', FakeByproduct)
    ]
    system = DefaultAgentSystem('the-system')

    with pytest.raises(ByproductRegistrationError):
      subsystem = SystemWithByproducts('the-subsystem', byproducts_to_register)

def create_mock_system(sys_name:str, mocker: MockerFixture) -> AgentSystem:
  system = DefaultAgentSystem(sys_name)
  system.before_subsystems_processed = mocker.Mock()
  system.after_subsystems_processed = mocker.Mock()
  system.collect_byproducts = mocker.Mock()
  return system

class TestAgentSystem:
  def test_registering_subsystems(self, mocker: MockerFixture) -> None:
    root_system = DefaultAgentSystem('root-system')
    subsystem_a = DefaultAgentSystem('subsystem_a')
    subsystem_b = DefaultAgentSystem('subsystem_b')
    subsystem_c = DefaultAgentSystem('subsystem_c')
    root_system.register_system(subsystem_a)
    root_system.register_system(subsystem_b)
    root_system.register_system(subsystem_c)

    assert len(root_system.byproducts_store.byproducts) == 0
  
  def test_registering_subsystems_with_byproducts(self, mocker: MockerFixture) -> None:
    root_system = DefaultAgentSystem('root-system')
    subsystem_a = DefaultAgentSystem('subsystem_a')
    subsystem_b = SystemWithByproducts('subsystem_b', [
      ByproductDefinition('a', int),
      ByproductDefinition('b', float)
    ])
    subsystem_c = SystemWithByproducts('subsystem_c', [
      ByproductDefinition('a', int),
      ByproductDefinition('b', float),
      ByproductDefinition('c', FakeByproduct)
    ])
    
    root_system.register_system(subsystem_a)
    root_system.register_system(subsystem_b)
    root_system.register_system(subsystem_c)

    assert len(root_system.byproducts_store.byproducts) == 3

  def test_duplicate_subsystems_not_allowed(self) -> None:
    root_system       = DefaultAgentSystem('root-system')
    subsystem_a       = DefaultAgentSystem('subsystem_a')
    subsystem_a_prime = DefaultAgentSystem('subsystem_a') # Same name

    root_system.register_system(subsystem_a)
    with pytest.raises(SystemRegistrationError):
      root_system.register_system(subsystem_a_prime)

  def test_system_orchestration(self, mocker: MockerFixture) -> None:
    root_system = create_mock_system('root-system', mocker)
    root_system.process(mocker.Mock(), AgentLifeCyclePhase.PRE_STATE_CHANGE)
    root_system.before_subsystems_processed.assert_called_once() 
    root_system.after_subsystems_processed.assert_called_once() 
    root_system.collect_byproducts.assert_called_once()

  def test_hierarchical_system_processing(self, mocker: MockerFixture) -> None:
    """
    Test a hierarchy of systems.
    Root
      - subsystem_a
      - subsystem_b
        - subsystem_d
        - subsystem_e
      - subsystem_c
        - subsystem_f
          - subsystem_g
    """
    root_system = create_mock_system('root-system', mocker)
    subsystem_a = create_mock_system('subsystem_a', mocker)
    subsystem_b = create_mock_system('subsystem_b', mocker)
    subsystem_c = create_mock_system('subsystem_c', mocker)
    subsystem_d = create_mock_system('subsystem_d', mocker)
    subsystem_e = create_mock_system('subsystem_e', mocker)
    subsystem_f = create_mock_system('subsystem_f', mocker)
    subsystem_g = create_mock_system('subsystem_g', mocker)
    
    root_system.register_system(subsystem_a)
    root_system.register_system(subsystem_b)
    root_system.register_system(subsystem_c)

    subsystem_b.register_system(subsystem_d)
    subsystem_b.register_system(subsystem_e)

    subsystem_c.register_system(subsystem_f)
    subsystem_f.register_system(subsystem_g)

    root_system.process(mocker.Mock(), AgentLifeCyclePhase.PRE_STATE_CHANGE)

    subsystem_g.before_subsystems_processed.assert_called_once() 
    subsystem_g.after_subsystems_processed.assert_called_once() 

  def test_collect_byproducts(self, mocker: MockerFixture) -> None:
    """
    Given the Hierarchy. 
    Root
      - subsystem_a (1)
      - subsystem_b (2)
        - subsystem_d (4)
        - subsystem_e (5)
      - subsystem_c (3)
        - subsystem_f (6)
          - subsystem_g (7)

    The the order of execution should be depth first.
    1, 2, 4, 5, 3, 6, 7
    """
    root_system = DefaultAgentSystem('root-system')
    subsystem_a = IntegerSystem('subsystem_a', 1)
    subsystem_b = IntegerSystem('subsystem_b', 2)
    subsystem_c = IntegerSystem('subsystem_c', 3)
    subsystem_d = IntegerSystem('subsystem_d', 4)
    subsystem_e = IntegerSystem('subsystem_e', 5)
    subsystem_f = IntegerSystem('subsystem_f', 6)
    subsystem_g = IntegerSystem('subsystem_g', 7)

    root_system.register_system(subsystem_a)
    root_system.register_system(subsystem_b)
    root_system.register_system(subsystem_c)

    subsystem_b.register_system(subsystem_d)
    subsystem_b.register_system(subsystem_e)

    subsystem_c.register_system(subsystem_f)
    subsystem_f.register_system(subsystem_g)

    root_system.process(mocker.Mock(), AgentLifeCyclePhase.PRE_STATE_CHANGE)

    byproducts = root_system.byproducts_store.byproducts['integers']
    assert len(byproducts) == 7
    assert byproducts == [1, 2, 4, 5, 3, 6, 7]