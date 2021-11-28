from logger import log, setup_logging
from profile_tools import timer

def parse_args() -> dict:
  import argparse
  parser = argparse.ArgumentParser(description='Intelligent Agents Playground')
  parser.add_argument('--log', type=str, dest='loglevel', default="INFO",help='The log level. DEBUG | INFO | WARNING | ERROR | CRITICAL')
  return vars(parser.parse_args())

@log
@timer
def setup_ui():
  import dearpygui.dearpygui as dpg
  import dearpygui.demo as demo

  dpg.create_context()
  dpg.create_viewport(title='Custom Title', width=600, height=600)

  demo.show_demo()

  dpg.setup_dearpygui()
  dpg.show_viewport()
  dpg.start_dearpygui()
  dpg.destroy_context()

def main():
  args: dict = parse_args()
  logger = setup_logging(args['loglevel'])
  logger.info("Starting Agent's Playground")
  setup_ui()

if __name__ == "__main__":
  main()