from math import copysign, radians
from typing import List
from typing import cast, Generator, Tuple

import dearpygui.dearpygui as dpg
from agents_playground.agents.spec.agent_spec import AgentLike

from agents_playground.core.task_scheduler import ScheduleTraps
from agents_playground.paths.linear_path import LinearPath
from agents_playground.paths.circular_path import CirclePath
from agents_playground.project.extensions import register_renderer, register_task
from agents_playground.renderers.color import Color, PrimaryColors
from agents_playground.legacy.scene.scene import Scene
from agents_playground.simulation.context import SimulationContext, Size
from agents_playground.simulation.tag import Tag

from agents_playground.sys.logger import get_default_logger
logger = get_default_logger()