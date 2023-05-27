from types import SimpleNamespace

import pytest
from pytest_mock import MockerFixture

from agents_playground.agents.default.default_agent_system import DefaultAgentSystem

from agents_playground.agents.spec.agent_system import (
  ByproductDefinition,
  ByproductRegistrationError, 
  ByproductStore,
  SystemRegistrationError
)

class FakeByproduct:
  ...

class TestByproductStore:
  def test_register_for_unique_byproduct(self, mocker: MockerFixture) -> None:
    byproducts = ByproductStore()
    byproducts_to_register = [
      ByproductDefinition('a', int),
      ByproductDefinition('b', float),
      ByproductDefinition('c', FakeByproduct)
    ]
    system = mocker.stub()
    subsystem = mocker.stub()
    byproducts.register(system, subsystem, byproducts_to_register)
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
    subsystem = mocker.stub()
    byproducts.register(system, subsystem, byproducts_to_register)
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
    subsystem = DefaultAgentSystem('the-subsystem')

    with pytest.raises(ByproductRegistrationError):
      byproducts.register(system, subsystem, byproducts_to_register)

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
    subsystem_b = DefaultAgentSystem('subsystem_b')
    subsystem_c = DefaultAgentSystem('subsystem_c')
    
    root_system.register_system(subsystem_a)
    root_system.register_system(subsystem_b, [
      ByproductDefinition('a', int),
      ByproductDefinition('b', float)
    ])
    root_system.register_system(subsystem_c, [
      ByproductDefinition('a', int),
      ByproductDefinition('b', float),
      ByproductDefinition('c', FakeByproduct)
    ])

    assert len(root_system.byproducts_store.byproducts) == 3

  def test_duplicate_subsystems_not_allowed(self) -> None:
    root_system       = DefaultAgentSystem('root-system')
    subsystem_a       = DefaultAgentSystem('subsystem_a')
    subsystem_a_prime = DefaultAgentSystem('subsystem_a') # Same name

    root_system.register_system(subsystem_a)
    with pytest.raises(SystemRegistrationError):
      root_system.register_system(subsystem_a_prime)
