"""
This module is a simple implementation of a model viewer that 
can load glTF models.

To Run
poetry run python -X dev pyside_webgpu/demos/gltf/naive_gltf_loader.py
"""
import os
from pathlib import Path

from pygltflib import GLTF2
import wx

import wgpu
import wgpu.backends.rs

from pyside_webgpu.demos.gltf.ui import AppWindow

"""
TODO
- [X] Select a glTF parser.
- [X] Select a few glTF models.
- Implement this beast!
"""

def select_scene() -> str:
  scene_dir = 'pyside_webgpu/demos/pyside/models/glTF'
  scene_filename = 'Box.gltf'
  return os.path.join(Path.cwd(), scene_dir, scene_filename)

def load_scene(scene_file_path: str) -> GLTF2:
  gltf = GLTF2().load(scene_file_path)
  if gltf is not None:
    return gltf  
  else:
    raise Exception(f'The file {scene_file_path} was not able to be loaded.')
  


def main() -> None:
  scene_file_path = select_scene()
  scene_data: GLTF2 = load_scene(scene_file_path)
  app = wx.App()
  app_window = AppWindow()
  app.MainLoop()

if __name__ == '__main__':
  main()