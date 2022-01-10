from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Union

from agents_playground.agents.structures import Size
from agents_playground.styles.agent_style import AgentStyle

class SimulationEvents(Enum):
  WINDOW_CLOSED = 'WINDOW_CLOSED'

class SimulationState(Enum):
  INITIAL = 'simulation:state:initial'
  RUNNING = 'simulation:state:running'
  STOPPED = 'simulation:state:stopped'
  ENDED = 'simulation:state:ended'

SimulationStateTable = {
  SimulationState.INITIAL: SimulationState.RUNNING,
  SimulationState.RUNNING: SimulationState.STOPPED,
  SimulationState.STOPPED: SimulationState.RUNNING
}

RUN_SIM_TOGGLE_BTN_START_LABEL = 'Start'
RUN_SIM_TOGGLE_BTN_STOP_LABEL = 'Stop'

SimulationStateToLabelMap = {
  SimulationState.INITIAL: RUN_SIM_TOGGLE_BTN_START_LABEL,
  SimulationState.RUNNING: RUN_SIM_TOGGLE_BTN_STOP_LABEL,
  SimulationState.STOPPED: RUN_SIM_TOGGLE_BTN_START_LABEL
}

@dataclass(init=False)
class SimulationContext:
  parent_window: Size
  canvas: Size
  agent_style: AgentStyle
  details: dict[Any, Any]

  def __init__(self) -> None:
    self.parent_window = Size()
    self.canvas = Size()
    self.agent_style = AgentStyle()
    self.details = dict()

Tag = Union[int, float]

@dataclass
class RenderLayer:
  id: Tag
  label: str
  menu_item: Tag
  layer: Callable