from agents_playground.core.task_scheduler import TaskId
from agents_playground.tasks.types import TaskLike

class TaskTrackerError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class TaskTracker:
    """
    Responsible for maintaining provisioned tasks.
    """
    def __init__(self) -> None:
        self._provisioned_tasks: list[TaskLike] = []
        self._task_id_index: dict[TaskId, int] = {}

    def clear(self) -> None:
        self._provisioned_tasks.clear()
        self._task_id_index.clear()

    def track(self, task: TaskLike) -> TaskId:
        if task.task_id in self._provisioned_tasks:
            raise TaskTrackerError(f"The task {task.task_id} is already being tracked.")
        self._provisioned_tasks.append(task)
        self._task_id_index[task.task_id] = len(self._provisioned_tasks) - 1
        return task.task_id

    # def task_graph(self) -> TaskGraph:
    #     graph = TaskGraph()
    #     for task in self._provisioned_tasks:
    #         pass
    #         # task.required_before_tasks
    #         # graph.
    #     return graph
    
    def __getitem__(self, key: TaskId) -> TaskLike:
        """Finds a TaskLike definition by its alias."""
        index = self._task_id_index[key]
        return self._provisioned_tasks[index]
    
    def __len__(self) -> int:
        return len(self._provisioned_tasks)
    
    def __contains__(self, key: TaskId) -> bool:
        return key in self._task_id_index
    
_task_tracker = TaskTracker()

def global_task_tracker() -> TaskTracker:
    return _task_tracker