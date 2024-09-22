import argparse
from typing import Optional


class OptionsProcessor:
    """Processes the application command line options"""

    def __init__(self) -> None:
        self._parser = argparse.ArgumentParser(
            description="Intelligent Agents Playground"
        )
        self._options: Optional[dict] = None
        self._register_options()

    def _register_options(self):
        """Register the command line options."""
        # Option to set the log level.
        self._parser.add_argument(
            "--log",
            type=str,
            dest="loglevel",
            default="ERROR",
            help="The log level. DEBUG | INFO | WARNING | ERROR | CRITICAL",
        )

        # Option to load a sim from a file on launch.
        self._parser.add_argument(
            "--sim",
            type=str,
            dest="sim_path",
            default=None,
            help="The simulation to load.",
        )

        # Option to visualize the task graph at run time.
        # Does not take a value. Toggles the ability to capture graph snapshots on.
        self._parser.add_argument(
            "--viz-task-graph",
            dest="viz_task_graph",
            action="store_true",
            default=False,
            help="Capture a snapshot of the task graph during initialization, frame processing, and shutdown. These are written to the current working directory under task_graph_debug_files.",
        )

    def process(self) -> dict:
        self._options = vars(self._parser.parse_args())
        return self._options
