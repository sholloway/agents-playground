from types import SimpleNamespace
from agents_playground.agents.byproducts.sensation import Sensation
from agents_playground.agents.default.default_agent_system import SystemWithByproducts
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_life_cycle_phase import AgentLifeCyclePhase
from agents_playground.agents.spec.agent_system import AgentSystem
from agents_playground.agents.spec.byproduct_definition import ByproductDefinition

class AgentVisualSystem(SystemWithByproducts):
  """
  Provides the sense of sight. The eyes perceive light.
  """
  def __init__(self) -> None:
    super().__init__(
      name                    = 'visual-system', 
      byproduct_defs          = [ByproductDefinition('stimuli', Sensation)], 
      internal_byproduct_defs = []
    )

  """
  Thoughts:
  The default sim is a top down model. That doesn't have to be the case though.

  Top Down Model:
  - Agent has a physical orientation. (2d vector)
  - The agent has a view frustum. In 2d this can be a simple triangle.
    Rather than ray casting, an agent can "see something" if:
    1. That something intersects with the agent's view frustum.
    2. A ray cast from the agent to the "something" does not have any other
       collision first.
  """