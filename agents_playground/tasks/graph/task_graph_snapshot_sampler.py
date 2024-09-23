from abc import ABC, abstractmethod
from collections.abc import Sequence
import os
from pathlib import Path

from graphviz import Digraph

from agents_playground.tasks.graph.types import TaskGraphLike, TaskGraphPhase
from agents_playground.tasks.types import TaskStatus


class TaskGraphSnapshotSampler(ABC):
    def __init__(self) -> None:
        pass

    def snapshot(
        self,
        task_graph: TaskGraphLike,
        phase: TaskGraphPhase,
        filter: Sequence[TaskStatus],
    ) -> None:
        snapshot: Digraph = self._take_snapshot(task_graph, phase, filter)
        self._save_snapshot(snapshot)

    @abstractmethod
    def _take_snapshot(
        self,
        task_graph: TaskGraphLike,
        phase: TaskGraphPhase,
        filter: Sequence[TaskStatus],
    ) -> Digraph: ...

    def _save_snapshot(self, snapshot: Digraph) -> None:
        """Save the graphviz file and render it."""
        task_graph_debug_dir: str = os.path.join(Path.cwd(), "task_graph_debug_files")
        if not os.path.isdir(task_graph_debug_dir):
            os.mkdir(task_graph_debug_dir)
        snapshot.render(directory=task_graph_debug_dir, cleanup=True)
