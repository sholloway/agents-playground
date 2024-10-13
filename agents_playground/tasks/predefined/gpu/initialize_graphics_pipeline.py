import wgpu
from wgpu import (
    gpu,
    GPUCanvasContext,
    GPUDevice,
)
from wgpu import GPUDevice
from wgpu.gui.wx import WgpuWidget

from agents_playground.tasks.register import task, task_input, task_output
from agents_playground.tasks.types import (
    TaskGraphLike,
    TaskInputs,
    TaskOutputs,
)


@task_input(type=WgpuWidget, name="canvas")
@task_output(type=GPUDevice, name="gpu_device")
@task_output(type=str, name="render_texture_format")
@task(require_before=["load_landscape_mesh"])
def initialize_graphics_pipeline(
    task_graph: TaskGraphLike, inputs: TaskInputs, outputs: TaskOutputs
) -> None:
    """
    A task responsible for initializing the graphics pipeline.
    """
    # Initialize the graphics pipeline via WebGPU.
    canvas: WgpuWidget = inputs.canvas

    # Create a high performance GPUAdapter for a Canvas.
    adapter: GPUAdapter = gpu.request_adapter(  # type: ignore
        canvas=canvas, power_preference="high-performance"
    )

    # Get an instance of the GPUDevice that is associated with a provided GPUAdapter.
    device: GPUDevice = adapter.request_device(
        label="only-gpu-device",
        required_features=[],
        required_limits={},
        default_queue={},
    )

    canvas_context: GPUCanvasContext = canvas.get_context()

    # Set the GPUCanvasConfiguration to control how drawing is done.
    render_texture_format: str = canvas_context.get_preferred_format(device.adapter)

    canvas_context.configure(
        device=device,
        usage=wgpu.flags.TextureUsage.RENDER_ATTACHMENT,  # type: ignore
        format=render_texture_format,
        view_formats=[],
        color_space="bgra8unorm-srgb",
        alpha_mode="opaque",
    )

    outputs.gpu_device = device
    outputs.render_texture_format = render_texture_format
