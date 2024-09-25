from collections.abc import Sequence
from datetime import datetime
from typing import NamedTuple

from graphviz import Digraph

from agents_playground.core.time_utilities import TimeUtilities
from agents_playground.tasks.graph.task_graph_snapshot_sampler import (
    TaskGraphSnapshotSampler,
)
from agents_playground.tasks.graph.types import TaskGraphLike, TaskGraphPhase
from agents_playground.tasks.types import TaskDef, TaskLike, TaskStatus


class MinimalGraphVizNode(NamedTuple):
    name: str
    type: str  # Resource | Task
    # The color name as specified at https://graphviz.org/doc/info/colors.html
    color: str


class MinimalGraphVizEdge(NamedTuple):
    """
    Represents a directed edge in a GraphViz graph.
    This points to That
    this -> that
    """

    this: str
    that: str
    label: str


_TASK_COLOR: str = "lightblue2"
_RESOURCE_COLOR: str = "firebrick2"


class MinimalSnapshotSampler(TaskGraphSnapshotSampler):
    def __init__(self) -> None:
        super().__init__()

    def _take_snapshot(
        self,
        task_graph: TaskGraphLike,
        phase: TaskGraphPhase,
        filter: Sequence[TaskStatus],
    ) -> Digraph:
        graph_nodes, graph_edges = self._preprocess_graph(task_graph, filter)
        return self._build_graph_viz(phase, graph_nodes, graph_edges)

    def _preprocess_graph(
        self, task_graph: TaskGraphLike, filter: Sequence[TaskStatus]
    ) -> tuple[set[MinimalGraphVizNode], set[MinimalGraphVizEdge]]:
        # Preprocess the nodes and edges to display.
        task: TaskLike
        graph_nodes: set[MinimalGraphVizNode] = set()
        graph_edges: set[MinimalGraphVizEdge] = set()
        for task in task_graph.task_tracker.filter_by_status(filter):
            task_def: TaskDef = task_graph.task_registry[task.task_name]
            graph_nodes.add(MinimalGraphVizNode(task.task_name, "Task", _TASK_COLOR))

            for required_task in task_def.required_before_tasks:
                graph_nodes.add(MinimalGraphVizNode(required_task, "Task", _TASK_COLOR))
                graph_edges.add(
                    MinimalGraphVizEdge(
                        required_task, task.task_name, "required before"
                    )
                )

            for required_input in task_def.inputs:
                graph_nodes.add(
                    MinimalGraphVizNode(required_input, "Resource", _RESOURCE_COLOR)
                )
                graph_edges.add(
                    MinimalGraphVizEdge(required_input, task.task_name, "input to")
                )

            for required_output in task_def.outputs:
                graph_nodes.add(
                    MinimalGraphVizNode(required_output, "Resource", _RESOURCE_COLOR)
                )
                graph_edges.add(
                    MinimalGraphVizEdge(task.task_name, required_output, "outputs")
                )
        return (graph_nodes, graph_edges)

    def _build_graph_viz(
        self,
        phase: TaskGraphPhase,
        graph_nodes: set[MinimalGraphVizNode],
        graph_edges: set[MinimalGraphVizEdge],
    ) -> Digraph:
        viz_time: datetime = TimeUtilities.clock_time_now()
        graph_viz = Digraph(
            name="graph_viz",
            filename=f"task_graph-{TimeUtilities.display_time(viz_time)}-{phase}.gv",
            engine="dot",
            graph_attr={
                "label": f"Task Graph {phase} {TimeUtilities.display_time(viz_time, format='%Y-%m-%d %H:%M:%S')}"
            },
        )

        # Build a graph that represents the task graph.
        # Note that the subgraphs must start with the prefix "cluster".
        with graph_viz.subgraph(name="cluster_task_graph", node_attr={"style": "filled", "shape": "rectangle"}, graph_attr={"label": "Task Graph", "color": "gray19"}) as graph:  # type: ignore
            # Add all tasks and resources as nodes
            for graph_node in graph_nodes:
                graph.node(name=graph_node.name, fillcolor=graph_node.color)

            # Add all edges. The direction of edges is this is before that  (this -> that).
            for graph_edge in graph_edges:
                graph.edge(
                    tail_name=graph_edge.this,
                    head_name=graph_edge.that,
                    label=graph_edge.label,
                )

        # Build a Legend
        with graph_viz.subgraph(name="cluster_legend", node_attr={"style": "filled", "shape": "rectangle"}, graph_attr={"label": "Legend", "color": "gray19"}) as legend:  # type: ignore
            legend.node(name="Task", fillcolor=_TASK_COLOR)
            legend.node(name="Resource", fillcolor=_RESOURCE_COLOR)

        return graph_viz