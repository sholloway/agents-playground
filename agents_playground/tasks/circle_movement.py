"""
Module containing coroutines related to moving circles.
"""

from math import sin, pi
from time import perf_counter
from typing import Generator

from agents_playground.core.task_scheduler import ScheduleTraps
from agents_playground.sys.logger import get_default_logger

logger = get_default_logger()


def pulse_circle_coroutine(*args, **kwargs) -> Generator:
    """A task that makes a 2D circle radius oscillate.

    Args:
      - scene: The scene to take action on.
      - circle_id: The agent to move along the path.
    """
    logger.info("pulse_circle: Starting task.")
    scene = kwargs["scene"]
    circle_id = kwargs["circle_id"]
    speed: float = kwargs["speed"]

    # TODO: What should the access pattern be?
    # Searching an array is less than ideal
    # circle = first_true(scene.entities.circles, None, lambda c: c.id == circle_id)
    circle = scene.entities["circles"][circle_id]

    if circle:
        try:
            while True:
                inflate_amount: float = 0.5 * (1 + sin(2 * pi * perf_counter()))
                circle.active_radius = (
                    circle.default_radius + circle.scale * inflate_amount
                )
                yield ScheduleTraps.NEXT_FRAME
        except GeneratorExit:
            logger.info("Task: pulse_circle - GeneratorExit")
        finally:
            logger.info("Task: pulse_circle - Task Completed")
    else:
        raise Exception(f"Could not find circle: {circle_id}")
