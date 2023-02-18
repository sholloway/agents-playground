from __future__ import annotations
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
  """
  A UI based wizard for creating a simulation. It is designed as a singleton
  to prevent multiple instance being open at the same time. 
  This is redundant when the window is launched as a modal.
  """
  _instance: CreateSimWizard | None = None
  
  def __new__(cls):
    if cls._instance is None:
        cls._instance = super(CreateSimWizard, cls).__new__(cls)
        cls._ui_components = CreateSimWizardUIComponents(dpg.generate_uuid)
        cls._active = False
    return cls._instance
  
  def launch(self) -> None:
    if not self._active:
      self._active = True
      with dpg.window(
        tag=self._ui_components.new_simulation_window, 
        label="Create a New Simulation", 
        width = 518, 
        height= 600,
        no_resize=True
        # modal=True
      ):
        with dpg.table(header_row=False):
          dpg.add_table_column(width_fixed=True)
          dpg.add_table_column(width_stretch=True, init_width_or_weight=0.0)

          self._add_text_input(
            tag       = self._ui_components.simulation_name_input,
            label     = "Name", 
            tooltip   = "Assign a unique name for the simulation. This is the name of the simulation file.",
            hint      = "Example: my_simulation",
            no_spaces = True
          )

          self._add_text_input(
            tag     = self._ui_components.simulation_title_input,
            label   = "Title", 
            tooltip = "Assign a unique title for the simulation. This will be displayed in the Simulation menu.",
            hint    = "Example: My Simulation"
          )

          self._add_text_input(
            tag     = self._ui_components.simulation_description_input,
            label   = "Description", 
            tooltip = "Describe what the simulation does. This will be displayed in the Simulation window.",
            multiline = True
          )

        dpg.add_button(label="Create Simulation", callback=self._create_simulation)


  def _add_text_input(self, tag, label, tooltip, hint = '', multiline=False, no_spaces=False) -> None:
    with dpg.table_row():
      dpg.add_text(label)
      dpg.add_input_text(tag=tag, multiline=multiline, width = 400, hint=hint, no_spaces=no_spaces)
      if tooltip:
        with dpg.tooltip(parent=tag):
          dpg.add_text(tooltip, wrap=TOOL_TIP_WIDTH)

  def _create_simulation(self) -> None:
    """Create the simulation and close the window."""
    dpg.configure_item(self._ui_components.new_simulation_window, show=False)
    dpg.delete_item(self._ui_components.new_simulation_window)
    self._active = False