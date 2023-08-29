from typing import Any

from pyside_webgpu.app.options import OptionsProcessor
from pyside_webgpu.demos.pyside.simple_triangle import build_app as build_pyside_single_triangle

def main() -> None:
  args: dict[str, Any] = OptionsProcessor().process()
  poc_to_run:str = args['poc']

  match poc_to_run:
    case 'pyside_triangle':
      build_pyside_single_triangle()
    case 'wx_triangle':
      print('blah')
    case _:
      error_msg = f'Unable to run specified POC. The value {poc_to_run} is unknown.'
      raise Exception(error_msg)

if __name__ == "__main__":
  main()