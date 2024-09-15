"""
This is a temporary test to help work through creating a frame graph/render graph based 
rendering pipeline. It'll probably need to be removed after that is established.
"""

import pytest

from agents_playground.core.task_scheduler import TaskId
from agents_playground.tasks.graph import TaskGraph
from agents_playground.tasks.predefined.generic_task import GenericTask
from agents_playground.tasks.register import task, task_input, task_output
from agents_playground.tasks.registry import (
    TaskRegistry,
    TaskRegistryError,
    global_task_registry,
)
from agents_playground.tasks.resources import (
    TaskResourceRegistry,
    global_task_resource_registry,
)
from agents_playground.tasks.tracker import TaskTracker
from agents_playground.tasks.types import TaskDef, TaskName, TaskStatus


def do_nothing(*args, **kwargs) -> None:
    return


@task_input(type="Texture", name="font_atlas_1")
@task_input(type="Buffer", name="buffer_1")
@task_output(type="GPUBuffer", name="font_atlas_buffer")
@task(name="my_cool_task")
class MyTask:
    pass


@task(name="my_task_with_no_deps")
class MyLonelyTask:
    pass


@pytest.fixture
def task_registry() -> TaskRegistry:
    """Injects the global task registry."""
    return global_task_registry()


@pytest.fixture
def task_resource_registry() -> TaskResourceRegistry:
    """Injects the global task resource registry."""
    return global_task_resource_registry()


@pytest.fixture
def initial_tasks() -> TaskRegistry:
    """Create a registry that is populated outside of using decorators.
    The Desired Hierarchy is:
    load_scene_file
        load_landscape | load_agent_meshes | load_entity_meshes | load_textures
    init_graphics_pipeline
        prep_landscape_render | prep_agent_renderer | prep_ui_renderer
    start_simulation_loop
    """
    tr = TaskRegistry()

    # Register the tasks
    for task_name in [
        "load_scene_file",
        "load_landscape",
        "load_agent_meshes",
        "load_entity_meshes",
        "load_textures",
        "init_graphics_pipeline",
        "prep_landscape_render",
        "prep_agent_renderer",
        "prep_ui_renderer",
        "start_simulation_loop",
    ]:
        tr.register(task_name, TaskDef(name=task_name, type=GenericTask))

    # Get the above working before adding Input/Output complexities.
    return tr


@pytest.fixture
def initial_tasks_with_requirements(initial_tasks: TaskRegistry) -> TaskRegistry:
    # Run load_scene_file -> before -> load_landscape | load_agent_meshes | load_entity_meshes | load_textures
    initial_tasks.add_requirement(
        ("load_scene_file",),
        ("load_landscape", "load_agent_meshes", "load_entity_meshes", "load_textures"),
    )

    # run load_landscape & load_agent_meshes & load_entity_meshes & load_textures -> before -> init_graphics_pipeline
    initial_tasks.add_requirement(
        ("load_landscape", "load_agent_meshes", "load_entity_meshes", "load_textures"),
        ("init_graphics_pipeline",),
    )

    # run init_graphics_pipeline -> before -> prep_landscape_render | prep_agent_renderer | prep_ui_renderer
    initial_tasks.add_requirement(
        ("init_graphics_pipeline",),
        ("prep_landscape_render", "prep_agent_renderer", "prep_ui_renderer"),
    )

    # run prep_landscape_render & prep_agent_renderer & prep_ui_renderer -> before -> start_simulation_loop
    initial_tasks.add_requirement(
        ("prep_landscape_render", "prep_agent_renderer", "prep_ui_renderer"),
        ("start_simulation_loop",),
    )
    return initial_tasks


@pytest.fixture
def provisioned_initial_tasks(
    initial_tasks_with_requirements: TaskRegistry,
) -> TaskTracker:
    tr = initial_tasks_with_requirements
    tt = TaskTracker()

    for task_name in tr.task_names():
        tt.track(
            initial_tasks_with_requirements.provision(
                task_name, task_ref=do_nothing, args=[], kwargs={}
            )
        )

    return tt


