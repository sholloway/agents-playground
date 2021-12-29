from typing import Optional

from agents_playground.app.playground_app import PlaygroundApp
from agents_playground.app.options import OptionsProcessor
from agents_playground.sys.logger import setup_logging
from agents_playground.sys.profile_tools import timer, size

"""
What is the abstraction here?
App
  Simulation
    Renderer
    Agent(s)
    Terrain
    Path
"""

def main():
  args: Optional[dict] = OptionsProcessor().process()
  logger = setup_logging(args['loglevel'])
  logger.info("Starting Agent's Playground")
  app = PlaygroundApp()
  app.launch()

if __name__ == "__main__":
  main()