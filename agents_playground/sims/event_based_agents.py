from typing import List, NamedTuple, Optional, Sized, Tuple, Union
from dataclasses import dataclass

import dearpygui.dearpygui as dpg

from agents_playground.agents.agent import Agent
from agents_playground.agents.direction import Direction, Vector2D
from agents_playground.agents.path import AgentAction, AgentPath, AgentStep
from agents_playground.agents.structures import Point, Size
from agents_playground.agents.utilities import update_agent_in_scene_graph
from agents_playground.core.event_based_simulation import EventBasedSimulation
from agents_playground.core.scheduler import JobScheduler
from agents_playground.core.time_utilities import TIME_PER_FRAME, TimeInMS, TimeUtilities
from agents_playground.renderers.agent import render_agents
from agents_playground.renderers.grid import render_grid
from agents_playground.renderers.path import render_path
from agents_playground.simulation.context import SimulationContext
from agents_playground.simulation.tag import Tag

@dataclass
class FutureAction:
  cost: TimeInMS
  action: AgentAction

  @property
  def location(self) -> Optional[Point]:
    return self.action.location if hasattr(self.action, 'location') else None # type: ignore[attr-defined]

StepsSchedule = List[FutureAction]

TIME_PER_STEP = TIME_PER_FRAME * 6
def sh(x: int, y: int, dir: Optional[Vector2D] = None, cost: TimeInMS=TIME_PER_STEP) -> FutureAction:
  """Convenance function for building a scheduled path step.
  
  Args:
    x: The tile/cell horizontal location to move to in the step.
    y: The tile/cell vertical location to move to in the step.
    dir: The direction the agent should face. 
    when: The number of milliseconds to when the action should be invoked.

  Returns:
    An action for an agent to take in the future.
  """
  action = AgentStep(Point(x,y), dir)
  return FutureAction(cost, action)

class EventBasedAgentsSim(EventBasedSimulation):
  def __init__(self) -> None:
    super().__init__()
    self._sim_description = 'Scheduled event based agent simulation.'
    self._sim_instructions = 'Click the start button to begin the simulation.'
    self._cell_size = Size(20, 20)
    self._cell_center_x_offset: float = self._cell_size.width/2
    self._cell_center_y_offset: float = self._cell_size.height/2
    self._agent: Agent = Agent()
    self._agent_ref: Tag = dpg.generate_uuid()
    self._paths: StepsSchedule = self._build_path()
    self._agent.movement_strategy(build_explorer_function(self._paths, self._scheduler))
    self.add_layer(render_grid, 'Terrain')
    self.add_layer(render_path, 'Paths')
    self.add_layer(render_agents, 'Agents')
  
  def _build_path(self) -> StepsSchedule:
    path = [
      # Walk 5 steps East.
      sh(9,4, Direction.EAST), sh(10,4), sh(11,4), sh(12,4), sh(13,4), sh(14,4),
      # Walk 3 steps south
      sh(14, 5, Direction.SOUTH), sh(14, 6), sh(14, 7),
      # Walk 6 steps to the East
      sh(15, 7, Direction.EAST), sh(16, 7), sh(17, 7), sh(18, 7), sh(19, 7), sh(20, 7),
      # Walk 2 steps south
      sh(20, 8, Direction.SOUTH), sh(20, 9),
      # Walk 8 steps to the West
      sh(19, 9, Direction.WEST), sh(18, 9, Direction.WEST), sh(17, 9, Direction.WEST), sh(16, 9, Direction.WEST), sh(15, 9, Direction.WEST), sh(14, 9, Direction.WEST), sh(13, 9, Direction.WEST), sh(12, 9, Direction.WEST),
      ## Walk North 3 steps
      sh(12, 8, Direction.NORTH), sh(12, 7), sh(12, 6), 
      # Walk West 3 steps
      sh(11, 6, Direction.WEST), sh(10, 6), sh(9, 6),
      # Walk North
      sh(9, 5, Direction.NORTH)
    ]
    return path

  def _establish_context_ext(self, context: SimulationContext) -> None:
    """Setup simulation specific context variables."""
    context.details['cell_size'] = self._cell_size
    context.details['paths'] = self._paths
    context.details['cell_center_x_offset'] = self._cell_center_x_offset
    context.details['cell_center_y_offset'] = self._cell_center_y_offset
    context.details['agent_node_refs'] = [self._agent_ref]
    
  def _bootstrap_simulation_render(self) -> None:
    # Schedule the first action.
    # TODO: Can this be cleaner?
    self._agent.explore()

  def _sim_loop_tick(self, **args):
    """Handles one tick of the simulation."""
    # This will force a rerender by updating the scene graph.
    if self._agent.agent_scene_graph_changed:
      update_agent_in_scene_graph(self._agent, self._agent_ref, self._cell_size)

def build_explorer_function(path_to_walk: StepsSchedule, 
  job_scheduler: JobScheduler, 
  starting_step_index=-1):
  """A closure that enables an agent to traverse a list of points.
  
  Args:
    path_to_walk: The path the agent will traverse.
    job_scheduler: Scheduler for tracking when to run the action.
    starting_step_index: The index of the step the agent starts on.
  """
  path: StepsSchedule = path_to_walk
  scheduler: JobScheduler = job_scheduler
  step_index = starting_step_index

  def schedule_next_action(agent: Agent, **data) -> None:
    """Simulates the agent walking down a determined path.
    
    An agent travels at the speed of 1 cell per 3 frames.

    Args:
      agent: The agent that this function is bound to.
      data: Dictionary catch all for additional args.
    """
    nonlocal step_index, path
    step_index = step_index + 1 if step_index < len(path) - 1 else 0
    step: FutureAction = path[step_index]

    # We'll explore again after the step is taken.
    step.action.after_action = agent.explore

    job_params = {'agent': agent}
    time_to_take_next_step: TimeInMS = TimeUtilities.now() + step.cost
    scheduler.schedule(step.action.run, time_to_take_next_step, job_params)

  return schedule_next_action