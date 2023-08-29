import argparse

class OptionsProcessor:
  """Processes the application command line options"""
  def __init__(self) -> None:
    self._parser = argparse.ArgumentParser(description='WebGPU POC')
    self._options: dict | None = None
    self._register_options()

  def _register_options(self):
    """Register the command line options."""
    self._parser.add_argument(
      '--poc', 
      type=str,
      dest='poc',
      default='pyside_triangle',
      help='Which POC to run? pyside_triangle | wx_triangle'
    )

  def process(self) -> dict:
    self._options = vars(self._parser.parse_args())
    return self._options