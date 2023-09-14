"""
This module is a simple implementation of a model viewer that 
can load Obj models.

To Run
poetry run python -X dev pyside_webgpu/demos/obj/app.py
"""
from agents_playground.loaders.obj_loader import ObjLoader, Obj

import os
from pathlib import Path

import wx
import wgpu
import wgpu.backends.rs

from pyside_webgpu.demos.obj.ui import AppWindow

def select_scene() -> str:
  """
  Find the path for the desired scene.
  """
  scene_dir = 'pyside_webgpu/demos/obj/models'
  scene_filename = 'skull.obj'
  return os.path.join(Path.cwd(), scene_dir, scene_filename)

def parse_scene_file(scene_file_path: str) -> Obj:
  return ObjLoader().load(scene_file_path)

def main() -> None:
  # Provision the UI.
  app = wx.App()
  app_window = AppWindow()
  scene_file_path = select_scene()
  scene_data: Obj = parse_scene_file(scene_file_path)

  print(scene_data)

  # app.MainLoop()

if __name__ == '__main__':
  main()