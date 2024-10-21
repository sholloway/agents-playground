from collections.abc import Sequence
from agents_playground.app.options import application_options
from agents_playground.counter.counter import Counter, CounterBuilder
from agents_playground.sys.logger import LoggingLevel, log_call
from agents_playground.tasks.graph.task_graph_snapshot_sampler import (
    TaskGraphSnapshotSampler,
)
from agents_playground.tasks.graph.types import TaskGraphPhase
from agents_playground.tasks.types import (
    SimulationPhase,
    TaskGraphLike,
    TaskName,
    TaskStatus,
)


class TaskDrivenRenderer:
    @log_call()
    def __init__(
        self,
        task_graph: TaskGraphLike,
        render_tasks: Sequence[TaskName],
        snapshot_sampler: TaskGraphSnapshotSampler,
    ) -> None:
        self._task_graph = task_graph
        self._capture_task_graph_snapshot = application_options()["viz_task_graph"]
        self._snapshot_sampler = snapshot_sampler
        self._frame_capture_counter: Counter = (
            CounterBuilder.integer_counter_with_defaults(max_value=5)
        )
        self._render_tasks = render_tasks

    @log_call(level=LoggingLevel.DEBUG)
    def render(self) -> None:
        self._task_graph.provision_tasks(self._render_tasks)

        if (
            self._capture_task_graph_snapshot
            and not self._frame_capture_counter.at_max_value()
        ):
            self._frame_capture_counter.increment()
            self._snapshot_sampler.graph_snapshot(
                task_graph=self._task_graph,
                phase=TaskGraphPhase.FRAME_DRAW,
                filter=(TaskStatus.INITIALIZED,),
            )

        self._task_graph.run_until_done()
        self._task_graph.release_completed_tasks()
        self._task_graph.release_resources(SimulationPhase.END_OF_FRAME)
