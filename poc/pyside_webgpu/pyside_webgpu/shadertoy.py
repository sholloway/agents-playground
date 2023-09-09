import os
from pathlib import Path

from wgpu.utils.shadertoy import Shadertoy

def main() -> None:
  shader_path: str = os.path.join(Path.cwd(), 'pyside_webgpu/demos/shaders/triangle.wgsl')
  with open(file = shader_path, mode = 'r') as filereader:
    shader = filereader.read()
  print(shader)
  st = Shadertoy(shader_code=shader, resolution=(800,800))
  st.show()

if __name__ == '__main__':
  main()