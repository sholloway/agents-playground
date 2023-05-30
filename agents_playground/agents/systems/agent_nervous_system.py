"""
Nervous System
- Sensory Organs: Eyes, Ears, Skin, Nose, and Mouth
- Eyes  -> Visual System
- Ears  -> Auditory System, Vestibular System (Inner ear, balance)
- Skin  -> Somatosensory System (sense of touch)
- Nose  -> Olfactory System (Sense of Smell)
- Mouth -> Gustatory system (sense of taste)
"""
from typing import List
from agents_playground.agents.byproducts.definitions import Stimuli

from agents_playground.agents.default.default_agent_system import SystemWithByproducts
from agents_playground.agents.spec.agent_memory_spec import Sensation
from agents_playground.agents.spec.byproduct_definition import ByproductDefinition
from agents_playground.agents.systems.agent_auditory_system import AgentAuditorySystem
from agents_playground.agents.systems.agent_gustatory_system import AgentGustatorySystem
from agents_playground.agents.systems.agent_olfactory_system import AgentOlfactorySystem
from agents_playground.agents.systems.agent_somatosensory_system import AgentSomatosensorySystem
from agents_playground.agents.systems.agent_vestibular_system import AgentVestibularSystem
from agents_playground.agents.systems.agent_visual_system import AgentVisualSystem

class AgentNervousSystem(SystemWithByproducts):
  def __init__(self) -> None:
    super().__init__(
      name                    = 'agent_nervous_system', 
      byproduct_defs          = [Stimuli], 
      internal_byproduct_defs = []
    )
    
    self.register_system(AgentVisualSystem())
    self.register_system(AgentAuditorySystem())
    self.register_system(AgentVestibularSystem())
    self.register_system(AgentSomatosensorySystem()) 
    self.register_system(AgentOlfactorySystem()) 
    self.register_system(AgentGustatorySystem()) 
