from dataclasses import dataclass
from typing import Callable

import dearpygui.dearpygui as dpg

from agents_playground.simulation.tag import Tag

@dataclass
class CreateSimWizardUIComponents:
  new_simulation_window: Tag
  simulation_name_input: Tag
  simulation_title_input: Tag
  simulation_description_input: Tag

  
  def __init__(self, generate_uuid: Callable[..., Tag]) -> None:
    self.new_simulation_window = generate_uuid()
    self.simulation_name_input = generate_uuid()
    self.simulation_title_input = generate_uuid()
    self.simulation_description_input = generate_uuid()

TOOL_TIP_WIDTH = 350

class CreateSimWizard:
  def __init__(self) -> None:
    self._ui_components = CreateSimWizardUIComponents(dpg.generate_uuid)

  def launch(self) -> None:
    with dpg.window(
      tag=self._ui_components.new_simulation_window, 
      label="Create a New Simulation", 
      width = 660, 
      height= 600, 
      modal=True
    ):
      self._add_text_input(
        tag     = self._ui_components.simulation_name_input,
        label   = "Name", 
        tooltip = "Assign a unique name for the simulation. This is the name of the simulation file. Example: my_simulation"
      )
      self._add_text_input(
        tag     = self._ui_components.simulation_title_input,
        label   = "Title", 
        tooltip = "Assign a unique title for the simulation. This will be displayed in the Simulation menu."
      )
      self._add_text_input(
        tag     = self._ui_components.simulation_description_input,
        label   = "Description", 
        tooltip = "Describe what the simulation does. This will be displayed in the Simulation window."
      )
      dpg.add_button(label="Create Simulation", callback=self._create_simulation)

  def _add_text_input(self, tag, label, tooltip) -> None:
    with dpg.group(horizontal=True):
      dpg.add_text(label)
      dpg.add_input_text(tag=tag)
      if tooltip:
        with dpg.tooltip(parent=tag):
          dpg.add_text(tooltip, wrap=TOOL_TIP_WIDTH)

  def _create_simulation(self) -> None:
    print('hi')
    dpg.configure_item(self._ui_components.new_simulation_window, show=False)
    dpg.delete_item(self._ui_components.new_simulation_window)