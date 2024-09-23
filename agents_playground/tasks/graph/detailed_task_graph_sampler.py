from collections.abc import Sequence
from datetime import datetime
from typing import NamedTuple

from graphviz import Digraph
from agents_playground.core.time_utilities import TimeUtilities
from agents_playground.tasks.graph.task_graph_snapshot_sampler import (
    TaskGraphSnapshotSampler,
)
from agents_playground.tasks.graph.types import TaskGraphLike, TaskGraphPhase
from agents_playground.tasks.types import TaskStatus

class DetailedGraphVizNode(NamedTuple):
    name: str
    type: str  # Resource | Task
    # The color name as specified at https://graphviz.org/doc/info/colors.html
    color: str


class DetailedGraphVizEdge(NamedTuple):
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

class DetailedTaskGraphSampler(TaskGraphSnapshotSampler):
    def __init__(self) -> None:
        super().__init__()

    def _take_snapshot(
        self,
        task_graph: TaskGraphLike,
        phase: TaskGraphPhase,
        filter: Sequence[TaskStatus],
    ) -> Digraph:
        viz_time: datetime = TimeUtilities.clock_time_now()
        graph_viz = Digraph(
            name="graph_viz",
            filename=f"task_graph-{TimeUtilities.display_time(viz_time)}-{phase}-details.gv",
            engine="dot",
            graph_attr={
                "label": f"Task Graph {phase} {TimeUtilities.display_time(viz_time, format='%Y-%m-%d %H:%M:%S')}"
            },
        )

        return graph_viz
