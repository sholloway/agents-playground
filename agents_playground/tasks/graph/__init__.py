from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
import logging
import os
from pathlib import Path
from typing import Any, NamedTuple

import graphviz

from agents_playground.core.task_scheduler import TaskId
from agents_playground.core.time_utilities import TimeUtilities
from agents_playground.sys.logger import get_default_logger, log_call
from agents_playground.tasks.registry import TaskRegistry, global_task_registry
from agents_playground.tasks.resources import (
    TaskResourceRegistry,
    TaskResourceTracker,
    global_task_resource_registry,
)
from agents_playground.tasks.runners.single_threaded_task_runner import (
    SingleThreadedTaskRunner,
)
from agents_playground.tasks.tracker import TaskTracker
from agents_playground.tasks.types import (
    ResourceName,
    TaskDef,
    TaskErrorMsg,
    TaskLike,
    TaskName,
    TaskResource,
    TaskRunResult,
    TaskRunnerLike,
    TaskStatus,
)

logger: logging.Logger = get_default_logger()

class TaskGraphPhase(StrEnum):
    INITIALIZATION = "INITIALIZATION"
    FRAME_DRAW = "FRAME_DRAW"
    SHUTDOWN = "SHUTDOWN"
    
class TaskGraphError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class GraphVizNode(NamedTuple):
    name: str
    type: str  # Resource | Task
    color: (
        str  # The color name as specified at https://graphviz.org/doc/info/colors.html
    )


class GraphVizEdge(NamedTuple):
    """
    Represents a directed edge in a GraphViz graph.
    This points to That
    this -> that
    """

    this: str
    that: str
    label: str 


TASK_COLOR: str = "lightblue2"
RESOURCE_COLOR: str = "firebrick2"


