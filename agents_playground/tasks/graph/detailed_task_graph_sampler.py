from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import NamedTuple

from graphviz import Digraph
from agents_playground.core.time_utilities import TimeUtilities
from agents_playground.fp import Maybe
from agents_playground.tasks.graph.task_graph_snapshot_sampler import (
    TaskGraphSnapshotSampler,
)
from agents_playground.tasks.graph.types import TaskGraphPhase
from agents_playground.tasks.types import (
    TaskDef,
    TaskGraphLike,
    TaskLike,
    TaskResource,
    TaskStatus,
)


@dataclass(unsafe_hash=True)
class DetailedGraphVizNode:
    name: str
    id: int
    status: str
    type: str  # Resource | Task
    # The color name as specified at https://graphviz.org/doc/info/colors.html
    color: str

    def to_table(self) -> str:
        return f"""<
            <table border="0" cellborder="1" cellspacing="0" cellpadding="3" bgcolor="white">
                <tr>
                    <td bgcolor="{self.color}" align="center" colspan="1">
                        <font color="white">{self.name}</font>
                    </td>
                </tr>
                <tr>
                    <td align="left">ID: {self.id}</td>
                </tr>
                <tr>
                    <td align="left">Status: {self.status}</td>
                </tr>
            </table>
        >"""


class DetailedGraphVizEdge(NamedTuple):
    """
    Represents a directed edge in a GraphViz graph.
    This points to That
    this -> that
    """

    this: str
    that: str
    label: str


_BACKGROUND_COLOR: str = "gray12"
_TASK_COLOR: str = "lightblue2"
_RESOURCE_COLOR: str = "firebrick2"
_EDGE_COLOR: str = "deepskyblue"


class DetailedTaskGraphSampler(TaskGraphSnapshotSampler):
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
    ) -> tuple[set[DetailedGraphVizNode], set[DetailedGraphVizEdge]]:
        # Preprocess the nodes and edges to display.
        task: TaskLike
        graph_nodes: set[DetailedGraphVizNode] = set()
        graph_edges: set[DetailedGraphVizEdge] = set()
        for task in task_graph.tasks_with_status(filter):
            # Add this task as a node.
            task_def: TaskDef = task_graph.task_def(task.task_name)
            graph_nodes.add(
                DetailedGraphVizNode(
                    task.task_name, task.task_id, task.status.name, "Task", _TASK_COLOR
                )
            )

            # Add every required task.
            for required_task_name in task_def.required_before_tasks:
                required_task: TaskLike = task_graph.task(required_task_name)
                graph_nodes.add(
                    DetailedGraphVizNode(
                        required_task.task_name,
                        required_task.task_id,
                        required_task.status.name,
                        "Task",
                        _TASK_COLOR,
                    )
                )
                graph_edges.add(
                    DetailedGraphVizEdge(
                        required_task_name, task.task_name, "required before"
                    )
                )

            # Process every input that the task has.
            for required_input_name in task_def.inputs:
                possible_input: Maybe[TaskResource] = task_graph.resource(
                    required_input_name
                )
                if possible_input.is_something():
                    required_input: TaskResource = possible_input.unwrap()
                    input_node = DetailedGraphVizNode(
                        required_input.resource_name,
                        required_input.resource_id,
                        required_input.resource_status.name,
                        "Resource",
                        _RESOURCE_COLOR,
                    )
                else:
                    # The input hasn't been provisioned yet.
                    input_node = DetailedGraphVizNode(
                        required_input_name,
                        -1,
                        "NOT PROVISIONED",
                        "Resource",
                        _RESOURCE_COLOR,
                    )

                graph_nodes.add(input_node)
                graph_edges.add(
                    DetailedGraphVizEdge(
                        required_input_name, task.task_name, "input to"
                    )
                )

            # Process every output that the task has.
            for required_output_name in task_def.outputs:
                possible_output: Maybe[TaskResource] = task_graph.resource(
                    required_output_name
                )
                if possible_output.is_something():
                    required_output: TaskResource = possible_output.unwrap()
                    output_node = DetailedGraphVizNode(
                        required_output.resource_name,
                        required_output.resource_id,
                        required_output.resource_status.name,
                        "Resource",
                        _RESOURCE_COLOR,
                    )
                else:
                    # The output hasn't been provisioned yet.
                    output_node = DetailedGraphVizNode(
                        required_output_name,
                        -1,
                        "NOT PROVISIONED",
                        "Resource",
                        _RESOURCE_COLOR,
                    )

                graph_nodes.add(output_node)
                graph_edges.add(
                    DetailedGraphVizEdge(
                        task.task_name, required_output_name, "outputs"
                    )
                )
        return (graph_nodes, graph_edges)

    def _build_graph_viz(
        self,
        phase: TaskGraphPhase,
        graph_nodes: set[DetailedGraphVizNode],
        graph_edges: set[DetailedGraphVizEdge],
    ) -> Digraph:
        viz_time: datetime = TimeUtilities.clock_time_now()
        graph_viz = Digraph(
            name="graph_viz",
            filename=f"task_graph-{TimeUtilities.display_time(viz_time)}-{phase}.gv",
            engine="dot",
            graph_attr={
                "label": f"Task Graph {phase} {TimeUtilities.display_time(viz_time, format='%Y-%m-%d %H:%M:%S')}",
                "fontname": "Helvetica,Arial,sans-serif",
                "fontcolor": "white",
                "bgcolor": str(_BACKGROUND_COLOR),
            },
        )

        # Build a graph that represents the task graph.
        # Note that the subgraphs must start with the prefix "cluster".
        subgraph_config = {
            "name": "cluster_task_graph",
            "node_attr": {"style": "filled", "shape": "rectangle"},
            "graph_attr": {
                "label": "Task Graph",
                "color": "gray19",
                "fontcolor": "white",
            },
        }
        with graph_viz.subgraph(**subgraph_config) as graph:  # type: ignore
            # Add all tasks and resources as nodes
            for graph_node in graph_nodes:
                graph.node(
                    name=graph_node.name,
                    # penwidth="1",
                    margin="0",
                    fillcolor="white",
                    shape="plantext",
                    label=graph_node.to_table(),
                )

            # Add all edges. The direction of edges is this is before that  (this -> that).
            for graph_edge in graph_edges:
                graph.edge(
                    tail_name=graph_edge.this,
                    head_name=graph_edge.that,
                    label=graph_edge.label,
                    color=_EDGE_COLOR,
                )

        return graph_viz
