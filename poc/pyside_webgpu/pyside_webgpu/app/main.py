from typing import Any

from pyside_webgpu.app.options import OptionsProcessor
from pyside_webgpu.demos.pyside.simple_triangle import build_app as build_pyside_single_triangle
from pyside_webgpu.demos.wx.simple_triangle import build_app as build_wx_single_triangle
from pyside_webgpu.demos.wx.playground_ui import main as run_playground_ui

def main() -> None:
  args: dict[str, Any] = OptionsProcessor().process()
  poc_to_run:str = args['poc']

  match poc_to_run:
    case 'pyside_triangle':
      build_pyside_single_triangle()
    case 'wx_triangle':
      build_wx_single_triangle()
    case 'playground_wx':
      run_playground_ui()
    case _:
      error_msg = f'Unable to run specified POC. The value {poc_to_run} is unknown.'
      raise Exception(error_msg)

if __name__ == "__main__":
  main()