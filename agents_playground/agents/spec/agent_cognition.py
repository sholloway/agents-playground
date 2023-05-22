from __future__ import annotations

from typing import List, Protocol

"""
Key Concepts in the Agent Model
- Internal State
- Hierarchy of Systems
- Physicality
- Position
- Movement
- Style

Perhaps there needs to be two hierarchies of systems on the Agent class.
- physical_systems
- mental_systems

Rather than an AgentCognition class there is just systems like:
- AgentPerceptionSystem
- AgentAttentionSystem

Where should memory live? 
- The three types don't necessarily have to live together. sensory_memory could
  live in AgentCognition and working memory live in AgentAttention for example.
  There needs to be a propagation chain with the systems but I currently don't 
  a way to do that.
"""

class AgentCognition(Protocol):
  """
  Cognition refers to "the mental action or process of acquiring knowledge and 
  understanding through thought, experience, and the senses". It encompasses all
  aspects of intellectual functions and processes.

  Stimuli -> Sensations -> Emotion -> (Moods | Feelings/Beliefs) | Behavior
  Stimuli -> Perception -> Attention -> Cognitive Processes 

  Nervous System -> Agent Perception -> Agent Attention -> Cognitive Processes -> Action
  """
  memory: AgentMemory
  perception: AgentPerception # Processes stimuli. What the agent is aware of.
  attention: AgentAttention # Identify irrelevant data and filter it out, enabling significant data to be distributed to the other mental processes. 


class AgentMemory(Protocol):
  sensory_memory: SensoryMemory
  working_memory: WorkingMemory	
  long_term_memory: LongTermMemory	