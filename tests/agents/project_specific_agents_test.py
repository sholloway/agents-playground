from pytest_mock import MockerFixture

from agents_playground.agents.agent_spec import AgentActionStateLike
from agents_playground.agents.default_agent import (
  DefaultAgentState, 
  MapAgentActionSelector, 
  NamedAgentState
)

class TestProjectSpecificAgents:
  def test_agent_state_reset(self) -> None:
    agent_state = DefaultAgentState(
      initial_state = NamedAgentState(name = 'IDLE'), 
      action_selector = MapAgentActionSelector(state_map = {})
    )

    agent_state.require_render = True
    agent_state.require_scene_graph_update = True

    agent_state.reset()
    assert not agent_state.require_render
    assert not agent_state.require_scene_graph_update

  def test_agent_state_transitions(self) -> None:
    idle_state: AgentActionStateLike      = NamedAgentState(name = 'IDLE')
    resting_state: AgentActionStateLike   = NamedAgentState(name = 'RESTING')
    planning_state: AgentActionStateLike  = NamedAgentState(name = 'PLANNING')
    routing_state: AgentActionStateLike   = NamedAgentState(name = 'ROUTING')
    traveling_state: AgentActionStateLike = NamedAgentState(name = 'TRAVELING')

    state_map = {
      idle_state: idle_state,
      resting_state: planning_state,
      planning_state: routing_state,
      traveling_state: resting_state
    } 

    agent_state = DefaultAgentState(
      initial_state = idle_state, 
      action_selector = MapAgentActionSelector(state_map=state_map)
    )

    assert agent_state.current_action_state == idle_state
    
    # assign_action_state should remember the last state.
    agent_state.assign_action_state(resting_state)
    assert agent_state.current_action_state == resting_state
    assert agent_state.last_action_state == idle_state

    # transition_to_next_action
    agent_state.transition_to_next_action()
    assert agent_state.current_action_state == planning_state
    assert agent_state.last_action_state == resting_state