from __future__ import annotations

from agents_playground.core.webgpu_sim_loop import WGPUSimLoop
import wx
import wgpu
import wgpu.backends.rs
from agents_playground.ui.wx_patch import WgpuWidget

from agents_playground.core.observe import Observable

from agents_playground.core.task_scheduler import TaskScheduler
from agents_playground.scene.scene_reader import SceneReader
from agents_playground.simulation.context import SimulationContext

class WebGPUSimulation(Observable):
  def __init__(
    self, 
    parent: wx.Window,
    scene_toml: str, 
    scene_reader = SceneReader(), 
    project_name: str = ''
  ) -> None:
    super().__init__()
    self._scene_toml = scene_toml
    self._project_name = project_name
    self._scene_reader = scene_reader

    self.canvas = WgpuWidget(parent)
    self.canvas.SetMinSize((640, 640))

    self._context: SimulationContext = SimulationContext()
    self._task_scheduler = TaskScheduler()
    self._pre_sim_task_scheduler = TaskScheduler()
    self._gpu_pipeline = WebGPUPipeline()

    # The 0.1.0 version of this allows _sim_loop to be set to None.
    # In 0.2.0 let's try to use a Maybe Monad or something similar.
    self._sim_loop: WGPUSimLoop = WGPUSimLoop(scheduler = self._task_scheduler)
    self._sim_loop.attach(self)


  def update(self, msg:str) -> None:
    """Receives a notification message from an observable object."""
    # Skipping for the moment.
    # Fire a wx.PostEvent to force a UI redraw?..
    pass

    
  def launch(self) -> None:
    """Opens the Simulation Window"""
    pass


ENABLE_WGPU_TRACING = True 

class WebGPUPipeline:
  """
  Orchestrate the WebGPU components.
  """
  def __init__(self) -> None:
    pass

  def initialize_pipeline(self, canvas: WgpuWidget) -> None:
    # Initialize WebGPU
    adapter: wgpu.GPUAdapter = self._provision_adapter(canvas)
    device: wgpu.GPUDevice = self._provision_gpu_device(adapter)
    if ENABLE_WGPU_TRACING:
      device.adapter.request_device_tracing('./wgpu_traces') # type: ignore
    canvas_context: wgpu.GPUCanvasContext = canvas.get_context()

    # Set the GPUCanvasConfiguration to control how drawing is done.
    render_texture_format = canvas_context.get_preferred_format(device.adapter)
    canvas_context.configure(
      device       = device, 
      usage        = wgpu.flags.TextureUsage.RENDER_ATTACHMENT, # type: ignore
      format       = render_texture_format,
      view_formats = [],
      color_space  = 'bgra8unorm-srgb', #'srgb',
      alpha_mode   = 'opaque'
    )

    # Next step, just get the OBJ model loading to flush out working 
    # with the thread in the sim loop.

  def _provision_adapter(canvas: wgpu.gui.WgpuCanvasInterface) -> wgpu.GPUAdapter:
    """
    Create a high performance GPUAdapter for a Canvas.
    """
    return wgpu.request_adapter( # type: ignore
      canvas=canvas, 
      power_preference='high-performance'
    ) 

  def _provision_gpu_device(adapter: wgpu.GPUAdapter) -> wgpu.GPUDevice:
    """
    Get an instance of the GPUDevice that is associated with a 
    provided GPUAdapter.
    """
    return adapter.request_device(
      label='only-gpu-device', 
      required_features=[],
      required_limits={}, 
      default_queue={}
    )

