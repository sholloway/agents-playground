"""
Nervous System
- Sensory Organs: Eyes, Ears, Skin, Nose, and Mouth
- Eyes  -> Visual System
- Ears  -> Auditory System, Vestibular System (Inner ear, balance)
- Skin  -> Somatosensory System (sense of touch)
- Nose  -> Olfactory System (Sense of Smell)
- Mouth -> Gustatory system (sense of taste)
"""
from types import SimpleNamespace
from agents_playground.agents.spec.agent_system import AgentSystem
from agents_playground.agents.systems.agent_auditory_system import AgentAuditorySystem
from agents_playground.agents.systems.agent_gustatory_system import AgentGustatorySystem
from agents_playground.agents.systems.agent_olfactory_system import AgentOlfactorySystem
from agents_playground.agents.systems.agent_somatosensory_system import AgentSomatosensorySystem
from agents_playground.agents.systems.agent_vestibular_system import AgentVestibularSystem
from agents_playground.agents.systems.agent_visual_system import AgentVisualSystem


class AgentNervousSystem(AgentSystem):
  def __init__(self) -> None:
    self.name = 'agent-nervous-system'
    self.subsystems = SimpleNamespace()
    self.register_system(AgentVisualSystem())
    self.register_system(AgentAuditorySystem())
    self.register_system(AgentVestibularSystem())
    self.register_system(AgentSomatosensorySystem()) 
    self.register_system(AgentOlfactorySystem()) 
    self.register_system(AgentGustatorySystem()) 
    