import pytest

import matplotlib.pyplot as plt
import squarify    

from agents_playground.tasks.types import ResourceAllocation

# Create a data frame with fake data
# df = pd.DataFrame({'nb_people':[8,3,4,2], 'group':["group A", "group B", "group C", "group D"] })

def test_simple_tree_map() -> None: 
    nb_people = [8,3,4,2]
    group = ["group A", "group B", "group C", "group D"]

    # plot it
    squarify.plot(sizes=nb_people, label=group, alpha=.8 )
    plt.axis('off')
    plt.show()

@pytest.fixture
def allocated_resources() -> tuple[ResourceAllocation, ...]:
    return tuple([ResourceAllocation(1, "simulation_tasks", 48),
        ResourceAllocation(2, "scene_file_path", 111),
        ResourceAllocation(3, "canvas", 144),
        ResourceAllocation(4, "scene", 48),
        ResourceAllocation(5, "landscape", 48),
        ResourceAllocation(6, "landscape_tri_mesh", 48),
        ResourceAllocation(7, "gpu_device", 48),
        ResourceAllocation(8, "render_texture_format", 56),
        ResourceAllocation(9, "camera_uniforms", 48),
        ResourceAllocation(10, "display_configuration_buffer", 48),
        ResourceAllocation(11, "landscape_rendering_pipeline", 48),
        ResourceAllocation(12, "landscape_renderer", 48),
        ResourceAllocation(13, "simulation_context", 48),
        ResourceAllocation(14, "fps_text_data", 48),
        ResourceAllocation(15, "fps_text_viewport_buffer", 48),
        ResourceAllocation(16, "fps_text_overlay_config_buffer", 48),
        ResourceAllocation(17, "fps_text_renderer_rendering_pipeline", 48),
        ResourceAllocation(18, "fps_text_renderer", 48),
        ResourceAllocation(19, "task_renderer", 48),
        ResourceAllocation(20, "sim_loop", 48)])

def test_visualize_resource_memory(allocated_resources: tuple[ResourceAllocation, ...]) -> None:
    sizes = [resource.size for resource in allocated_resources]
    names = [f"{resource.name}\n{resource.size}" for resource in allocated_resources]

    # plot it
    squarify.plot(sizes=sizes, label=names, alpha=.8 )
    plt.axis('off')
    plt.show()