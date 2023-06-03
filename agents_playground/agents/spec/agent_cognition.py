"""
Key Concepts in the Agent Model
- Internal State
- Hierarchy of Systems
- Physicality
- Position
- Movement
- Style

Rather than an AgentCognition class there is just systems like:
- AgentPerceptionSystem
- AgentAttentionSystem

Where should memory live? 
- The three types don't necessarily have to live together. sensory_memory could
  live in AgentCognition and working memory live in AgentAttention for example.
  There needs to be a propagation chain with the systems but I currently don't 
  a way to do that.

Cognition refers to "the mental action or process of acquiring knowledge and 
  understanding through thought, experience, and the senses". It encompasses all
  aspects of intellectual functions and processes.

  Stimuli -> Sensations -> Emotion -> (Moods | Feelings/Beliefs) | Behavior
  Stimuli -> Perception -> Attention -> Cognitive Processes 

  Nervous System  -> (Collects Stimuli) 
                  -> Agent Perception -> (Sensations/SensoryMemory) 
                  -> Agent Attention -> (Memory/WorkingMemory) 
                  -> Cognitive Processes -> (Memory, Skill, Fact/LongTermMemory)
                  -> Action

The above implies a propagation pipeline from the Nervous System to the 
Cognitive Systems, however the ability to base things from one system to another
is limited to the AgentCharacteristics and AgentLifeCyclePhase.
- Should that contract be made more generic or should a different communication 
  mechanism be introduced?


How does the Agent's perception system become aware of the stimuli?
- Observer Pattern?
- Msg Broker style delivery.
- Collected by the nervous system and handed off?
- Trying to use the concept of a system byproduct. Using a SimpleNamespace
  to pass around outputs. I think I can make that work, however it is poorly defined.
  It leaks information. Systems need to know what the expected output to produce is.
  Is there some way to bake that into the Systems abstraction? This seems very 
  error prone. Like when a system is registered, can we declare the byproduct?

The responsibility of the perception system is to really sort through all the 
noise generated by the nervous system receptors and prioritize what the attention
system should look at. Examples
- There are 5 organs alerting of pain. That should be collapsed down to one.
- The agent has cast rays from the visual system. It can "see" 30 other agents.
  The perception system should simplify that somehow to allow the attention system 
  to recognize the agents it knows. This would probably need to be proximity based.


Consider that emotions are reactive.
Personality is persistent. 
"""