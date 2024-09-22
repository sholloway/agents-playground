import logging
import os
import sys
import wx
from wgpu.gui.wx import WgpuWidget

from agents_playground.core.performance_monitor import PerformanceMonitor
from agents_playground.core.privileged import require_root
from agents_playground.core.webgpu_sim_loop import (
    WGPU_SIM_LOOP_EVENT,
    WGPUSimLoop,
    WGPUSimLoopEvent,
)
from agents_playground.fp import Maybe, Nothing, Something
from agents_playground.gpu.renderers.gpu_renderer import GPURenderer
from agents_playground.simulation.context import SimulationContext
from agents_playground.simulation.sim_state import SimulationState
from agents_playground.simulation.types import SimulationError
from agents_playground.sys.logger import get_default_logger, log_call
from agents_playground.tasks.graph import TaskGraph, TaskGraphError, TaskGraphPhase

from agents_playground.tasks.predefined.bootstrap import *
from agents_playground.tasks.types import TaskStatus

logger: logging.Logger = get_default_logger()


class KeyEventHandler:
    """
    Handle when a user presses a button on their keyboard.
    """

    @log_call
    def __init__(self) -> None:
        pass

    def handle_key_pressed(self, event: wx.Event) -> None:
        """
        ASCII key codes use a single bit position between upper and lower case so
        x | 0x20 will force any key to be lower case.

        For example:
        A is 65 or 1000001
        32 -> 0x20 -> 100000
        1000001 | 100000 -> 1100001 -> 97 -> 'a'
        """
        key_str = chr(event.GetKeyCode() | 0x20)  # type: ignore
        logger.info(f"Key pressed: {key_str}")


class SimLoopEventHandler:
    @log_call
    def __init__(self) -> None:
        pass

    def handle_sim_loop_event(self, event: WGPUSimLoopEvent) -> None:
        pass
        # TODO: Implement responding to the the events sent by the SimLoop.
        # logger.info(f"The simulation received the event {event.msg} from the SimLoop")


EARLY_START_ERROR_MSG = "Attempted to launch the simulation before it was ready."
FAILED_TO_START_PERF_MON = "Failed to start the performance monitor."


class TaskDrivenSimulation:
    @log_call
    def __init__(
        self,
        canvas: WgpuWidget,
        scene_file: str,
        capture_task_graph_snapshot: bool = False,
    ) -> None:
        self._scene_file = scene_file
        self._capture_task_graph_snapshot = capture_task_graph_snapshot
        self._task_graph = TaskGraph()
        self._canvas = canvas
        self._initial_tasks: list[str] = [
            "load_scene",
            "load_landscape_mesh",
            "initialize_graphics_pipeline",
            "prepare_landscape_renderer",
            "create_simulation_context",
            # "start_performance_monitor",
            "start_simulation_loop",
        ]
        self._shutdown_tasks: list[str] = [
            "end_simulation",
            # "end_performance_monitor",
        ]

        # self._perf_monitor: Maybe[PerformanceMonitor] = Something(PerformanceMonitor())

    @log_call
    def bind_event_listeners(self, frame: wx.Panel) -> None:
        """
        Given a panel, binds event listeners.
        """
        key_event_handler = KeyEventHandler()
        frame.Bind(wx.EVT_CHAR, key_event_handler.handle_key_pressed)

        sim_loop_event_handler = SimLoopEventHandler()
        frame.Connect(
            -1, -1, WGPU_SIM_LOOP_EVENT, sim_loop_event_handler.handle_sim_loop_event
        )

    @log_call
    def launch(self) -> None:
        # TODO: Find a cleaner way to provision tasks.
        # Perhaps inject the task graph an only allow things like scene_path and _sim_context_builder
        # to be available as resources?
        #  Set the initial inputs
        try:
            self._task_graph.provision_resource(
                "scene_file_path", instance=self._scene_file
            )

            self._task_graph.provision_resource("canvas", instance=self._canvas)

            for task_name in self._initial_tasks:
                self._task_graph.provision_task(task_name)

            if self._capture_task_graph_snapshot:
                self._task_graph.visualize(phase=TaskGraphPhase.INITIALIZATION)

            self._task_graph.run_until_done()
            tasks_complete = self._task_graph.tasks_with_status((TaskStatus.COMPLETE,))
            logger.info(f"Completed Initialization Tasks: {len(tasks_complete)}")
        except TaskGraphError as e:
            logger.critical(
                "An error occurred while trying to initialize the simulation."
            )
            logger.critical(e)
            logger.critical("Attempting to release the task graph and stopping.")
            self._task_graph.clear()
            sys.exit("Attempting to stop because of a task graph error.")

    @log_call
    def shutdown(self) -> None:
        logger.info("TaskDrivenSimulation: It's closing time!")
        for task_name in self._shutdown_tasks:
            self._task_graph.provision_task(task_name)

        if self._capture_task_graph_snapshot:
            self._task_graph.visualize(phase=TaskGraphPhase.SHUTDOWN)

        self._task_graph.run_until_done()
        self._task_graph.clear()
        logger.info(f"Completed Shutdown Tasks")

    # TODO: Make this a task.
    # Make a version of require_root that works with tasks.
    # I'd like to have a task decorator that is conditional.
    # For Example:
    # @task(require_root=True)
    # is there a way to make that more generic?
    #   @task(run_only_if=runtime_check_method)
    #   @task(run_only_if=running_as_root)
    @require_root
    def _start_perf_monitor(self):
        get_default_logger().info("Starting the Performance Monitor")
        try:
            if self._perf_monitor.is_something():
                self._perf_receive_pipe = Something(
                    self._perf_monitor.unwrap().start(os.getpid())
                )
        except Exception as e:
            logger.error(FAILED_TO_START_PERF_MON)
            logger.error(e, exc_info=True)
