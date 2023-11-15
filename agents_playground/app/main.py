from typing import Any
from agents_playground.app.playground import Playground

from agents_playground.app.playground_app import PlaygroundApp
from agents_playground.app.options import OptionsProcessor
from agents_playground.sys.logger import setup_logging

def main() -> None:
  args: dict[str, Any] = OptionsProcessor().process()
  logger = setup_logging(args['loglevel'])
  logger.info("Main: Starting")

  # app = PlaygroundApp()
  # app.launch()

  app = Playground()
  app.MainLoop()

if __name__ == "__main__":
  main()