from __future__ import annotations
from typing import Protocol, Dict, Set, Tuple

from agents_playground.simulation.tag import Tag


class AgentMemoryLike(Protocol):
  """
  The top level memory store of an agent.
  """
  sensory_memory: SensoryMemoryLike
  working_memory: WorkingMemoryLike	
  long_term_memory: LongTermMemoryLike	


class SensoryMemoryLike(Protocol):
  """
  Stores the memories of stimuli. This is intended to be used by the Nervous System
  and Perception System.
  """
  memory_store: Dict

  def remember(self, memory: Sensation) -> None:
    """
    What is a memory?
    - The sensory memory remembers short term stimuli/sensations.
    - All of the inputs from the Nervous System. Pain, Warmth, Cold, touch, etc...
    - What is the TTL of a sensation? By default probably just until the attention
      system processes it but I can imagine some situations might need a longer TTL.

    - How should this work? A set of sensations may not be appropriate. For example,
      "I'm in pain" vs "My leg hurts, my back hurts, and I burned my hand. I feel a breeze."
    """
    ...

  def recall(self) -> Sensation:
    ...

  def forget(self, memory: Sensation) -> None:
    ...

class WorkingMemoryLike(Protocol):
  """
  The Agent's short term memory. This is used by the Agent's Attention System to 
  store any required data for the cognitive processes it's thinking about.
  """
  ...

class LongTermMemoryLike(Protocol):
  memories: Set[Memory]
  skills: Set[Skill]
  knowledge: Set[Fact]

  # Maps another agent's tag to how this agent perceives their relationship.
  relationships: Dict[Tag, Relationship] 

  """
  The Agent's Long Term memory. This stores the the history of the agent. 
  What's happened to it, who it knows, facts, and skills.
  """
  def remember(self, memory: Memory) -> None:
    """Make a long term memory."""
    ...

  def learn(self, skill: Skill) -> None:
    """Acquire a skill."""
    ...

  def memorize(self, fact: Fact) -> None:
    """Remember a fact."""
    ...

  def recognize(self, AgentLike) -> Tuple[bool, Relationship]:
    """Does the agent know another agent?"""
    ...


class Memory:
  ...

class Skill:
  ...

class Fact:
  ...

class Sensation:
  ...

class Relationship:
  """The type of relationship between two agents."""
  ...