from types import SimpleNamespace

import pytest
from pytest_mock import MockerFixture

from agents_playground.agents.default.default_agent_system import DefaultAgentSystem

from agents_playground.agents.spec.agent_system import (
  ByproductDefinition,
  ByproductRegistrationError, 
  ByproductStore
)

class FakeByproduct:
  ...

class TestByproductStore:
  def test_register_for_unique_byproduct(self, mocker: MockerFixture) -> None:
    byproducts = ByproductStore()
    byproducts_to_register = [
      ByproductDefinition('a', int),
      ByproductDefinition('b', float),
      ByproductDefinition('c', FakeByproduct),
    ]
    system = mocker.stub()
    subsystem = mocker.stub()
    byproducts.register(system, subsystem, byproducts_to_register)
    assert len(byproducts._byproducts) == 3
    assert len(byproducts._registered_byproducts) == 3

  def test_duplicate_byproducts_not_allowed(self, mocker: MockerFixture) -> None:
    byproducts = ByproductStore()
    byproducts_to_register = [
      ByproductDefinition('a', int),
      ByproductDefinition('b', float),
      ByproductDefinition('a', FakeByproduct),
    ]
    system = DefaultAgentSystem('the-system', SimpleNamespace())
    subsystem = DefaultAgentSystem('the-subsystem', SimpleNamespace())

    with pytest.raises(ByproductRegistrationError):
      byproducts.register(system, subsystem, byproducts_to_register)