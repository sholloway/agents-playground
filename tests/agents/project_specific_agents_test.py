from pytest_mock import MockerFixture

from agents_playground.agents.default.default_agent import DefaultAgent
from agents_playground.agents.default.default_agent_state import DefaultAgentState
from agents_playground.agents.default.map_agent_action_selector import MapAgentActionSelector
from agents_playground.agents.default.named_agent_state import NamedAgentActionState
from agents_playground.agents.spec.agent_life_cycle_phase import AgentLifeCyclePhase
from agents_playground.core.types import Coordinate, Size

class TestProjectSpecificAgents:
  def test_agent_selection(self, mocker: MockerFixture) -> None:
    agent = DefaultAgent(
      initial_state = DefaultAgentState(
        initial_state = NamedAgentActionState('IDLE'),
        action_selector = MapAgentActionSelector(state_map = {}),
        agent_is_selected = False,
      ),
      style            = mocker.Mock(),
      identity         = mocker.Mock(),
      physicality      = mocker.Mock(),
      position         = mocker.Mock(),
      movement         = mocker.Mock(),
      internal_systems = mocker.Mock()
    )

    agent.handle_agent_selected = mocker.Mock()
    agent.handle_agent_deselected = mocker.Mock()

    assert not agent.selected
    agent.handle_agent_selected.assert_not_called()
    
    agent.select()
    
    assert agent.selected
    agent.handle_agent_selected.assert_called_once()

    agent.deselect()
    agent.handle_agent_deselected.assert_called_once()

  def test_moving_the_agent(self, mocker: MockerFixture) -> None:
    agent = DefaultAgent(
      initial_state = DefaultAgentState(
        initial_state = NamedAgentActionState('IDLE'),
        action_selector = MapAgentActionSelector(state_map = {}),
        agent_is_selected = False,
      ),
      style            = mocker.Mock(),
      identity         = mocker.Mock(),
      physicality      = mocker.Mock(),
      position         = mocker.Mock(),
      movement         = mocker.Mock(),
      internal_systems = mocker.Mock()
    )

    assert not agent.agent_scene_graph_changed
    agent.position.move_to.assert_not_called()
    agent.physicality.calculate_aabb.assert_not_called()

    agent.move_to(new_location = Coordinate(14, 22), cell_size = Size(10, 10))

    assert agent.agent_scene_graph_changed
    agent.position.move_to.assert_called_once()
    agent.physicality.calculate_aabb.assert_called_once()

  def test_changing_to_next_state(self, mocker: MockerFixture) -> None:
    agent = DefaultAgent(
      initial_state    = mocker.Mock(),
      style            = mocker.Mock(),
      identity         = mocker.Mock(),
      physicality      = mocker.Mock(),
      position         = mocker.Mock(),
      movement         = mocker.Mock(),
      internal_systems = mocker.Mock()
    )

    agent.transition_state()
    characteristics = agent.agent_characteristics()

    print(agent.internal_systems.process.call_args_list[0].args)
    assert agent.internal_systems.process.call_count == 2
    assert agent.internal_systems.process.call_args_list[0].args == ((characteristics, AgentLifeCyclePhase.PRE_STATE_CHANGE))
    assert agent.internal_systems.process.call_args_list[1].args == ((characteristics, AgentLifeCyclePhase.POST_STATE_CHANGE))

  def test_agent_transition_lifecycle(self, mocker: MockerFixture) -> None:
    agent = DefaultAgent(
      initial_state    = mocker.Mock(),
      style            = mocker.Mock(),
      identity         = mocker.Mock(),
      physicality      = mocker.Mock(),
      position         = mocker.Mock(),
      movement         = mocker.Mock(),
      internal_systems = mocker.Mock()
    )

    agent.before_state_change = mocker.Mock()
    agent.pre_state_change_process_subsystems = mocker.Mock()
    agent.change_state = mocker.Mock()
    agent.post_state_change_process_subsystems = mocker.Mock()
    agent.post_state_change = mocker.Mock()

    agent.transition_state()

    agent.before_state_change.assert_called_once()
    agent.pre_state_change_process_subsystems.assert_called_once()
    agent.change_state.assert_called_once()
    agent.post_state_change_process_subsystems.assert_called_once()
    agent.post_state_change.assert_called_once()