# TODO: Simplify the TaskGraph API. I don't want to do things like tg.resource_tracker["my_resource"].
# It should be closer to something like:
#  - tg.allocate_resource("my_resource.", instance=...)
#  - tg.get_resource("my_resource.") -> ResourceType
#  - tg.unwrap_resource("my_resource") -> Any
#  - tg.unwrap_resources(tag="resources") -> dict[name, Any]
@dataclass
class TaskGraph:
    """
    Represents a collection of interdependent tasks. Loops are not permitted.
    """

    task_registry: TaskRegistry = field(default_factory=lambda: global_task_registry())

    resource_registry: TaskResourceRegistry = field(
        default_factory=lambda: global_task_resource_registry()
    )

    task_tracker: TaskTracker = field(default_factory=lambda: TaskTracker())

    resource_tracker: TaskResourceTracker = field(
        default_factory=lambda: TaskResourceTracker()
    )

    task_runner: TaskRunnerLike = field(
        default_factory=lambda: SingleThreadedTaskRunner()
    )

    def provision_task(self, name: TaskName, *args, **kwargs) -> TaskLike:
        """Provisions a task and adds it to the tracker.

        Args:
        - name: The name of the task to provision.
        - args: The positional arguments to pass to the TaskLike.
        - kwargs: The named arguments to pass to the TaskLike.

        Returns:
        The instance of the task that was provisioned.
        """
        kwargs["task_graph"] = self  # inject the task_graph.
        try:
            task = self.task_registry.provision(name, *args, **kwargs)
            self.task_tracker.track(task)
        except Exception as e:
            logger.error(
                f"An error occurred while attempting to provision an instance of task {name}."
            )
            logger.exception(e)
            raise TaskGraphError(f"Failed to provision task {name}")
        return task

    def provision_resource(
        self, name: ResourceName, instance: Any | None = None, *args, **kwargs
    ) -> TaskResource:
        resource: TaskResource = self.resource_registry.provision(
            name, instance, *args, **kwargs
        )
        self.resource_tracker.track(resource)
        return resource

    def clear(self) -> None:
        """
        Deletes all provisioned resources and tasks and removes all registrations.
        Basically, resets the task graph to be empty.
        """
        self.resource_tracker.clear()
        self.task_tracker.clear()
        self.resource_registry.clear()
        self.task_registry.clear()

    def tasks_with_status(self, filter: Sequence[TaskStatus]) -> tuple[TaskLike, ...]:
        return self.task_tracker.filter_by_status(filter)

    def check_if_blocked_tasks_are_ready(self) -> None:
        """
        Inspect all provisioned tasks with a status of INITIALIZED or BLOCKED to see if
        they're ready to run. If they are, then update the status to READY_FOR_ASSIGNMENT.

        Effects:
        - Tasks that are INITIALIZED but blocked have their status set to BLOCKED.
        - Tasks that are INITIALIZED or BLOCKED have their status set to READY_FOR_ASSIGNMENT.
        """
        status_filter = (TaskStatus.INITIALIZED, TaskStatus.BLOCKED)
        tasks_to_check: tuple[TaskLike, ...] = self.task_tracker.filter_by_status(
            status_filter
        )

        for task in tasks_to_check:
            # Get the task's definition.
            task_def: TaskDef = self.task_registry[task.task_name]

            # If the task has a conditional requirement, run that
            # to determine it the task is permitted to run.
            # Skip the rest of the checks if the bound run_if
            # function returns False.
            if not task_def.run_if():
                # Tasks that fail their run_if check will not be run
                # so mark it as complete.
                task.status = TaskStatus.COMPLETE
                logger.info(
                    f"The task {task.task_name} was not run because its run_if check {task_def.run_if.__qualname__} evaluated to False."
                )
                continue

            # Get the provisioned before tasks.
            before_tasks: tuple[TaskLike, ...] = self.task_tracker.collect_by_name(
                task_def.required_before_tasks
            )

            # Did all the before tasks run?
            all_before_tasks_are_complete = all(
                [task.status == TaskStatus.COMPLETE for task in before_tasks]
            )

            # Check that the required inputs have been allocated.
            allocated_inputs = [
                required_input in self.resource_tracker
                for required_input in task_def.inputs
            ]
            all_inputs_are_allocated = all(allocated_inputs)

            if all_before_tasks_are_complete and all_inputs_are_allocated:
                task.status = TaskStatus.READY_FOR_ASSIGNMENT
            else:
                task.status = TaskStatus.BLOCKED

    def run_all_ready_tasks(self) -> None:
        """Run all tasks that have their status set to READY_FOR_ASSIGNMENT."""
        ready_tasks = self.task_tracker.filter_by_status(
            (TaskStatus.READY_FOR_ASSIGNMENT,)
        )
        self.task_runner.run(ready_tasks, self._handle_task_done)

    def run_until_done(self) -> None:
        """
        Continue to run tasks until they're all complete or the graph is blocked.

        Effects:
        - Calls check_if_blocked_tasks_are_ready to prompt tasks into ready status.
        - Runs tasks and pushes them into completed status.
        """
        still_work_to_do: bool = True
        while still_work_to_do:
            self.run_all_ready_tasks()
            self.check_if_blocked_tasks_are_ready()
            still_work_to_do = self._work_to_do()

    @log_call
    def snapshot(self, phase: TaskGraphPhase, filter: Sequence[TaskStatus]) -> None:
        """
        Draw the task graph via graphviz. This is intended to help with debugging task graphs.

        Args:
            - label: A label to apply to the task graph.
        """
        viz_time: datetime = TimeUtilities.clock_time_now()
        graph_viz = graphviz.Digraph(
            name="graph_viz",
            filename=f"task_graph-{TimeUtilities.display_time(viz_time)}-{phase}.gv",
            engine="dot",
            graph_attr={"label":f"Task Graph {phase} {TimeUtilities.display_time(viz_time, format="%Y-%m-%d %H:%M:%S")}"},
        )

        # Preprocess the nodes and edges to display.
        task: TaskLike
        graph_nodes: set[GraphVizNode] = set()
        graph_edges: set[GraphVizEdge] = set()
        for task in self.task_tracker.filter_by_status(filter):
            task_def: TaskDef = self.task_registry[task.task_name]
            graph_nodes.add(GraphVizNode(task.task_name, "Task", TASK_COLOR))

            for required_task in task_def.required_before_tasks:
                graph_nodes.add(GraphVizNode(required_task, "Task", TASK_COLOR))
                graph_edges.add(GraphVizEdge(required_task, task.task_name, "required before"))

            for required_input in task_def.inputs:
                graph_nodes.add(
                    GraphVizNode(required_input, "Resource", RESOURCE_COLOR)
                )
                graph_edges.add(GraphVizEdge(required_input, task.task_name, "input to"))

            for required_output in task_def.outputs:
                graph_nodes.add(
                    GraphVizNode(required_output, "Resource", RESOURCE_COLOR)
                )
                graph_edges.add(GraphVizEdge(task.task_name, required_output, "outputs"))

        # Build a graph that represents the task graph.
        # Note that the subgraphs must start with the prefix "cluster".
        with graph_viz.subgraph(name="cluster_task_graph", node_attr={"style": "filled", "shape": "rectangle"}, graph_attr={"label": "Task Graph", "color": "gray19"}) as graph:  # type: ignore
            # Add all tasks and resources as nodes
            for graph_node in graph_nodes:
                graph.node(name=graph_node.name, fillcolor=graph_node.color)

            # Add all edges. The direction of edges is this is before that  (this -> that).
            for graph_edge in graph_edges:
                graph.edge(tail_name=graph_edge.this, head_name=graph_edge.that, label=graph_edge.label)

        # Build a Legend
        with graph_viz.subgraph(name="cluster_legend", node_attr={"style": "filled", "shape": "rectangle"}, graph_attr={"label": "Legend", "color": "gray19"}) as legend:  # type: ignore
            legend.node(name="Task", fillcolor=TASK_COLOR)
            legend.node(name="Resource", fillcolor=RESOURCE_COLOR)

        # Visualize it!
        # Save the graphviz file, render it, and open a viewer.
        task_graph_debug_dir: str = os.path.join(Path.cwd(), "task_graph_debug_files")
        if not os.path.isdir(task_graph_debug_dir):
            os.mkdir(task_graph_debug_dir)

        graph_viz.render(directory=task_graph_debug_dir, cleanup=True)

    def _work_to_do(self) -> bool:
        """
        Returns true if there are any tasks with a status of READY_FOR_ASSIGNMENT.
        """
        return (
            len(self.task_tracker.filter_by_status((TaskStatus.READY_FOR_ASSIGNMENT,)))
            > 0
        )

    def _handle_task_done(
        self, taskId: TaskId, result: TaskRunResult, error_msg: TaskErrorMsg
    ) -> None:
        if result == TaskRunResult.SUCCESS:
            self.task_tracker[taskId].status = TaskStatus.COMPLETE
        else:
            failed_task = self.task_tracker[taskId]
            logger.error(f"Task {failed_task.task_name} failed to run.\n{error_msg}")
