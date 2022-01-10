from typing import List, NamedTuple, Optional, Tuple, Union
from dataclasses import dataclass

import dearpygui.dearpygui as dpg

from agents_playground.agents.agent import Agent
from agents_playground.agents.direction import Direction
from agents_playground.agents.path import AgentAction, AgentPath, AgentStep
from agents_playground.core.event_based_simulation import EventBasedSimulation
from agents_playground.agents.structures import Point
from agents_playground.agents.utilities import update_agent_in_scene_graph
from agents_playground.core.scheduler import JobScheduler
from agents_playground.core.time_utilities import TIME_PER_FRAME, TimeInMS, TimeUtilities

SIM_DESCRIPTION = 'Scheduled event based agent simulation.'
SIM_INSTRUCTIONs = 'Click the start button to begin the simulation.'

"""
The Components that together make the agent move.
- The Agent
- The Agent's Movement Strategy, perhaps this is the missing piece.
- The Scheduler
- The path of actions
- update_agent_in_scene_graph

An action updates the agents location...

BUG: Right now nothing is calling self._agent.explore(**data)
The other approach does this in sim_loop_tick.

Which is better, having agent.explore() be scheduled or the action.process()?
Action.process feels better. If there was a way to chain a secondary callable
to a scheduled job, then we could do something like:
  run job, then explore again.
"""

@dataclass
class FutureAction:
  cost: TimeInMS
  action: AgentAction

StepsSchedule = List[FutureAction]

TIME_PER_STEP = TIME_PER_FRAME * 6
def sh(x: int, y: int, dir: Optional[Direction] = None, cost: TimeInMS=TIME_PER_STEP) -> FutureAction:
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
    self._agent: Agent = Agent()
    
    # TODO: Registering layers should be more formal than this.
    self._layers['agents'] = dpg.generate_uuid()
    self._agent_ref: Union[int, str] = dpg.generate_uuid()
    self._cell_size = Point(20, 20)
    self._path: StepsSchedule = self._build_path()
    self._agent.movement_strategy(build_explorer_function(self._path, self._scheduler))
  
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

  def _initial_render(self) -> None:
    self._context.parent_window.width = dpg.get_item_width(super().primary_window)
    self._context.parent_window.height = dpg.get_item_width(super().primary_window)
    self._context.canvas.width = self._context.parent_window.width if self._context.parent_window.width else 0
    self._context.canvas.height = self._context.parent_window.height - 40 if self._context.parent_window.height else 0

    with dpg.drawlist(
      tag=self._sim_initial_state_dl_ref, 
      parent=self._sim_window_ref, 
      width=self._context.canvas.width, 
      height=self._context.canvas.height): 
      dpg.draw_text(pos=(20,20), text=SIM_DESCRIPTION, size=13)
      dpg.draw_text(pos=(20,40), text=SIM_INSTRUCTIONs, size=13)

  def _bootstrap_simulation_render(self) -> None:
    self._context.agent_style.stroke_thickness = 1.0
    self._context.agent_style.stroke_color = (255,255,255)
    self._context.agent_style.fill_color = (0, 0, 255)
    self._context.agent_style.size.width = 20
    self._context.agent_style.size.height = 20
    agent_half_size: Size = Size()
    agent_half_size.width = self._context.agent_style.size.width / 2
    agent_half_size.height = self._context.agent_style.size.height / 2

    with dpg.drawlist(
      parent=self._sim_window_ref, 
      width=self._context.canvas.width, 
      height=self._context.canvas.height): 

      with dpg.draw_layer(tag=self._layers['agents']):
        with dpg.draw_node(tag=self._agent_ref):
          # Draw the triangle centered at cell (0,0) in the grid and pointing EAST.
          dpg.draw_triangle(
            p1=(agent_half_size.width,0), 
            p2=(-agent_half_size.width, -agent_half_size.height), 
            p3=(-agent_half_size.width, agent_half_size.height), 
            color=self._context.agent_style.stroke_color, 
            fill=self._context.agent_style.fill_color, 
            thickness=self._context.agent_style.stroke_thickness
          )

      with dpg.draw_layer(tag=self._layers['stats']):
        dpg.draw_text(tag=self._stats['fps'], pos=(20,20), text='Frame Rate (Hz): 0', size=13)
        dpg.draw_text(tag=self._stats['utilization'], pos=(20,40), text='Utilization (%): 0', size=13)


    # Schedule the first action. This could be cleaner.
    self._agent.explore()

  def _sim_loop_tick(self, **args):
    """Handles one tick of the simulation."""
    # This will force a rerender by updating the scene graph.
    if self._agent.agent_changed:
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