
import pytest
from pytest_mock import MockerFixture

from agents_playground.agents.default.default_agent import DefaultAgent
from agents_playground.agents.default.default_agent_memory import DefaultAgentMemory
from agents_playground.agents.default.default_agent_state import DefaultAgentState
from agents_playground.agents.default.default_agent_system import DefaultAgentSystem
from agents_playground.agents.default.named_agent_state import NamedAgentActionState
from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.agents.systems.agent_nervous_system import AgentNervousSystem
from agents_playground.agents.systems.agent_perception_system import AgentPerceptionSystem

"""
Test an agent's ability to have cognition (i.e. mental capacity).
"""

@pytest.fixture
def nervous_agent(mocker: MockerFixture) -> AgentLike:
  """
  Create an agent that has a nervous system wired up.
  """
  root_system = DefaultAgentSystem(name = 'root-system')
  root_system.register_system(AgentNervousSystem())
  return DefaultAgent(
    initial_state = mocker.Mock(),
    style = mocker.Mock(),
    identity=mocker.Mock(),
    physicality=mocker.Mock(),
    position=mocker.Mock(),
    movement         = mocker.Mock(),
    agent_memory     = DefaultAgentMemory(),
    internal_systems = root_system
  )

@pytest.fixture
def perceptive_agent(nervous_agent: AgentLike) -> AgentLike:
  nervous_agent.internal_systems.register_system(AgentPerceptionSystem())
  return nervous_agent

class TestAgentPerception:
  def test_agent_sees_something(self, mocker: MockerFixture, perceptive_agent: AgentLike) -> None:
    # Confirm that the visual system is in place.
    assert perceptive_agent.internal_systems.subsystems.agent_nervous_system.subsystems.visual_system is not None
    
    # Setup something for the agent to see.
    """
    The implementation of the life systems are each nontrivial. They should be on 
    their own branch.
    The challenge here, is the agent needs access to the scene.
    The other agents, the entities. Lights whatever. 

    How does a sim work.
    SimLoop -> _process_sim_cycle()
      TaskScheduler -> consume() the queued Tasks
        Task -> Loop through Agents in a scene
          Agent -> transition_state() 

    Shouldn't pass the entire scene in. Just entities and agents.
    Need to filter active agent out.

    This is probably where performance is going to get harder.
    Ray casting O(n^2).

    I could do something similar to the Conway's game. Have a data structure
    that associates the agent's cell location. Then find the cells that the view 
    frustum overlaps, then just select those agents.
    Use a triangle for an agent's view frustum to simplify the intersection tests.

    Then cast a ray from the agent to each of the filtered agents and check if anything 
    intersects first.

    Algorithm
    1. Prepare the structure that organize Agents by their current location.
    2. Prepare the structure that organizes the static entities by their current location.
       Note: We may be able to get away with doing this step just once.
       Note: This is sim specific.
    3. Filter out any agent that is sleeping or otherwise inactive.
    4. For agent in the active agents.
      A. Calculate the agent's view frustum from their facing vector.
    5. For agent in the active agents.
      A. Find the cells that the agent's view Frustum intersects.
      B. Find any agents that are in the cells from the last step.
      For each selected agent, 
        1. Cast a ray from the active agent to the selected agent.
        2. Determine if anything else (entities, other agents) intersects that ray.
           If the answer is no, then active agent can "see" the selected agent.
           The visual system should store a Sensation memory in its Stimuli byproduct.
           Associate the seen agent's ID in the sensation memory.
      
       
    """

    # Process the agent's systems.
    perceptive_agent.transition_state()

    # Confirm the agent saw something.
    # Need to confirm the sensory memory contains a visual sensation.
    assert len(perceptive_agent.memory.sensory_memory.memory_store) == 1

  
  def test_agent_hears_something(self, mocker: MockerFixture, perceptive_agent: AgentLike) -> None:
    assert True
  
  def test_agent_touches_something(self, mocker: MockerFixture, perceptive_agent: AgentLike) -> None:
    assert True
  
  def test_agent_smells_something(self, mocker: MockerFixture, perceptive_agent: AgentLike) -> None:
    assert True
  
  def test_agent_tastes_something(self, mocker: MockerFixture, perceptive_agent: AgentLike) -> None:
    assert True
  
  def test_agent_vestibular(self, mocker: MockerFixture, perceptive_agent: AgentLike) -> None:
    assert True
  