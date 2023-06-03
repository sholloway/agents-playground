import pytest
from pytest_mock import MockerFixture
from agents_playground.agents.default.default_agent_system import DefaultAgentSystem, SystemWithByproducts
from agents_playground.agents.spec.byproduct_definition import ByproductDefinition
from agents_playground.agents.spec.byproduct_store import ByproductRegistrationError, ByproductStore


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
    subsystem = SystemWithByproducts('subsystem', byproducts_to_register)
    byproducts.register_subsystem_byproducts("root-system", subsystem.name, subsystem.byproducts_definitions)
    assert len(byproducts._byproducts) == 3
    assert len(byproducts._registered_byproducts) == 3

  def test_duplicate_byproducts_of_same_type(self, mocker: MockerFixture) -> None:
    byproducts = ByproductStore()
    byproducts_to_register = [
      ByproductDefinition('a', int),
      ByproductDefinition('b', float),
      ByproductDefinition('a', int)
    ]
    subsystem = SystemWithByproducts('subsystem', byproducts_to_register)
    byproducts.register_subsystem_byproducts("root-system", subsystem.name, subsystem.byproducts_definitions)
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