
from agents_playground.playground_app import PlaygroundApp
from agents_playground.logger import setup_logging
from agents_playground.profile_tools import timer, size

"""
What is the abstraction here?
App
  Simulation
    Renderer
    Agent(s)
    Terrain
    Path
"""

def parse_args() -> dict:
  import argparse
  parser = argparse.ArgumentParser(description='Intelligent Agents Playground')
  parser.add_argument('--log', type=str, dest='loglevel', default="INFO",help='The log level. DEBUG | INFO | WARNING | ERROR | CRITICAL')
  return vars(parser.parse_args())

def main():
  args: dict = parse_args()
  logger = setup_logging(args['loglevel'])
  logger.info("Starting Agent's Playground")
  app = PlaygroundApp()
  app.launch()

if __name__ == "__main__":
  main()