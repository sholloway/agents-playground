import math
import threading
from time import sleep, perf_counter

import dearpygui.dearpygui as dpg

from logger import log, setup_logging
from profile_tools import timer, size

def parse_args() -> dict:
  import argparse
  parser = argparse.ArgumentParser(description='Intelligent Agents Playground')
  parser.add_argument('--log', type=str, dest='loglevel', default="INFO",help='The log level. DEBUG | INFO | WARNING | ERROR | CRITICAL')
  return vars(parser.parse_args())

def animation_thread_loop():
  planet2_moon2angle = 120
  planet2_moon2distance = 45
  while True:
    sleep(0.1)
    planet2_moon2angle += 5
    dpg.apply_transform("planet 2, moon 2 node", dpg.create_rotation_matrix(math.pi*planet2_moon2angle/180.0 , [0, 0, -1])*dpg.create_translation_matrix([planet2_moon2distance, 0]))

def pulse(time:float):
  # frequency: float = 10; # Frequency in Hz
  return 0.5*(1+math.sin(2 * math.pi * time))

def single_agent_sim_loop():
  # for now just have the radius pulsate.

  default_radius: float = 20
  scale:float = 10

  while True:
    sleep(0.100) 
    inflat:float = pulse(perf_counter())
    new_radius = default_radius + scale * inflat
    dpg.configure_item('my-circle',radius = new_radius)

def launch_single_agent_sim(sender):
  with dpg.window(label="Single Agent Simulation", width=400, height=400):
    dpg.add_text("Baby steps...")
    # Create a drawing canvas
    with dpg.drawlist(label="My Drawlist", width=400, height=400): 
      with dpg.draw_node(label="My Node", tag="circle-node"):
        dpg.draw_circle(tag="my-circle", center = [0,0], radius=20, color=[0, 0, 0], fill=[0, 0, 255])
  
    dpg.apply_transform("circle-node", dpg.create_translation_matrix([250, 250]))  

  # Create a thread for updating the simulation.
  sim_thread = threading.Thread(name="single-agent-thread", target=single_agent_sim_loop, args=(), daemon=True)
  sim_thread.start()

@log
def setup_ui():
  dpg.create_context()

  # Configure the Primary Window (the hosting window).
  with dpg.window(tag="Primary Window"):
    dpg.add_text("Hello, world")

  dpg.create_viewport(title="Intelligent Agent Playground")

  # Configure the primary window's menu bar.
  with dpg.viewport_menu_bar():
    with dpg.menu(label="Simulations"):
      dpg.add_menu_item(label="Single Agent", callback=launch_single_agent_sim)
      
  dpg.setup_dearpygui() # Assign the viewport

  # This is a nested window.
  with dpg.window(label="tutorial", width=550, height=550):
    with dpg.drawlist(width=500, height=500):
      with dpg.draw_node(tag="root node"):
        dpg.draw_circle([0, 0], 150, color=[0, 255, 0])                      # inner planet orbit
        dpg.draw_circle([0, 0], 200, color=[0, 255, 255])                    # outer planet orbit
        dpg.draw_circle([0, 0], 15, color=[255, 255, 0], fill=[255, 255, 0]) # sun

        with dpg.draw_node(tag="planet node 1"):
          dpg.draw_circle([0, 0], 10, color=[0, 255, 0], fill=[0, 255, 0]) # inner planet
          dpg.draw_circle([0, 0], 25, color=[255, 0, 255])                 # moon orbit path

          with dpg.draw_node(tag="planet 1, moon node"):
            dpg.draw_circle([0, 0], 5, color=[255, 0, 255], fill=[255, 0, 255]) # moon

        with dpg.draw_node(tag="planet node 2"):
          dpg.draw_circle([0, 0], 10, color=[0, 255, 255], fill=[0, 255, 255]) # outer planet
          dpg.draw_circle([0, 0], 25, color=[255, 0, 255])                     # moon 1 orbit path
          dpg.draw_circle([0, 0], 45, color=[255, 255, 255])                   # moon 2 orbit path

          with dpg.draw_node(tag="planet 2, moon 1 node"):
            dpg.draw_circle([0, 0], 5, color=[255, 0, 255], fill=[255, 0, 255]) # moon 1

          with dpg.draw_node(tag="planet 2, moon 2 node"):
            dpg.draw_circle([0, 0], 5, color=[255, 255, 255], fill=[255, 255, 255]) # moon 2

  planet1_distance = 150
  planet1_angle = 45.0
  planet1_moondistance = 25
  planet1_moonangle = 45

  planet2_distance = 200
  planet2_angle = 0.0
  planet2_moon1distance = 25
  planet2_moon1angle = 45
  planet2_moon2distance = 45
  planet2_moon2angle = 120

  dpg.apply_transform("root node", dpg.create_translation_matrix([250, 250]))
  dpg.apply_transform("planet node 1", dpg.create_rotation_matrix(math.pi*planet1_angle/180.0 , [0, 0, -1])*dpg.create_translation_matrix([planet1_distance, 0]))
  dpg.apply_transform("planet 1, moon node", dpg.create_rotation_matrix(math.pi*planet1_moonangle/180.0 , [0, 0, -1])*dpg.create_translation_matrix([planet1_moondistance, 0]))
  dpg.apply_transform("planet node 2", dpg.create_rotation_matrix(math.pi*planet2_angle/180.0 , [0, 0, -1])*dpg.create_translation_matrix([planet2_distance, 0]))
  dpg.apply_transform("planet 2, moon 1 node", dpg.create_rotation_matrix(math.pi*planet2_moon1distance/180.0 , [0, 0, -1])*dpg.create_translation_matrix([planet2_moon1distance, 0]))
  dpg.apply_transform("planet 2, moon 2 node", dpg.create_rotation_matrix(math.pi*planet2_moon2angle/180.0 , [0, 0, -1])*dpg.create_translation_matrix([planet2_moon2distance, 0]))

  dpg.show_viewport()
  dpg.set_primary_window("Primary Window", True)

  # Create a thread for updating the animation.
  animation_thread = threading.Thread(name="create blocks", target=animation_thread_loop, args=(), daemon=True)
  animation_thread.start()

  # this is the render loop for all of the viewports.
  while dpg.is_dearpygui_running():
    dpg.render_dearpygui_frame()

  dpg.destroy_context()
  

def main():
  args: dict = parse_args()
  logger = setup_logging(args['loglevel'])
  logger.info("Starting Agent's Playground")
  setup_ui()

if __name__ == "__main__":
  main()