
from typing import Any, List
from more_itertools import consume
from agents_playground.agents.spec.byproduct_definition import ByproductDefinition

class ByproductRegistrationError(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

class ByproductStorageError(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

class ByproductStore:
  """
  Responsible for storing the outputs of systems.
  """
  def __init__(self) -> None:
    self._byproducts: dict[str, list] = {}
    self._registered_byproducts: dict[str, ByproductDefinition] = {}

  @property
  def byproducts(self) -> dict[str, list]:
    return self._byproducts

  def register_system_byproducts(self, system_name: str, byproduct_defs: List[ByproductDefinition]) -> None:
    """
    Registers byproducts that can be collected.

    Args:
      - system_name: The name of the system to register byproducts for.
      - byproduct_defs: A list of system byproducts to register.
    """
    byproduct_def: ByproductDefinition
    for byproduct_def in byproduct_defs:
      if not byproduct_def.name in self.byproducts:
        self._byproducts[byproduct_def.name] = []
        self._registered_byproducts[byproduct_def.name] = byproduct_def
      elif (byproduct_def.name in self._registered_byproducts) and \
        (self._registered_byproducts[byproduct_def.name].type != byproduct_def.type):
        error_msg = f"""
        Error registering system byproduct.
        The system {system_name} attempted to register the byproduct {byproduct_def.name} for it's internal
        byproduct store. However the byproduct was already registered there with a different type.
        """
        raise ByproductRegistrationError(error_msg)

  def register_subsystem_byproducts(
    self, 
    system_name: str,
    subsystem_name: str,
    subsystem_byproducts: List[ByproductDefinition]
  ) -> None:
    """
    Registers byproducts that can be collected.

    Args:
      - system_name: The name of the system that the subsystem is being added to.
      - subsystem_name: The name of the subsystem that can produce the byproducts.
      - possible_byproducts: The list of byproducts that the subsystem may produce.
    """
    byproduct_def: ByproductDefinition
    for byproduct_def in subsystem_byproducts:
      if not byproduct_def.name in self._byproducts:
        self._byproducts[byproduct_def.name] = []
        self._registered_byproducts[byproduct_def.name] = byproduct_def
      elif (byproduct_def.name in self._registered_byproducts) and \
        (self._registered_byproducts[byproduct_def.name].type != byproduct_def.type):
        error_msg = f"""
        Error registering subsystem byproducts.
        The system {system_name} attempted to registers subsystem {subsystem_name} with byproduct {byproduct_def.name} of type {byproduct_def.type}.
        However, byproduct {byproduct_def.name} is already registered with type {self._registered_byproducts[byproduct_def.name].type}.
        Byproducts may not have multiple types.
        """
        raise ByproductRegistrationError(error_msg)
      
  def store(self, system_name: str, byproduct_name: str, value: Any) -> None:
    """
    Record a byproduct produced by a system.

    Args:
      - subsystem_name: The name of the subsystem that produced the byproduct.
      - byproduct_name: The name of the byproduct to record.
      - value: The byproduct output.
    """
    if byproduct_name in self.byproducts:
      self.byproducts[byproduct_name].append(value)
    else:
      error_msg=f"""
      Byproduct Storage Error
      The system {system_name} attempted to store the value {value} byproduct {byproduct_name}
      in its internal byproduct store.
      However, there was no byproduct registered with the name {byproduct_name}.
      """
      raise ByproductStorageError(error_msg)

  def clear(self) -> None:
    """
    Empties the byproducts but keeps the registrations.
    """
    consume(
      map(lambda byproduct: byproduct.clear(), 
          self._byproducts.values())
    ) 