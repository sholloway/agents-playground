import logging
import os
import sys
import wx
from wgpu.gui.wx import WgpuWidget

from agents_playground.app.options import application_options
from agents_playground.cameras.camera import Camera
from agents_playground.core.privileged import require_root
from agents_playground.core.webgpu_sim_loop import (
    WGPU_SIM_LOOP_EVENT,
    WGPUSimLoopEvent,
    WGPUSimLoopEventMsg,
)
from agents_playground.fp import Maybe, Something
from agents_playground.loaders.tasks_loader import SimulationTasksLoader
from agents_playground.spatial.vector.vector import Vector
from agents_playground.sys.logger import (
    LoggingLevel,
    get_default_logger,
    log_call,
    log_table,
)
from agents_playground.tasks.graph.detailed_task_graph_sampler import (
    DetailedTaskGraphSampler,
)
from agents_playground.tasks.graph.minimal_task_graph_sampler import (
    MinimalSnapshotSampler,
)
from agents_playground.tasks.graph.task_graph import TaskGraph
from agents_playground.tasks.graph.task_graph_snapshot_sampler import (
    TaskGraphSnapshotSampler,
)
from agents_playground.tasks.graph.types import (
    TaskGraphError,
    TaskGraphLike,
    TaskGraphPhase,
)
from agents_playground.tasks.types import SimulationTasks, TaskStatus

# This import loads all of the predefined tasks into the task registry.
from agents_playground.tasks.predefined.bootstrap import *

logger: logging.Logger = get_default_logger()


def log_camera(camera: Camera) -> None:
    """Log the camera orientation as a table."""
    facing: Vector = camera.facing.unwrap()
    right: Vector = camera.right.unwrap()
    up: Vector = camera.up.unwrap()

    header = ["", "X", "Y", "Z"]
    data = []
    data.append(["Target", camera.target.i, camera.target.j, camera.target.k])
    data.append(
        ["Camera Location", camera.position.i, camera.position.j, camera.position.k]
    )
    data.append(["Facing", facing.i, facing.j, facing.k])
    data.append(["Right", right.i, right.j, right.k])
    data.append(["Up", up.i, up.j, up.k])
    log_table(
        rows=data, message="Camera Updated", header=header, level=LoggingLevel.INFO
    )


class KeyEventHandler:
    """
    Handle when a user presses a button on their keyboard.
    """

    @log_call()
    def __init__(self, task_graph: TaskGraphLike) -> None:
        self._task_graph = task_graph

    def handle_key_pressed(self, event: wx.Event) -> None:
        maybe_scene: Maybe[TaskResource] = self._task_graph.get_resource("scene")
        if not maybe_scene.is_something():
            return

        task_resource: TaskResource = maybe_scene.unwrap()
        scene: Scene = task_resource.resource.unwrap()

        """
        ASCII key codes use a single bit position between upper and lower case so
        x | 0x20 will force any key to be lower case.

        For example:
        A is 65 or 1000001
        32 -> 0x20 -> 100000
        1000001 | 100000 -> 1100001 -> 97 -> 'a'
        """
        key_str = chr(event.GetKeyCode() | 0x20)  # type: ignore

        # A/D are -/+ On on the X-Axis
        # S/W are -/+ On on the Z-Axis
        match key_str:  # type: ignore
            case "a":
                scene.camera.position.i -= 1
                scene.camera.update()
                log_camera(scene.camera)
            case "d":
                scene.camera.position.i += 1
                scene.camera.update()
                log_camera(scene.camera)
            case "w":
                scene.camera.position.k += 1
                scene.camera.update()
                log_camera(scene.camera)
            case "s":
                scene.camera.position.k -= 1
                scene.camera.update()
                log_camera(scene.camera)
            case "f":
                log_camera(scene.camera)
            case _:
                pass


class SimLoopEventHandler:
    @log_call()
    def __init__(self, task_graph: TaskGraphLike) -> None:
        self._task_graph = task_graph

    def handle_sim_loop_event(self, event: WGPUSimLoopEvent) -> None:
        maybe_canvas: Maybe[TaskResource] = self._task_graph.get_resource("canvas")
        if not maybe_canvas.is_something():
            return

        task_resource: TaskResource = maybe_canvas.unwrap()
        canvas: WgpuWidget = task_resource.resource.unwrap()

        match event.msg:
            case WGPUSimLoopEventMsg.REDRAW:
                canvas.request_draw()
            case WGPUSimLoopEventMsg.UPDATE_FPS:
                pass
            case WGPUSimLoopEventMsg.UTILITY_SAMPLES_COLLECTED:
                pass
            case WGPUSimLoopEventMsg.TIME_TO_MONITOR_HARDWARE:
                pass
            case WGPUSimLoopEventMsg.SIMULATION_STARTED:
                pass
            case WGPUSimLoopEventMsg.SIMULATION_STOPPED:
                pass
            case _:
                get_default_logger().error(
                    f"WGPUSimLoopEvent: Got a message I can't handle. {event.msg}"
                )


