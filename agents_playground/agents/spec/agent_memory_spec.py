from __future__ import annotations

from typing import Any, List, Protocol, Dict, Set, Tuple
from agents_playground.agents.byproducts.sensation import Sensation
from agents_playground.agents.spec.tick import Tick as FrameTick
from agents_playground.containers.ttl_store import TTLStore
from agents_playground.counter.counter import Counter, CounterBuilder

from agents_playground.simulation.tag import Tag
      
class AgentMemoryLike(FrameTick, Protocol):
  """
  The top level memory store of an agent.
  """
  sensory_memory: SensoryMemoryLike
  working_memory: WorkingMemoryLike	
  long_term_memory: LongTermMemoryLike	

  def tick(self) -> None:
    self.sensory_memory.tick()
    self.working_memory.tick()
    self.long_term_memory.tick()


class SensoryMemoryLike(FrameTick, Protocol):
  """
  Stores the memories of stimuli. This is intended to be used by the Nervous System
  and Perception System.
  """

  """
  What is the TTL of a sensation? By default probably just until the attention
  system processes it but I can imagine some situations might need a longer TTL.

  How should this work? A set of sensations may not be appropriate. For example,
  "I'm in pain" vs "My leg hurts, my back hurts, and I burned my hand. I feel a breeze."
  """
  memory_store: List[Sensation] # TODO: Perhaps a priority queue will work better.

  def sense(self, memory: Sensation) -> None:
    """
    Stores a sensation detected by the Nervous System.
    The sensory memory remembers short term stimuli/sensations.
    These are all of the inputs from the Nervous System. Pain, Warmth, Cold, touch, etc...
    """
    self.memory_store.append(memory)

  def feel(self) -> List[Sensation]:
    """
    Enable the Attention system process the various sensations.

    Does this make sense? 
    
    The Attention system may just loop through all the sensations. Or should 
    there be some kind of priority or categorization? 
    - Perhaps pain is always processed first?
    - Sensations could be stored in association with their system. By that would
      mean the perception system has to be aware of the other systems. 
    - A priority queue may be appropriate.
    """
    return self.memory_store

  def forget(self, memory: Sensation) -> None:
    self.memory_store.remove(memory)

  def forget_all(self) -> None:
    self.memory_store.clear()


class WorkingMemoryLike(FrameTick, Protocol):
  """
  The Agent's short term memory. This is used by the Agent's Attention System to 
  store any required data for the cognitive processes it's thinking about.
  """

  """
  Recognitions are the other agents in the immediate area that this agent is aware.
  Intended Behavior:
    When an agent is recognized, it is placed in the working memory. A recognition
    has a TTL. Each time (sim tick) that the agent is recognized the TTL is renewed.
    When the TTL expires the recognition is removed from working memory.
  """
  recognitions: TTLStore 


class LongTermMemoryLike(FrameTick, Protocol):
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
    return

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

class Relationship:
  """The type of relationship between two agents."""
  ...