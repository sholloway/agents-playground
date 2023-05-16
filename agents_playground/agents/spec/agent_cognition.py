from __future__ import annotations
from abc import abstractmethod
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
"""

class AgentCognition(Protocol):
  """
  Cognition refers to "the mental action or process of acquiring knowledge and 
  understanding through thought, experience, and the senses". It encompasses all
  aspects of intellectual functions and processes.

  Stimuli -> Sensations -> Emotion -> (Moods | Feelings/Beliefs) | Behavior
  Stimuli -> Perception -> Attention -> Cognitive Processes 
  """
  memory: AgentMemory
  perception: AgentPerception # Processes stimuli. What the agent is aware of.
  attention: AgentAttention # Identify irrelevant data and filter it out, enabling significant data to be distributed to the other mental processes. 

class AgentMemory(Protocol):
  sensory_memory: SensoryMemory
  working_memory: WorkingMemory	
  long_term_memory: LongTermMemory	


class AgentPerception(Protocol):
  """
  The organization, identification, and interpretation of sensory information in 
  order to represent and understand the presented information or environment.
  """

class AgentAttention(Protocol):
  """
  A state of focused awareness on a subset of the available sensation 
  perception information. 
  
  A key function of attention is to identify irrelevant data and filter it out, 
  enabling significant data to be distributed to the other mental processes.

  Responsible for spinning up cognitive processes (CP). Each frame ticks away at each 
  cognitive process. A CP can have a fixed time to live that could expire if 
  certain things don't happen or are interrupted (like an injury). 
  """
  active_mental_processes: List[CognitiveProcess] # A cognitive process could take various amounts of time (frames). 

class CognitiveProcess(Protocol):
  ...

class Thought(CognitiveProcess):
  ...

class Imagination(CognitiveProcess):
  ...

class Judgement(CognitiveProcess):
  ...

class Evaluation(CognitiveProcess):
  ...

class Reasoning(CognitiveProcess):
  ...

class Computation(CognitiveProcess):
  ...

class ProblemSolving(CognitiveProcess):
  ...

class DecisionMaking(CognitiveProcess):
  ...

class Comprehension(CognitiveProcess):
  ...

class Speaking(CognitiveProcess):
  ...

class Writing(CognitiveProcess):
  ...

class FormationOfKnowledge(CognitiveProcess):
  ...