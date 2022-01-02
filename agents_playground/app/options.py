import argparse
from typing import Optional

class OptionsProcessor:
  """Processes the application command line options"""
  def __init__(self) -> None:
    self._parser = argparse.ArgumentParser(description='Intelligent Agents Playground')
    self._options: Optional[dict] = None
    self._register_options()

  def _register_options(self):
    """Register the command line options."""
    self._parser.add_argument(
      '--log', 
      type=str, 
      dest='loglevel', 
      default="INFO",
      help='The log level. DEBUG | INFO | WARNING | ERROR | CRITICAL'
    )

  def process(self) -> dict:
    self._options = vars(self._parser.parse_args())
    return self._options