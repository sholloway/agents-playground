import logging
import os
import wx
import wgpu
import wgpu.backends.wgpu_native
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
from agents_playground.loaders.scene_loader import SceneLoader
from agents_playground.simulation.context import SimulationContext, UniformRegistry
from agents_playground.simulation.sim_state import SimulationState
from agents_playground.simulation.simulation_context_builder import (
    SimulationContextBuilder,
)
from agents_playground.simulation.types import SimulationError
from agents_playground.spatial.mesh import MeshRegistry
from agents_playground.sys.logger import get_default_logger, log_call
from agents_playground.tasks.graph import TaskGraph

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
        logger.info(f"The simulation received the event {event.msg} from the SimLoop")


class TaskDrivenRenderer:
    @log_call
    def __init__(
        self, context: SimulationContext, renderers: dict[str, GPURenderer]
    ) -> None:
        self._context = context
        self._renderers = renderers

    @log_call
    def render(self) -> None:
        pass


EARLY_START_ERROR_MSG = "Attempted to launch the simulation before it was ready."
FAILED_TO_START_PERF_MON = "Failed to start the performance monitor."


class TaskDrivenSimulation:
    @log_call
    def __init__(self, canvas: WgpuWidget, scene_file: str) -> None:
        self._scene_file = scene_file
        self._task_graph = TaskGraph()
        self._canvas = canvas
        self._sim_loop: WGPUSimLoop = WGPUSimLoop(window=canvas)
        self._perf_monitor: Maybe[PerformanceMonitor] = Something(PerformanceMonitor())

        # Set by the self._sim_context_builder in the launch method.
        self._sim_context: SimulationContext

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
        self._task_graph.provision_resource(
            "scene_file_path", instance=self._scene_file
        )

        self._task_graph.provision_resource("canvas", instance=self._canvas)

        # self._task_graph.provision_resource(
        #     "sim_context_builder",
        #     instance=SimulationContextBuilder(
        #         canvas=self._canvas,
        #         mesh_registry=MeshRegistry(),
        #         renderers={},
        #         uniforms=UniformRegistry(),
        #         extensions={},
        #     ),
        # )

        initial_tasks: list[str] = [
            "load_scene",
            "load_landscape_mesh",
            "initialize_graphics_pipeline",
            "prepare_landscape_renderer",
            "create_simulation_context",
            "start_simulation_loop",
        ]

        for task_name in initial_tasks:
            self._task_graph.provision_task(task_name)

        self._task_graph.run_until_done()

        logger.info(
            f"Completed Tasks: {self._task_graph.tasks_with_status((TaskStatus.COMPLETE,))}"
        )

        # Start the sim loop.
        # TODO: Put the below into the task start_simulation_loop.
        if self._sim_context_builder.is_ready():
            self._sim_context = self._sim_context_builder.create_context()
            task_renderer = TaskDrivenRenderer(
                self._sim_context, self._sim_context_builder.renderers
            )
            self._sim_context.canvas.request_draw(task_renderer.render)
            self._sim_loop.simulation_state = SimulationState.RUNNING
            self._start_perf_monitor()
            self._sim_loop.start(self._sim_context)
        else:
            raise SimulationError(EARLY_START_ERROR_MSG)

    @log_call
    def shutdown(self) -> None:
        # 1. Stop the simulation thread and task scheduler.
        self.simulation_state = SimulationState.ENDED
        # self._task_scheduler.stop()

        # 2. Stop the performance monitor process if it's going.
        if self._perf_monitor.is_something():
            self._perf_monitor.unwrap().stop()
            self._perf_monitor = Nothing()

        # 3. Kill the simulation thread.
        self._sim_loop.end()

        # 4. Remove the reference to the simulations key components.
        # self._task_scheduler.purge()
        # self._pre_sim_task_scheduler.purge()

        # 6. Purge the Context Object
        if hasattr(self, "_sim_context"):
            self._sim_context.purge()

        # 7. Purge any extensions defined by the Simulation's Project
        # TODO: Re-introduce simulation extensions.
        # simulation_extensions().reset()

    @require_root
    def _start_perf_monitor(self):
        try:
            if self._perf_monitor.is_something():
                self._perf_receive_pipe = Something(
                    self._perf_monitor.unwrap().start(os.getpid())
                )
        except Exception as e:
            logger.error(FAILED_TO_START_PERF_MON)
            logger.error(e, exc_info=True)
