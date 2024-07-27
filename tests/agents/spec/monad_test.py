from __future__ import annotations

from typing import Any, Callable, Dict, Generic, List, Protocol, Set, TypeVar, cast

"""
What is the contract for a generic monad?
Two main components:
Unit : Take a value and turn it into a Monad
Bind : Take a Monad, apply a function to it and return a new Monad

Monads are contains for values that enable binding functions to 
them.

Is Memory a good fit for a monad?
For a memory, I need a generic container that can bind things like
- expire_on_ttl
- enable_skill_on_ttl

In this case a skill is a memory with a Time To Learn (ttl)
skill = Memory(value=CutWood, ttl=5).bind(enable_skill_on_ttl)

A fact is something an Agent knows to be true about it's world.
This could be used to drive agent behavior as an agent learns
more about it's world. Or as a game mechanic.
class WorldFacts(Enum):
  SkyIsBlue: int = auto()
fact = Memory(value=WorldFacts.SkyIsBlue)
"""

A = TypeVar("A")
B = TypeVar("B")


class Monad(Generic[A]):
    def __init__(self, value: A):
        self._value = value

    def bind(self, func: Callable[[A], B]) -> Monad[B]:
        result = func(self._value)
        return Monad[B](result)

    def unwrap(self) -> A:
        return self._value


class Memory(Monad, Generic[A]):
    def __init__(self, value: A):
        super().__init__(value)


class AgentSaw(Generic[A]):
    def __init__(self, saw_what: A):
        self._saw_what = saw_what


AgentId = int
saw = AgentSaw[AgentId](123)

memory_of_seeing_agent = Memory[AgentSaw](saw)

"""
Can a monad help wrap with arbitraty metadata?
Can I wrap a memory with concepts like time to live, and time to learn?
"""
