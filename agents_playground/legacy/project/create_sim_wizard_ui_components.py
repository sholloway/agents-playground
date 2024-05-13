from dataclasses import dataclass
from typing import Callable

from agents_playground.simulation.tag import Tag
@dataclass
class CreateSimWizardUIComponents:
  new_simulation_window: Tag
  project_name_input: Tag
  simulation_title_input: Tag
  simulation_description_input: Tag
  select_directory_button: Tag
  selected_directory_display: Tag
  
  def __init__(self, generate_uuid: Callable[..., Tag]) -> None:
    self.new_simulation_window        = generate_uuid()
    self.project_name_input           = generate_uuid()
    self.simulation_title_input       = generate_uuid()
    self.simulation_description_input = generate_uuid()
    self.select_directory_button      = generate_uuid()
    self.selected_directory_display   = generate_uuid()