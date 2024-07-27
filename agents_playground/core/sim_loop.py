from __future__ import annotations

from enum import Enum
from functools import wraps
import os
import threading
from typing import Dict, List

from agents_playground.agents.utilities import update_all_agents_display
from agents_playground.core.constants import (
    FRAME_SAMPLING_SERIES_LENGTH,
    HARDWARE_SAMPLING_WINDOW,
    UPDATE_BUDGET,
    UTILITY_UTILIZATION_WINDOW,
)
from agents_playground.counter.counter import Counter, CounterBuilder
from agents_playground.core.duration_metrics_collector import (
    collected_duration_metrics,
    sample_duration,
)
from agents_playground.core.observe import Observable
from agents_playground.core.samples import Samples
from agents_playground.core.task_scheduler import TaskScheduler
from agents_playground.core.time_utilities import TimeUtilities
from agents_playground.core.types import TimeInMS, TimeInSecs
from agents_playground.core.waiter import Waiter
from agents_playground.legacy.scene.scene import Scene
from agents_playground.simulation.context import SimulationContext
from agents_playground.simulation.sim_state import SimulationState


from agents_playground.sys.logger import get_default_logger

logger = get_default_logger()


class SimLoopEvent(Enum):
    UTILITY_SAMPLES_COLLECTED = "UTILITY_SAMPLES_COLLECTED"
    TIME_TO_MONITOR_HARDWARE = "TIME_TO_MONITOR_HARDWARE"
    SIMULATION_STARTED = "SIMULATION_STARTED"
    SIMULATION_STOPPED = "SIMULATION_STOPPED"


class SimLoop(Observable):
    """The main loop of a simulation."""

    def __init__(
        self, scheduler: TaskScheduler = TaskScheduler(), waiter=Waiter()
    ) -> None:
        super().__init__()
        self._task_scheduler = scheduler
        self._sim_stopped_check_time: TimeInSecs = 0.5
        self._waiter = waiter
        self._sim_current_state: SimulationState = SimulationState.INITIAL
        self._utility_sampler = CounterBuilder.integer_counter_with_defaults(
            start=UTILITY_UTILIZATION_WINDOW,
            decrement_step=1,
            min_value=0,
            min_value_reached=self._utility_samples_collected,
        )

        self.__monitor_hardware_counter = CounterBuilder.integer_counter_with_defaults(
            start=HARDWARE_SAMPLING_WINDOW,
            decrement_step=1,
            min_value=0,
            min_value_reached=self.__notify_monitor_usage,
        )

    def __del__(self) -> None:
        logger.info("SimLoop deleted.")

    @property
    def running(self) -> bool:
        """Determines if the sim loop is currently running."""
        return self._sim_current_state == SimulationState.RUNNING

    @property
    def simulation_state(self) -> SimulationState:
        return self._sim_current_state

    @simulation_state.setter
    def simulation_state(self, next_state: SimulationState) -> None:
        self._sim_current_state = next_state
        match next_state:
            case SimulationState.RUNNING:
                super().notify(SimLoopEvent.SIMULATION_STARTED.value)
            case SimulationState.STOPPED:
                super().notify(SimLoopEvent.SIMULATION_STOPPED.value)

    def end(self) -> None:
        self._sim_current_state = SimulationState.ENDED
        if hasattr(self, "_sim_thread"):
            self._sim_thread.join()

    def start(self, context: SimulationContext) -> None:
        """Create a thread for updating the simulation."""
        # Note: A daemonic thread cannot be "joined" by another thread.
        # They are destroyed when the main thread is terminated.
        self._sim_thread = threading.Thread(
            name="simulation-loop", target=self._sim_loop, args=(context,), daemon=True
        )
        self._sim_thread.start()

    def _sim_loop(self, context: SimulationContext):
        """The thread callback that processes a simulation tick.

        Using the definitions in agents_playground.core.time_utilities, this ensures
        a fixed time for scheduled events to be ran. Rendering is handled automatically
        via DataPyUI (note: VSync is turned on when the Viewport is created.)

        For 60 FPS, TIME_PER_UPDATE is 5.556 ms.
        """
        while self.simulation_state is not SimulationState.ENDED:
            match self.simulation_state:
                case SimulationState.RUNNING:
                    self._process_sim_cycle(context)
                    self._utility_sampler.decrement(frame_context=context)
                    self.__monitor_hardware_counter.decrement()
                case SimulationState.STOPPED | SimulationState.INITIAL:
                    # The sim isn't running so don't keep checking it.
                    self._wait_until_next_check()
                case _:
                    raise Exception(
                        f"SimLoop: Unknown SimulationState {self.simulation_state}"
                    )

    @sample_duration(sample_name="frame-tick", count=FRAME_SAMPLING_SERIES_LENGTH)
    def _process_sim_cycle(self, context: SimulationContext) -> None:
        loop_stats = {}
        loop_stats["start_of_cycle"] = TimeUtilities.now()
        time_to_render: TimeInMS = loop_stats["start_of_cycle"] + UPDATE_BUDGET

        # Are there any tasks to do in this cycle? If so, do them.
        self._process_per_frame_tasks()
        context.scene.tick()

        # Is there any time until we need to render?
        # If so, then sleep until then.
        self._waiter.wait_until_deadline(time_to_render)
        self._update_render(context.scene)

    @sample_duration(
        sample_name="waiting-until-next-frame", count=FRAME_SAMPLING_SERIES_LENGTH
    )
    def _wait_until_next_check(self) -> None:
        self._waiter.wait(self._sim_stopped_check_time)

    @sample_duration(sample_name="running-tasks", count=FRAME_SAMPLING_SERIES_LENGTH)
    def _process_per_frame_tasks(self) -> None:
        self._task_scheduler.queue_holding_tasks()
        self._task_scheduler.consume()

    @sample_duration(sample_name="rendering", count=FRAME_SAMPLING_SERIES_LENGTH)
    def _update_render(self, scene: Scene) -> None:
        for _, entity_grouping in scene.entities.items():
            for _, entity in entity_grouping.items():
                entity.update(scene)

        """
    TODO: Move this to an 'update_method' style function on Agent.
    Perhaps there needs to be a default update function on Agent that can be
    overridden. That may be putting the cart before the horse. Can the update_agent_in_scene_graph
    be merged with the configure_item call? It would be nice to simplify.

    Currently we're doing two passes over scene.agents and in the loop below the
    SimLoop has knowledge of how to render an Agent. That's not good separation
    of concerns.
    """
        update_all_agents_display(scene)

    def _utility_samples_collected(self, **kargs) -> None:
        """
        I'd like to use this hook to copy the samples to the context (eventually context.stats)
        and use the update method on the Simulation to grab the samples.

        1. copy the samples to the context
        2. Clear the SAMPLE dict.
        3. Notify the Simulation
        4. Reset the counter.

        Challenges
        - How to access the context instance? Context is not currently bound
          to the counter or SimLoop.
        """
        context = kargs["frame_context"]
        context.stats.per_frame_samples = collected_duration_metrics().samples
        super().notify(SimLoopEvent.UTILITY_SAMPLES_COLLECTED.value)
        self._utility_sampler.reset()

    def __notify_monitor_usage(self) -> None:
        super().notify(SimLoopEvent.TIME_TO_MONITOR_HARDWARE.value)
