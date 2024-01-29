from __future__ import annotations

from abc import abstractmethod
from array import array as create_array
from array import ArrayType
from dataclasses import dataclass
from math import radians
import os

from typing import Dict, List, Protocol, Tuple

import wx
import wgpu
import wgpu.backends.wgpu_native
from wgpu.gui.wx import WgpuWidget

from agents_playground.cameras.camera import Camera, Camera3d
from agents_playground.core.observe import Observable
from agents_playground.core.task_scheduler import TaskScheduler
from agents_playground.core.webgpu_sim_loop import WGPUSimLoop
from agents_playground.gpu.pipelines.obj_pipeline import ObjPipeline
from agents_playground.gpu.pipelines.web_gpu_pipeline import WebGpuPipeline
from agents_playground.scene.scene_reader import SceneReader
from agents_playground.loaders.mesh import Mesh

from agents_playground.simulation.context import SimulationContext
from agents_playground.spatial.matrix.matrix import Matrix, MatrixOrder
from agents_playground.spatial.matrix.matrix4x4 import Matrix4x4
from agents_playground.spatial.vector.vector3d import Vector3d

class WebGPUSimulation(Observable):
  def __init__(
    self, 
    parent: wx.Window,
    canvas: WgpuWidget,
    scene_toml: str, 
    scene_reader: SceneReader, 
    project_name: str = ''
  ) -> None:
    super().__init__()
    self._canvas = canvas
    self._scene_toml = scene_toml
    self._project_name = project_name
    self._scene_reader = scene_reader
    self._context: SimulationContext = SimulationContext()
    self._task_scheduler = TaskScheduler()
    self._pre_sim_task_scheduler = TaskScheduler()
    self._gpu_pipeline: WebGpuPipeline = ObjPipeline()
    
    # The 0.1.0 version of this allows _sim_loop to be set to None.
    # In 0.2.0 let's try to use a Maybe Monad or something similar.
    # self._sim_loop: WGPUSimLoop = WGPUSimLoop(scheduler = self._task_scheduler)
    # self._sim_loop.attach(self)

  def update(self, msg:str) -> None:
    """Receives a notification message from an observable object."""
    # Skipping for the moment.
    # Fire a wx.PostEvent to force a UI redraw?..
    pass

    
  def launch(self) -> None:
    """Opens the Simulation Window
    (At the moment starts rendering...)
    """
    self._gpu_pipeline.initialize_pipeline(self._canvas)