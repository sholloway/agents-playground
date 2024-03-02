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
    # Option to set the log level.
    self._parser.add_argument(
      '--log', 
      type=str, 
      dest='loglevel', 
      default="INFO",
      help='The log level. DEBUG | INFO | WARNING | ERROR | CRITICAL'
    )

    # Option to load a sim from a file on launch.
    self._parser.add_argument(
      '--sim',
      type=str,
      dest='sim_path',
      default=None,
      help='The simulation to load.'
    )

    # Option to control which UI to launch with. Classic or Normal.
    # Note: This will be removed when the new UI and rendering pipeline is done.
    self._parser.add_argument(
      '--ui_version',
      type=str,
      dest='ui_version',
      default='normal',
      help='The UI style to use. CLASSIC | NORMAL'
    )



  def process(self) -> dict:
    self._options = vars(self._parser.parse_args())
    return self._options