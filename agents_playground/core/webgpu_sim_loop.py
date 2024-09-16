from __future__ import annotations
from collections.abc import Callable
from enum import StrEnum
from threading import Event, Thread, Timer

import wx
from wx.core import wxEVT_NULL

from agents_playground.core.constants import (
    FRAME_SAMPLING_SERIES_LENGTH,
    HARDWARE_SAMPLING_WINDOW,
    MONITOR_FREQUENCY,
    UPDATE_BUDGET,
    UTILITY_UTILIZATION_WINDOW,
)
from agents_playground.core.duration_metrics_collector import (
    collected_duration_metrics,
    sample_duration,
)

from agents_playground.core.task_scheduler import TaskScheduler
from agents_playground.core.time_utilities import TimeUtilities
from agents_playground.core.types import TimeInMS, TimeInSecs
from agents_playground.core.waiter import Waiter
from agents_playground.counter.counter import CounterBuilder
from agents_playground.scene import Scene
from agents_playground.simulation.context import SimulationContext
from agents_playground.simulation.sim_state import SimulationState

from agents_playground.sys.logger import get_default_logger, log_call

logger = get_default_logger()

class WGPUSimLoopEventMsg(StrEnum):
    UPDATE_FPS = "UPDATE_FPS"
    UTILITY_SAMPLES_COLLECTED = "UTILITY_SAMPLES_COLLECTED"
    TIME_TO_MONITOR_HARDWARE = "TIME_TO_MONITOR_HARDWARE"
    SIMULATION_STARTED = "SIMULATION_STARTED"
    SIMULATION_STOPPED = "SIMULATION_STOPPED"
    REDRAW = "REDRAW"

# Define notification event ID for WGPUSimLoopEvent.
WGPU_SIM_LOOP_EVENT  = wx.NewId()

class WGPUSimLoopEvent(wx.PyEvent):
    def __init__(self, msg: WGPUSimLoopEventMsg):
        wx.PyEvent.__init__(self)
        self.SetEventType(WGPU_SIM_LOOP_EVENT)
        self.msg = msg

class RecurringAction(Timer):
    """Repeatedly invokes a function at a set interval."""
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class WGPUSimLoop:
    @log_call
    def __init__(
        self, 
        window: wx.Window,
        scheduler: TaskScheduler | None = None, 
        waiter: Waiter | None = None,
    ) -> None:
        super().__init__()
        self._window = window
        self._task_scheduler = TaskScheduler() if scheduler is None else scheduler
        self._waiter = Waiter() if waiter is None else waiter
        self._sim_stopped_check_time: TimeInSecs = 0.5
        self._sim_current_state: SimulationState = SimulationState.INITIAL
        """
        An actionable counter that controls when to prompt the 
        UI to display the the runtime metrics.
        """
        self._utility_sampler = CounterBuilder.integer_counter_with_defaults(
            start=UTILITY_UTILIZATION_WINDOW,
            decrement_step=1,
            min_value=0,
            min_value_reached=self._utility_samples_collected,
        )

        """
        An actionable counter that controls when to prompt the 
        UI to display the hardware metrics.
        """
        self.__monitor_hardware_counter = CounterBuilder.integer_counter_with_defaults(
            start=HARDWARE_SAMPLING_WINDOW,
            decrement_step=1,
            min_value=0,
            min_value_reached=self._notify_monitor_usage,
        )

        """A timer that controls taking action once per second."""
        self._once_per_second_timer: Timer # Initialized when the sim loop is started.

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
                wx.PostEvent(self._window, WGPUSimLoopEvent(WGPUSimLoopEventMsg.SIMULATION_STARTED))
            case SimulationState.STOPPED:
                wx.PostEvent(self._window, WGPUSimLoopEvent(WGPUSimLoopEventMsg.SIMULATION_STOPPED))

    def end(self) -> None:
        """
        Attempt to gracefully shut down the simulation.
        """
        self._sim_current_state = SimulationState.ENDED
        if hasattr(self, "_once_per_second_timer"):
            self._once_per_second_timer.cancel()
        if hasattr(self, "_sim_thread"):
            self._sim_thread.join()

    def start(self, context: SimulationContext) -> None:
        """Create a thread for updating the simulation."""
        # Note: A daemonic thread cannot be "joined" by another thread.
        # They are destroyed when the main thread is terminated.
        self._sim_thread = Thread(
            name="simulation-loop", target=self._loop, args=(context,), daemon=True
        )
        self._sim_thread.start()

    def _loop(self, context: SimulationContext):
        """The thread callback that processes a simulation tick.

        Using the definitions in agents_playground.core.time_utilities, this ensures
        a fixed time for scheduled events to be ran. Rendering is handled automatically
        via DataPyUI (note: VSync is turned on when the Viewport is created.)

        For 60 FPS, TIME_PER_UPDATE is 5.556 ms.
        """
        self._once_per_second_timer = RecurringAction(
            interval=MONITOR_FREQUENCY,
            function=self._once_per_second,
            args=(context,)
        )
        self._once_per_second_timer.start()
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

    @log_call
    def _once_per_second(self, context: SimulationContext) -> None:
        """
        Per its name, this method is invoked once a second.
        """
        context.stats.per_frame_samples = collected_duration_metrics().aggregate()
        wx.PostEvent(self._window, WGPUSimLoopEvent(WGPUSimLoopEventMsg.UPDATE_FPS))
        collected_duration_metrics().reset_sample_window_counters()

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
        self._request_render(context.scene)

    @sample_duration(
        sample_name="waiting-until-next-frame", count=FRAME_SAMPLING_SERIES_LENGTH
    )
    def _wait_until_next_check(self) -> None:
        self._waiter.wait(self._sim_stopped_check_time)

    @sample_duration(sample_name="running-tasks", count=FRAME_SAMPLING_SERIES_LENGTH)
    def _process_per_frame_tasks(self) -> None:
        self._task_scheduler.queue_holding_tasks()
        self._task_scheduler.consume()

    def _request_render(self, scene: Scene) -> None:
        wx.PostEvent(self._window, WGPUSimLoopEvent(WGPUSimLoopEventMsg.REDRAW))

    def _utility_samples_collected(self, **kwargs) -> None:
        """
        This hook copies the samples to the simulation context and use the update method 
        on the Simulation to grab the samples.
        """
        context = kwargs["frame_context"]
        context.stats.per_frame_samples = collected_duration_metrics().aggregate()
        wx.PostEvent(self._window, WGPUSimLoopEvent(WGPUSimLoopEventMsg.UTILITY_SAMPLES_COLLECTED))
        self._utility_sampler.reset()

    def _notify_monitor_usage(self) -> None:
        wx.PostEvent(self._window, WGPUSimLoopEvent(WGPUSimLoopEventMsg.TIME_TO_MONITOR_HARDWARE))
