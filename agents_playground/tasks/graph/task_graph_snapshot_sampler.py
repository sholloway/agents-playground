from abc import ABC, abstractmethod
from collections.abc import Sequence
import os
from pathlib import Path

from graphviz import Digraph

from agents_playground.sys.logger import get_default_logger
from agents_playground.tasks.graph.types import TaskGraphPhase
from agents_playground.tasks.types import TaskGraphLike, TaskRunHistory, TaskStatus


class TaskGraphSnapshotSampler(ABC):
    def __init__(self) -> None:
        pass

    def graph_snapshot(
        self,
        task_graph: TaskGraphLike,
        phase: TaskGraphPhase,
        filter: Sequence[TaskStatus],
    ) -> None:
        """
        Inspect the task graph relationships between tasks and resources.
        """
        try:
            snapshot: Digraph = self._take_graph_snapshot(task_graph, phase, filter)
            self._save_snapshot(snapshot)
        except Exception as e:
            get_default_logger().error(
                "An an occurred while trying to take a snapshot of the task graph."
            )
            get_default_logger().exception(e)

    def history_snapshot(
        self,
        task_graph: TaskGraphLike,
        history: tuple[TaskRunHistory, ...],
        phase: TaskGraphPhase,
    ) -> None:
        """
        Inspect the order in which tasks were run.
        """
        try:
            snapshot: Digraph = self._take_history_snapshot(task_graph, history, phase)
            self._save_snapshot(snapshot)
        except Exception as e:
            get_default_logger().error(
                "An an occurred while trying to take a snapshot of the task graph."
            )
            get_default_logger().exception(e)

    def memory_snapshot(self, task_graph: TaskGraphLike, phase: TaskGraphPhase) -> None:
        """
        Inspect the memory used by resources
        """
        try:
            snapshot: Digraph = self._take_memory_snapshot(task_graph, phase)
            self._save_snapshot(snapshot, engine="fdp")
        except Exception as e:
            get_default_logger().error(
                "An an occurred while trying to take a snapshot of the task graph."
            )
            get_default_logger().exception(e)

    @abstractmethod
    def _take_graph_snapshot(
        self,
        task_graph: TaskGraphLike,
        phase: TaskGraphPhase,
        filter: Sequence[TaskStatus],
    ) -> Digraph: ...

    @abstractmethod
    def _take_history_snapshot(
        self,
        task_graph: TaskGraphLike,
        history: tuple[TaskRunHistory, ...],
        phase: TaskGraphPhase,
    ) -> Digraph: ...

    @abstractmethod
    def _take_memory_snapshot(
        self,
        task_graph: TaskGraphLike,
        phase: TaskGraphPhase,
    ) -> Digraph: ...

    def _save_snapshot(self, snapshot: Digraph, engine: str = "dot") -> None:
        """Save the graphviz file and render it."""
        task_graph_debug_dir: str = os.path.join(Path.cwd(), "task_graph_debug_files")
        if not os.path.isdir(task_graph_debug_dir):
            os.mkdir(task_graph_debug_dir)
        snapshot.render(directory=task_graph_debug_dir, cleanup=True, engine=engine)
