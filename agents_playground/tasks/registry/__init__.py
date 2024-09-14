from itertools import chain
from agents_playground.counter.counter import Counter, CounterBuilder
from agents_playground.tasks.graph import TaskGraph
from agents_playground.tasks.types import TaskDef, TaskId, TaskLike, TaskName


class TaskRegistryError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class TaskRegistry:
    """
    Responsible for maintaining a registry of tasks that can be provisioned.
    When a task is provisioned it is stored in the TaskRegistry.
    """
    def __init__(self) -> None:
        # Storage and indices for task type declarations
        self._registered_tasks: list[TaskDef] = []
        self._aliases_index: dict[TaskName, int] = {}

        # Storage and indices for provisioned tasks.
        self._task_counter: Counter[int] = CounterBuilder.count_up_from_zero()
        self._provisioned_tasks: list[TaskLike] = []
        self._provisioned_task_ids: dict[TaskId, int] = {}

        

    def register(self, alias:str, task_def: TaskDef) -> None:
        """Alternative to tr[alias] = task_def."""
        self[alias] = task_def

    def clear(self) -> None:
        self._aliases_index.clear()
        self._registered_tasks.clear()
        self._provisioned_tasks.clear()
        self._provisioned_task_ids.clear()

    def provision(self, alias: str, *args, **kwargs) -> TaskLike:
        if alias not in self._aliases_index:
            raise TaskRegistryError(f"Attempted to provision a task that was not registered. Could not find task alias {alias}.")
        
        task_def_index = self._aliases_index[alias]
        task_def = self._registered_tasks[task_def_index]
        task: TaskLike = task_def.type(*args, **kwargs)
        task.task_id = self._task_counter.increment()
                
        self._provisioned_tasks.append(task)
        self._provisioned_task_ids[task.task_id] = len(self._provisioned_tasks) - 1
        return task

    def task_graph(self) -> TaskGraph:
        graph = TaskGraph()
        for task in self._provisioned_tasks:
            pass
            # task.required_before_tasks
            # graph.
        return graph
    
    def add_requirement(
        self, 
        before_tasks: tuple[TaskName,...], 
        later_tasks: tuple[TaskName,...]
    ) -> None:
        """
        Set a task dependency. Task A (B, C,...) must run before task X, (Y, Z).

        Args:
        - before_tasks: The list of tasks that must run before the later tasks.
        - later_tasks: The list of tasks that can run after the list of tasks in the before tuple.
        """
        # Verify that all tasks are in the registry.
        for task_name in chain(before_tasks, later_tasks):
            if task_name not in self._aliases_index:
                raise TaskRegistryError(f"Attempted to add a requirement on a task that is not registered.\nThe task name {task_name} is not associated with a registered task.")
        
        # Add the before tasks as requirements to the later tasks.
        for later_task_name in later_tasks:
            later_task: TaskDef = self[later_task_name]
            later_task.required_before_tasks.extend(before_tasks)

    @property
    def provisioned_tasks_count(self) -> int:
        return len(self._provisioned_tasks)

    def __setitem__(self, key: str, value: TaskDef) -> None:
        if key in self._aliases_index:
            raise TaskRegistryError(
                f"The alias {key} is already assigned to a Task definition."
            )
        if value in self._registered_tasks:
            index = self._registered_tasks.index(value)
        else:
            self._registered_tasks.append(value)
            index = len(self._registered_tasks) - 1
        self._aliases_index[key] = index 
      

    def __getitem__(self, key: TaskName) -> TaskDef:
        """Finds a TaskLike definition by its alias."""
        index = self._aliases_index[key]
        return self._registered_tasks[index]
    
    def __len__(self) -> int:
        return len(self._aliases_index)
    
    def __contains__(self, key: str) -> bool:
        """Enables 'my_alias' in task_registry."""
        return key in self._aliases_index
    
_task_registry: TaskRegistry = TaskRegistry()

def global_task_registry() -> TaskRegistry:
    return _task_registry