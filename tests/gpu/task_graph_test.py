"""
This is a temporary test to help work through creating a frame graph/render graph based 
rendering pipeline. It'll probably need to be removed after that is established.
"""
import pytest

from agents_playground.tasks.graph import TaskGraph
from agents_playground.tasks.predefined.generic_task import GenericTask
from agents_playground.tasks.register import task, task_input, task_output
from agents_playground.tasks.registry import TaskRegistry, TaskRegistryError, global_task_registry
from agents_playground.tasks.resources import TaskResourceRegistry, global_task_resource_registry
from agents_playground.tasks.types import TaskDef, TaskName

def do_nothing(*args, **kwargs) -> None:
    return

@task_input(type='Texture', id='font_atlas_1', label='Font Atlas')
@task_input(type='Buffer', id='buffer_1', label='Some kind of buffer')
@task_output(type='GPUBuffer', id='font_atlas_buffer', label='Packed Font Atlas')
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
def populated_task_registry() -> TaskRegistry:
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

    # Establish inter-task dependencies.
    
    # Run load_scene_file -> before -> load_landscape | load_agent_meshes | load_entity_meshes | load_textures
    tr.add_requirement(("load_scene_file",), ("load_landscape", "load_agent_meshes", "load_entity_meshes","load_textures"))
   
    # run load_landscape & load_agent_meshes & load_entity_meshes & load_textures -> before -> init_graphics_pipeline
    tr.add_requirement(("load_landscape", "load_agent_meshes", "load_entity_meshes", "load_textures"), ("init_graphics_pipeline",))

    # run init_graphics_pipeline -> before -> prep_landscape_render | prep_agent_renderer | prep_ui_renderer
    tr.add_requirement(("init_graphics_pipeline",), ("prep_landscape_render", "prep_agent_renderer", "prep_ui_renderer"))
    
    # run prep_landscape_render & prep_agent_renderer & prep_ui_renderer -> before -> start_simulation_loop
    tr.add_requirement(("prep_landscape_render", "prep_agent_renderer", "prep_ui_renderer"),("start_simulation_loop",))

    # Get the above working before adding Input/Output complexities.
    return tr

class TestTaskGraph:
    def test_task_creation(self, task_registry: TaskRegistry) -> None:
        assert task_registry.provisioned_tasks_count == 0
        task = task_registry.provision("my_cool_task", task_ref=do_nothing, args=[], kwargs={})
        assert task.task_id == 1

    def test_task_was_registered(self, task_registry: TaskRegistry) -> None:
        # Test that a task is registered with it's name.
        assert "my_cool_task" in task_registry
        assert "my_task_with_no_deps" in task_registry

    def test_dynamic_task_creation(self, task_registry: TaskRegistry) -> None:
        task = task_registry.provision(
            'my_task_with_no_deps', 
            task_ref=do_nothing,
            args=[],
            kwargs={}
        )
        assert task.task_id == 1

    def test_cannot_provision_unregistered_tasks(self, task_registry: TaskRegistry) -> None:
        with pytest.raises(TaskRegistryError) as tre:
            task_registry.provision('unregistered_task_alias')
        assert "Attempted to provision a task that was not registered. Could not find task alias unregistered_task_alias." == str(tre.value)

    def test_register_task_resources(self, task_registry: TaskRegistry, task_resource_registry: TaskResourceRegistry) -> None:
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

    def test_prepare_task_graph(self, populated_task_registry: TaskRegistry) -> None:
        """
        With the tasks that have been provisioned, create a task graph that can be 
        handed off to be optimized or executed.

        I've used a "smart" queue in the 2D engine to schedule things to work. 
        That version of the TaskScheduler makes use of counters to decrement blocking things. 

        The idea of optimizing a graph is more complicated but may be a better option 
        long term. 

        With this capability, the goal is to produce a list of tasks that can be run
        """

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
            "dynamically_generate_agents",
            "set_agents_initial_state",
            "start_simulation_loop",
        ]
        
        task_graph: TaskGraph = populated_task_registry.task_graph()


    def test_prepare_execution_plan(self) -> None:
        """
        Given a list of tasks, create the optimal execution plan.
        """
        assert False
