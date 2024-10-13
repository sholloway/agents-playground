from multiprocessing.connection import Connection
import os

from agents_playground.core.performance_monitor import PerformanceMonitor
from agents_playground.core.privileged import running_as_root
from agents_playground.sys.logger import get_default_logger
from agents_playground.tasks.register import task, task_input, task_output
from agents_playground.tasks.types import TaskGraphLike, TaskInputs, TaskOutputs

FAILED_TO_START_PERF_MON = "Failed to start the performance monitor."


# TODO: Make this a task.
# Make a version of require_root that works with tasks.
# I'd like to have a task decorator that is conditional.
# For Example:
# @task(require_root=True)
# is there a way to make that more generic?
#   @task(run_only_if=runtime_check_method)
#   @task(run_only_if=running_as_root)
@task_output(type=PerformanceMonitor, name="performance_monitor")
@task(run_if=running_as_root)
def start_perf_monitor(
    task_graph: TaskGraphLike, inputs: TaskInputs, outputs: TaskOutputs
):
    """
    Create an instance of the Performance Monitor and start it.

    Effects:
    - Creates a subprocess that monitors the main process.
    - Outputs the Performance Monitor as a resource.
    - Outputs the Performance Monitor as a resource.
    """
    try:
        outputs.performance_monitor = PerformanceMonitor()
        outputs.performance_monitor.start(os.getpid())
    except Exception as e:
        get_default_logger().error(FAILED_TO_START_PERF_MON)
        get_default_logger().error(e, exc_info=True)
