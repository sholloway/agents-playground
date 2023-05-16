from __future__ import annotations
from abc import abstractmethod
from types import SimpleNamespace
from typing import List, Protocol
from more_itertools import consume
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_life_cycle_phase import AgentLifeCyclePhase

from agents_playground.agents.spec.agent_system import AgentSystem

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
  """
  memory: AgentMemory
  perception: AgentPerception # Processes stimuli. What the agent is aware of.
  attention: AgentAttention # Identify irrelevant data and filter it out, enabling significant data to be distributed to the other mental processes. 

class AgentPerception(AgentSystem):
  """
  The organization, identification, and interpretation of sensory information in 
  order to represent and understand the presented information or environment.
  """

  def __init__(self) -> None:
    self.name = 'agent_perception'
    self.subsystems = SimpleNamespace()

  def before_subsystems_processed(self, characteristics: AgentCharacteristics, agent_phase: AgentLifeCyclePhase) -> None:
    """
    TODO: Collect all sensory information that the agent is experiencing.
    """
    return
  
  def after_subsystems_processed(self, characteristics: AgentCharacteristics, agent_phase: AgentLifeCyclePhase) -> None:
    """
    TODO: Prepare the stimuli for the attention subsystem.
    - This could mean storing it in one of the Agent's memory stores.
    """
    return

class AgentAttention(AgentSystem):
  """
  A state of focused awareness on a subset of the available sensation 
  perception information. 
  
  A key function of attention is to identify irrelevant data and filter it out, 
  enabling significant data to be distributed to the other mental processes.

  Responsible for spinning up cognitive processes (CP). Each frame ticks away at each 
  cognitive process. A CP can have a fixed time to live that could expire if 
  certain things don't happen or are interrupted (like an injury). 
  """
  # A cognitive process could take various amounts of time (frames). 
  # TODO: Would it make sense for cognitive processes to be subsystems?
  # My initial thought is it's not a good fit. Cognitive processes have a shelf 
  # life then end where as subsystems are part of the agent and are only released
  # when the agent dies.
  active_mental_processes: List[CognitiveProcess] 
  
  def __init__(self) -> None:
    self.name = 'agent_attention'
    self.subsystems = SimpleNamespace()

  def before_subsystems_processed(self, characteristics: AgentCharacteristics, agent_phase: AgentLifeCyclePhase) -> None:
    """
    TODO: 
    - Process the sensory memory. Does a new cognitive process need to be spun up?
    - 
    """
    return
  
  def after_subsystems_processed(self, characteristics: AgentCharacteristics, agent_phase: AgentLifeCyclePhase) -> None:
    """
    TODO: 
    - Iterate one frame of processing for each cognitive process. 
    """
    consume(map(lambda mental_process: mental_process.process(), self.active_mental_processes)) 
    return


class AgentMemory(Protocol):
  sensory_memory: SensoryMemory
  working_memory: WorkingMemory	
  long_term_memory: LongTermMemory	


class CognitiveProcess(Protocol):
  @abstractmethod
  def process():
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