class TestTaskGraph:
    def test_task_creation(self, task_registry: TaskRegistry) -> None:
        assert task_registry.provisioned_tasks_count == 0
        task = task_registry.provision(
            "my_cool_task", task_ref=do_nothing, args=[], kwargs={}
        )
        assert task.task_id == 1

    def test_task_was_registered(self, task_registry: TaskRegistry) -> None:
        # Test that a task is registered with it's name.
        assert "my_cool_task" in task_registry
        assert "my_task_with_no_deps" in task_registry

    def test_dynamic_task_creation(self, task_registry: TaskRegistry) -> None:
        task = task_registry.provision(
            "my_task_with_no_deps", task_ref=do_nothing, args=[], kwargs={}
        )
        assert task.task_id == 1

    def test_cannot_provision_unregistered_tasks(
        self, task_registry: TaskRegistry
    ) -> None:
        with pytest.raises(TaskRegistryError) as tre:
            task_registry.provision("unregistered_task_alias")
        assert (
            "Attempted to provision a task that was not registered. Could not find task alias unregistered_task_alias."
            == str(tre.value)
        )

    def test_register_task_resources(
        self, task_registry: TaskRegistry, task_resource_registry: TaskResourceRegistry
    ) -> None:
        """
        Task declarations that are marked with @task_input or @task_output have their
        associated resources added to the task resource registry when an instance of
        the task is provisioned.
        """
        task_registry.provision("my_cool_task", task_ref=do_nothing, args=[], kwargs={})

        # Verify that the resources are registered.
        assert len(task_resource_registry) == 3
        assert "font_atlas_1" in task_resource_registry
        assert "buffer_1" in task_resource_registry
        assert "font_atlas_buffer" in task_resource_registry

        # Verify that the task instance has the resources associated.
        task_def = task_registry["my_cool_task"]
        assert "font_atlas_1" in task_def.inputs
        assert "buffer_1" in task_def.inputs
        assert "font_atlas_buffer" in task_def.outputs

    def test_track_provisioned_task(
        self, initial_tasks_with_requirements: TaskRegistry
    ) -> None:
        """
        With the tasks that have been provisioned, create a task graph that can be
        handed off to be optimized or executed.

        I've used a "smart" queue in the 2D engine to schedule things to work.
        That version of the TaskScheduler makes use of counters to decrement blocking things.

        The idea of optimizing a graph is more complicated but may be a better option
        long term.

        With this capability, the goal is to produce a list of tasks that can be run
        """
        tr = initial_tasks_with_requirements

        # The scene.json determines the general intent.
        # This is an example of what might be listed in a simulation file.
        initial_tasks: list[TaskName] = [
            "load_scene_file",
            "load_landscape",
            "load_agent_meshes",
            "load_entity_meshes",
            "load_textures",
            "init_graphics_pipeline",
            "prep_landscape_render",
            "prep_agent_renderer",
            "prep_ui_renderer",
            "start_simulation_loop",
        ]

        task_graph = TaskGraph(task_registry=initial_tasks_with_requirements)
        task_ids: list[TaskId] = []

        for task_name in initial_tasks:
            task_ids.append(
                task_graph.provision(
                    task_name, task_ref=do_nothing, args=[], kwargs={}
                ).task_id
            )

        assert len(task_graph.task_tracker) == 10
        for id in task_ids:
            assert id in task_graph.task_tracker

    def test_update_tracked_tasks(
        self,
        initial_tasks_with_requirements: TaskRegistry,
        provisioned_initial_tasks: TaskTracker,
    ) -> None:
        # Given a task graph with provisioned tasks, check all tasks to see if they
        # can now run.
        task_graph = TaskGraph(
            task_registry=initial_tasks_with_requirements,
            task_tracker=provisioned_initial_tasks,
        )
        assert len(task_graph.tasks_with_status((TaskStatus.INITIALIZED,))) == 10
        task_graph.check_if_blocked_tasks_are_ready()
        assert len(task_graph.tasks_with_status((TaskStatus.INITIALIZED,))) == 0

        # With the tasks provisioned by initial_tasks_with_requirements, only
        # the first task should now be READY_FOR_ASSIGNMENT. The others should be blocked.
        assert (
            len(task_graph.tasks_with_status((TaskStatus.READY_FOR_ASSIGNMENT,))) == 1
        )
        assert len(task_graph.tasks_with_status((TaskStatus.BLOCKED,))) == 9

    def test_manually_run_graph(
        self,
        initial_tasks_with_requirements: TaskRegistry,
        provisioned_initial_tasks: TaskTracker,
    ) -> None:
        # Manually run the tasks until the graph is complete.
        task_graph = TaskGraph(
            task_registry=initial_tasks_with_requirements,
            task_tracker=provisioned_initial_tasks,
        )
        task_graph.check_if_blocked_tasks_are_ready()

        # With the tasks provisioned by initial_tasks_with_requirements, only
        # the first task should now be READY_FOR_ASSIGNMENT. The others should be blocked.
        assert (
            len(task_graph.tasks_with_status((TaskStatus.READY_FOR_ASSIGNMENT,))) == 1
        )
        assert len(task_graph.tasks_with_status((TaskStatus.COMPLETE,))) == 0
        
        task_graph.run_all_ready_tasks()

        assert len(task_graph.tasks_with_status((TaskStatus.COMPLETE,))) == 1

        task_graph.check_if_blocked_tasks_are_ready()
        assert (
            len(task_graph.tasks_with_status((TaskStatus.READY_FOR_ASSIGNMENT,))) == 4
        )
        
        task_graph.run_all_ready_tasks()
        assert len(task_graph.tasks_with_status((TaskStatus.COMPLETE,))) == 5
        
        task_graph.check_if_blocked_tasks_are_ready()
        assert (
            len(task_graph.tasks_with_status((TaskStatus.READY_FOR_ASSIGNMENT,))) == 1
        )
        
        task_graph.run_all_ready_tasks()
        assert len(task_graph.tasks_with_status((TaskStatus.COMPLETE,))) == 6
        
        task_graph.check_if_blocked_tasks_are_ready()
        assert (
            len(task_graph.tasks_with_status((TaskStatus.READY_FOR_ASSIGNMENT,))) == 3
        )
        
        task_graph.run_all_ready_tasks()
        assert len(task_graph.tasks_with_status((TaskStatus.COMPLETE,))) == 9
        
        task_graph.check_if_blocked_tasks_are_ready()
        assert (
            len(task_graph.tasks_with_status((TaskStatus.READY_FOR_ASSIGNMENT,))) == 1
        )
        
        task_graph.run_all_ready_tasks()
        assert len(task_graph.tasks_with_status((TaskStatus.COMPLETE,))) == 10

    def test_run_graph_until_done(
        self,
        initial_tasks_with_requirements: TaskRegistry,
        provisioned_initial_tasks: TaskTracker,
    ) -> None:
        # Run the tasks until the graph is complete.
        task_graph = TaskGraph(
            task_registry=initial_tasks_with_requirements,
            task_tracker=provisioned_initial_tasks,
        )
        assert len(task_graph.tasks_with_status((TaskStatus.COMPLETE,))) == 0
        task_graph.run_until_done()
        assert len(task_graph.tasks_with_status((TaskStatus.COMPLETE,))) == 10