from typing import Optional
from agents_playground.core.playground_app import PlaygroundApp
from agents_playground.core.logger import setup_logging
from agents_playground.core.profile_tools import timer, size
from agents_playground.core.options import OptionsProcessor
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