EARLY_START_ERROR_MSG = "Attempted to launch the simulation before it was ready."
FAILED_TO_START_PERF_MON = "Failed to start the performance monitor."


class TaskDrivenSimulation:
    @log_call()
    def __init__(self, canvas: WgpuWidget, scene_file: str, project_path: str) -> None:
        self._scene_file = scene_file
        self._project_path = project_path
        self._capture_task_graph_snapshot = application_options()["viz_task_graph"]
        self._task_graph: TaskGraphLike = TaskGraph()
        self._snapshot_sampler: TaskGraphSnapshotSampler = DetailedTaskGraphSampler()
        self._key_event_handler = KeyEventHandler(self._task_graph)
        self._sim_loop_event_handler = SimLoopEventHandler(self._task_graph)
        self._canvas = canvas

        # _sim_tasks is set in the load_tasks_file method.
        self._sim_tasks: SimulationTasks

        # self._initial_tasks: list[str] = [
        #     "load_scene",
        #     "load_landscape_mesh",
        #     "initialize_graphics_pipeline",
        #     "prepare_landscape_renderer",
        #     "create_simulation_context",
        #     # "start_performance_monitor",
        #     "start_simulation_loop",
        # ]
        # self._shutdown_tasks: list[str] = [
        #     "end_simulation",
        #     # "end_performance_monitor",
        # ]

    @log_call()
    def bind_event_listeners(self, frame: wx.Panel) -> None:
        """
        Given a panel, binds event listeners.
        """
        frame.Bind(wx.EVT_CHAR, self._key_event_handler.handle_key_pressed)
        frame.Connect(
            -1,
            -1,
            WGPU_SIM_LOOP_EVENT,
            self._sim_loop_event_handler.handle_sim_loop_event,
        )

    @log_call("Initializing the simulation.")
    def launch(self) -> None:
        try:
            self._sim_tasks = self._load_tasks_file()
            self._task_graph.provision_resource(
                "scene_file_path", instance=self._scene_file
            )

            self._task_graph.provision_resource("canvas", instance=self._canvas)

            for task_name in self._sim_tasks.initial_tasks:
                self._task_graph.provision_task(task_name)

            if self._capture_task_graph_snapshot:
                self._snapshot_sampler.snapshot(
                    task_graph=self._task_graph,
                    phase=TaskGraphPhase.INITIALIZATION,
                    filter=(TaskStatus.INITIALIZED,),
                )

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

    @log_call()
    def shutdown(self) -> None:
        logger.info("TaskDrivenSimulation: It's closing time!")
        for task_name in self._sim_tasks.shutdown_tasks:
            self._task_graph.provision_task(task_name)

        if self._capture_task_graph_snapshot:
            self._snapshot_sampler.snapshot(
                task_graph=self._task_graph,
                phase=TaskGraphPhase.SHUTDOWN,
                filter=(TaskStatus.INITIALIZED,),
            )

        self._task_graph.run_until_done()
        self._task_graph.clear()
        logger.info(f"Completed Shutdown Tasks")

    @log_call("Attempting to load the simulation's task file.")
    def _load_tasks_file(self) -> SimulationTasks:
        """
        Attempts to load the tasks.json file in the Simulation project.
        If none is found, then the default tasks file is loaded.
        """
        loader = SimulationTasksLoader()
        sim_tasks_file_path: str = os.path.join(self._project_path, "tasks.json")
        sim_tasks: SimulationTasks
        if os.path.exists(sim_tasks_file_path) and os.path.isfile(sim_tasks_file_path):
            sim_tasks = loader.load(sim_tasks_file_path)
        else:
            logger.info(
                "No tasks file was found. Attempting to load the default tasks file."
            )
            default_tasks_file_rel_path = (
                "agents_playground/tasks/file/default_tasks.json"
            )
            tasks_path = os.path.join(Path.cwd(), default_tasks_file_rel_path)
            sim_tasks = loader.load(tasks_path)
        return sim_tasks

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
