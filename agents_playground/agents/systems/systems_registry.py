
from typing import Callable, Dict, Final

from agents_playground.agents.default.default_agent_system import DefaultAgentSystem
from agents_playground.agents.systems.agent_attention_system import AgentAttentionSystem
from agents_playground.agents.systems.agent_auditory_system import AgentAuditorySystem
from agents_playground.agents.systems.agent_gustatory_system import AgentGustatorySystem
from agents_playground.agents.systems.agent_nervous_system import AgentNervousSystem
from agents_playground.agents.systems.agent_olfactory_system import AgentOlfactorySystem
from agents_playground.agents.systems.agent_perception_system import AgentPerceptionSystem
from agents_playground.agents.systems.agent_recognition_system import AgentRecognitionSystem
from agents_playground.agents.systems.agent_somatosensory_system import AgentSomatosensorySystem
from agents_playground.agents.systems.agent_vestibular_system import AgentVestibularSystem
from agents_playground.agents.systems.agent_visual_system import AgentVisualSystem
    
do_nothing_system = lambda *args, **kargs: DefaultAgentSystem(name = 'default-system')

AGENT_SYSTEMS_REGISTRY: Final[Dict[str, Callable]] = {
  # Top level systems
  'nervous_system': lambda : AgentNervousSystem(),
  'attention_system': lambda : AgentAttentionSystem(),
  'perception_system': lambda : AgentPerceptionSystem(), 
  'recognition_system': lambda : AgentRecognitionSystem(), 

  # Nervous System's Subsystems
  'auditory_system': lambda : AgentAuditorySystem(),
  'gustatory_system': lambda : AgentGustatorySystem(),
  'olfactory_system': lambda : AgentOlfactorySystem(),
  'somatosensory_system': lambda : AgentSomatosensorySystem(),
  'vestibular_system': lambda : AgentVestibularSystem(),
  'visual_system': lambda : AgentVisualSystem()
}