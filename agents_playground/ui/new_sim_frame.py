from __future__ import annotations

from enum import StrEnum
import traceback

import wx

from agents_playground.loaders import now_as_string
from agents_playground.projects.new_simulation_builder import NewSimulationBuilder, NewSimulationBuilderException
from agents_playground.projects.simulation_template_options import SimulationTemplateOptions
from agents_playground.ui.validators.cannot_be_empty_validator import CannotBeEmptyValidator
from agents_playground.ui.validators.directory_must_exist_validator import DirectoryMustExistValidator
from agents_playground.ui.validators.pattern_validator import PatternValidator

ALLOWED_SIM_NAME_PATTERN    = r"^([a-z_])+$"
NEW_SIM_GRID_BOARDER        = 5
NEW_SIM_FRAME_TITLE         = 'Create a New Simulation'

NEW_SIM_DIR_TOOLTIP             = 'Specify where the new simulation should be created.\nA new directory will be created in this location.'
NEW_SIM_NAME_TOOLTIP            = 'Assign a unique name for the simulation.\nThis is the name of the simulation file.'
NEW_SIM_TITLE_TOOLTIP           = 'Assign a unique title for the simulation.\nThis will be displayed in the Simulation menu.'
NEW_SIM_DESCRIPTION_TOOLTIP     = 'Describe what the simulation does.\nThis will be displayed in the Simulation window.'
NEW_SIM_SIM_UOM_SYSTEM          = 'Pick the unit of measure (UOM) system for the simulation.'
NEW_SIM_DISTANCE_UOM            = 'Pick the UOM for distance.\nExample: 1 = 1 foot or 1 = 1 centimeter'
NEW_SIM_AUTHOR_TOOLTIP          = 'Optionally, specify your name.\nExample: Joan Smith'
NEW_SIM_LICENSE_TOOLTIP         = 'Optionally, specify the license type name.\nExample: MIT LICENSE'
NEW_SIM_CONTACT_TOOLTIP         = 'Optionally, specify contact information.\nThis could be anything (e.g. email address, GitHub Issues URL).'
NEW_SIM_LANDSCAPE_UOM_SYSTEM    = 'Pick the unit of measure (UOM) system for the landscape.'
NEW_SIM_LANDSCAPE_TILE_SIZE_UOM = 'Pick the UOM for the landscape tiles.\nExample: 1 tile = 1 foot or 1 tile = 1 centimeter'

NEW_SIM_NAME_FORMAT_ERROR        = "Only the lower case characters a-1 and the _ character are allowed."
NEW_SIM_TITLE_FORMAT_ERROR       = "The title cannot be empty."
NEW_SIM_DESCRIPTION_FORMAT_ERROR = "The description cannot be empty."
NEW_SIM_DIR_FORMAT_ERROR         = "The directory must exist."

class SceneUOMOptions(StrEnum):
  METRIC = 'METRIC'
  US_STANDARD = 'US CUSTOMARY'

METRIC_DISTANCE_OPTIONS = [
  'PICOMETER','NANOMETER','MICROMETER','MILLIMETER','CENTIMETER','DECIMETER',
  'METER','DECAMETER','HECTOMETER','KILOMETER','MEGAMETER','GIGAMETER',
  'TERAMETER'
]

STANDARD_DISTANCE_OPTIONS = ['POINT','PICA','INCH','FEET','YARD','MILE','LEAGUE']

CHAR_SPACE      = ' '
CHAR_UNDERSCORE = '_'

class NewSimFrame(wx.Frame):
  def __init__(self, parent):
    super().__init__(parent = parent, title=NEW_SIM_FRAME_TITLE, style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT )
    self._build_ui()

  def _build_ui(self) -> None:
    self.SetSize(600, 525)
    self._panel = wx.Panel(self)
    self._build_sim_description_components() # Note: Must be created before other components. Color is reused.
    self._build_sim_project_home_components()
    self._build_sim_name_components()
    self._build_sim_title_components()  
    self._build_sim_uom_components()  
    self._build_landscape_uom_components()  
    self._build_author_components()
    self._build_license_components()
    self._build_contact_components()
    self._build_create_sim_button()
    self._layout_components()

  def _build_sim_description_components(self) -> None:
    self._sim_description_label = wx.StaticText(self._panel, label="Simulation Description")
    self._sim_description_input = wx.TextCtrl(
      self._panel, 
      value="", 
      style = wx.TE_MULTILINE,
    )

    self._sim_description_input.SetToolTip(NEW_SIM_DESCRIPTION_TOOLTIP)
    self._sim_description_input.SetValidator(
      CannotBeEmptyValidator(
        NEW_SIM_DESCRIPTION_FORMAT_ERROR, 
        self._sim_description_input.GetBackgroundColour(),
        wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)
      )
    )

  def _build_sim_project_home_components(self) -> None:
    # Picker for where to save the simulation project.
    sp: wx.StandardPaths = wx.StandardPaths.Get()
    self._dir_picker = wx.DirPickerCtrl(self._panel, path=sp.GetDocumentsDir())
    self._dir_picker.SetToolTip(NEW_SIM_DIR_TOOLTIP)
    self._dir_picker.SetValidator(
      DirectoryMustExistValidator(
        NEW_SIM_DIR_FORMAT_ERROR,
        self._sim_description_input.GetBackgroundColour(),
        wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)
      )
    )

  def _build_sim_name_components(self) -> None:
    # Input Rules: Lower Case only, a-z, _, no spaces
    self._sim_name_label = wx.StaticText(self._panel, label="Simulation Name")
    self._sim_name_input = wx.TextCtrl(
      self._panel, 
      value="my_simulation", 
      validator=PatternValidator(
        ALLOWED_SIM_NAME_PATTERN, 
        NEW_SIM_NAME_FORMAT_ERROR, 
        self._sim_description_input.GetBackgroundColour(),
        wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)
      )
    )
    self._sim_name_input.SetToolTip(NEW_SIM_NAME_TOOLTIP) 
    
    # Set all the input boxes to have the same color. There is a weird quirk with 
    # wxPython that it creates a multiline TextCtrl with a different color than 
    # a single line.  
    self._sim_name_input.SetBackgroundColour(self._sim_description_input.GetBackgroundColour())

  def _build_sim_title_components(self) -> None:
    self._sim_title_label = wx.StaticText(self._panel, label="Simulation Title")
    self._sim_title_input = wx.TextCtrl(
      self._panel, 
      value="My Simulation",
      validator = CannotBeEmptyValidator(
        NEW_SIM_TITLE_FORMAT_ERROR, 
        self._sim_description_input.GetBackgroundColour(),
        wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)
      )
    )
    self._sim_title_input.SetToolTip(NEW_SIM_TITLE_TOOLTIP)
    
    # Set all the input boxes to have the same color. There is a weird quirk with 
    # wxPython that it creates a multiline TextCtrl with a different color than 
    # a single line. 
    self._sim_title_input.SetBackgroundColour(self._sim_description_input.GetBackgroundColour())
  
  def _build_author_components(self) -> None:
    self._author_label = wx.StaticText(self._panel, label="Author")
    self._author_input = wx.TextCtrl(
      self._panel, 
      value=""
    )
    self._author_input.SetToolTip(NEW_SIM_AUTHOR_TOOLTIP)
    
    # Set all the input boxes to have the same color. There is a weird quirk with 
    # wxPython that it creates a multiline TextCtrl with a different color than 
    # a single line. 
    self._author_input.SetBackgroundColour(self._sim_description_input.GetBackgroundColour())
  
  def _build_license_components(self) -> None:
    self._license_label = wx.StaticText(self._panel, label="Simulation License")
    self._license_input = wx.TextCtrl(
      self._panel, 
      value=""
    )
    self._license_input.SetToolTip(NEW_SIM_LICENSE_TOOLTIP)
    
    # Set all the input boxes to have the same color. There is a weird quirk with 
    # wxPython that it creates a multiline TextCtrl with a different color than 
    # a single line. 
    self._license_input.SetBackgroundColour(self._sim_description_input.GetBackgroundColour())
  
  def _build_contact_components(self) -> None:
    self._contact_label = wx.StaticText(self._panel, label="Contact")
    self._contact_input = wx.TextCtrl(
      self._panel, 
      value=""
    )
    self._contact_input.SetToolTip(NEW_SIM_CONTACT_TOOLTIP)
    
    # Set all the input boxes to have the same color. There is a weird quirk with 
    # wxPython that it creates a multiline TextCtrl with a different color than 
    # a single line. 
    self._contact_input.SetBackgroundColour(self._sim_description_input.GetBackgroundColour())

  def _build_create_sim_button(self) -> None:
    self._create_button = wx.Button(self._panel, label="Create")
    self._create_button.Bind(wx.EVT_BUTTON, self._handle_clicked_create_button)

  def _layout_components(self) -> None:
    grid_sizer = wx.GridBagSizer()
    grid_sizer.Add(self._dir_picker, pos=(1,1), span=(1,2), flag = wx.EXPAND | wx.ALL, border=NEW_SIM_GRID_BOARDER)
    grid_sizer.Add(self._sim_name_label, pos=(2,1), span=(1,1), flag = wx.ALL, border=NEW_SIM_GRID_BOARDER)
    grid_sizer.Add(self._sim_name_input, pos=(2,2), span=(1,1), flag = wx.EXPAND | wx.ALL, border=NEW_SIM_GRID_BOARDER)
    
    grid_sizer.Add(self._sim_title_label, pos=(3,1), span=(1,1), flag = wx.ALL, border=NEW_SIM_GRID_BOARDER)
    grid_sizer.Add(self._sim_title_input, pos=(3,2), span=(1,1), flag = wx.EXPAND | wx.ALL, border=NEW_SIM_GRID_BOARDER)
    
    grid_sizer.Add(self._sim_description_label, pos=(4,1), span=(1,1), flag = wx.ALL, border=NEW_SIM_GRID_BOARDER)
    grid_sizer.Add(self._sim_description_input, pos=(5,1), span=(1,2), flag = wx.EXPAND | wx.ALL, border=NEW_SIM_GRID_BOARDER)
    
    grid_sizer.Add(self._scene_uom_system_label, pos=(6,1), span=(1,1), flag = wx.ALL, border=NEW_SIM_GRID_BOARDER)
    grid_sizer.Add(self._scene_uom_system_choice, pos=(6,2), span=(1,1), flag = wx.EXPAND | wx.ALL, border=NEW_SIM_GRID_BOARDER)
    
    grid_sizer.Add(self._scene_distance_uom_label, pos=(7,1), span=(1,1), flag = wx.ALL, border=NEW_SIM_GRID_BOARDER)
    grid_sizer.Add(self._scene_distance_uom_choice, pos=(7,2), span=(1,1), flag = wx.EXPAND | wx.ALL, border=NEW_SIM_GRID_BOARDER)
    
    #
    grid_sizer.Add(self._landscape_uom_system_label, pos=(8,1), span=(1,1), flag = wx.ALL, border=NEW_SIM_GRID_BOARDER)
    grid_sizer.Add(self._landscape_uom_system_choice, pos=(8,2), span=(1,1), flag = wx.EXPAND | wx.ALL, border=NEW_SIM_GRID_BOARDER)
    
    grid_sizer.Add(self._landscape_tile_size_uom_label, pos=(9,1), span=(1,1), flag = wx.ALL, border=NEW_SIM_GRID_BOARDER)
    grid_sizer.Add(self._landscape_tile_size_uom_choice, pos=(9,2), span=(1,1), flag = wx.EXPAND | wx.ALL, border=NEW_SIM_GRID_BOARDER)
    #
    grid_sizer.Add(self._author_label, pos=(10,1), span=(1,1), flag = wx.ALL, border=NEW_SIM_GRID_BOARDER)
    grid_sizer.Add(self._author_input, pos=(10,2), span=(1,1), flag = wx.EXPAND | wx.ALL, border=NEW_SIM_GRID_BOARDER)
    
    grid_sizer.Add(self._license_label, pos=(11,1), span=(1,1), flag = wx.ALL, border=NEW_SIM_GRID_BOARDER)
    grid_sizer.Add(self._license_input, pos=(11,2), span=(1,1), flag = wx.EXPAND | wx.ALL, border=NEW_SIM_GRID_BOARDER)
    
    grid_sizer.Add(self._contact_label, pos=(12,1), span=(1,1), flag = wx.ALL, border=NEW_SIM_GRID_BOARDER)
    grid_sizer.Add(self._contact_input, pos=(12,2), span=(1,1), flag = wx.EXPAND | wx.ALL, border=NEW_SIM_GRID_BOARDER)

    grid_sizer.Add(self._create_button, pos=(13,2), span=(1,2), flag = wx.ALIGN_RIGHT | wx.ALL, border=NEW_SIM_GRID_BOARDER)

    grid_sizer.AddGrowableCol(2)
    grid_sizer.AddGrowableRow(5)

    self._panel.SetSizerAndFit(grid_sizer)

  def _build_sim_uom_components(self) -> None:
    # Simulations UOM System
    self._scene_uom_system_label = wx.StaticText(self._panel, label="Unit of Measure System")
    self._scene_uom_system_choice = wx.Choice(self._panel, choices = [ e.value for e in SceneUOMOptions])
    self._scene_uom_system_choice.Bind(wx.EVT_CHOICE, self._handle_scene_uom_selected)
    self._scene_uom_system_choice.SetToolTip(NEW_SIM_SIM_UOM_SYSTEM)

    # Scene Distance UOM
    self._scene_distance_uom_label = wx.StaticText(self._panel, label="Distance UOM")
    self._scene_distance_uom_choice = wx.Choice(self._panel, choices = METRIC_DISTANCE_OPTIONS)
    self._scene_distance_uom_choice.SetToolTip(NEW_SIM_DISTANCE_UOM)
  
  def _build_landscape_uom_components(self) -> None:
    # Simulations UOM System
    self._landscape_uom_system_label = wx.StaticText(self._panel, label="Landscape Unit of Measure System")
    self._landscape_uom_system_choice = wx.Choice(self._panel, choices = [ e.value for e in SceneUOMOptions])
    self._landscape_uom_system_choice.Bind(wx.EVT_CHOICE, self._handle_landscape_uom_selected)
    self._landscape_uom_system_choice.SetToolTip(NEW_SIM_LANDSCAPE_UOM_SYSTEM)

    # Scene Distance UOM
    self._landscape_tile_size_uom_label = wx.StaticText(self._panel, label="Tile Size UOM")
    self._landscape_tile_size_uom_choice = wx.Choice(self._panel, choices = METRIC_DISTANCE_OPTIONS)
    self._landscape_tile_size_uom_choice.SetToolTip(NEW_SIM_LANDSCAPE_TILE_SIZE_UOM)

  def _handle_scene_uom_selected(self, event) -> None:
    selection = self._scene_uom_system_choice.GetStringSelection()
    match selection:
      case SceneUOMOptions.METRIC:
        self._scene_distance_uom_choice.SetItems(METRIC_DISTANCE_OPTIONS)
      case SceneUOMOptions.US_STANDARD:
        self._scene_distance_uom_choice.SetItems(STANDARD_DISTANCE_OPTIONS)
      case _:
        wx.MessageBox(
          message = f'There was an error while trying to select the unit of measure.\nCannot handle value {selection}.',
          caption = 'Error',
          parent  = self,
          style   = wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP | wx.CENTRE
        )
  
  def _handle_landscape_uom_selected(self, event) -> None:
    selection = self._landscape_uom_system_choice.GetStringSelection()
    match selection:
      case SceneUOMOptions.METRIC:
        self._landscape_tile_size_uom_choice.SetItems(METRIC_DISTANCE_OPTIONS)
      case SceneUOMOptions.US_STANDARD:
        self._landscape_tile_size_uom_choice.SetItems(STANDARD_DISTANCE_OPTIONS)
      case _:
        wx.GenericMessageDialog(
          message = f'There was an error while trying to select the unit of measure.\nCannot handle value {selection}.',
          caption = 'Error',
          parent  = self,
          style   = wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP | wx.CENTRE
        )

  def _handle_clicked_create_button(self, event) -> None:
    """
    Event handler for clicking the Create Simulation button.

    Validates that the selected directory exits, the name is valid, and the title isn't empty.
    If all inputs are valid, then it attempts to create a new simulation. 
    """
    if self.Validate():
      try:
        options = SimulationTemplateOptions(
          simulation_name        = self._sim_name_input.GetValue(),
          simulation_title       = self._sim_title_input.GetValue(),
          simulation_description = self._sim_description_input.GetValue(),
          parent_directory       = self._dir_picker.GetPath(),
          creation_time          = now_as_string(),
          scene_uom_system       = self._scene_uom_system_choice.GetStringSelection().replace(CHAR_SPACE, CHAR_UNDERSCORE),
          scene_distance_uom     = self._scene_distance_uom_choice.GetStringSelection(),
          author                 = self._author_input.GetValue(),
          license                = self._license_input.GetValue(),
          contact                = self._contact_input.GetValue(),
          landscape_uom_system   = self._landscape_uom_system_choice.GetStringSelection().replace(CHAR_SPACE, CHAR_UNDERSCORE),
          tile_size_uom          = self._landscape_tile_size_uom_choice.GetStringSelection()
        )
        NewSimulationBuilder().build(options)
        self.Close()
        wx.GenericMessageDialog(
          message = f'New simulation {options.simulation_title} created at {options.parent_directory}/{options.simulation_name}.',
          caption = 'Success',
          parent  = self,
          style   = wx.OK | wx.ICON_INFORMATION | wx.STAY_ON_TOP | wx.CENTRE
        ).ShowModal()
      except NewSimulationBuilderException as e:
        error_msg = (
          'There was an error while trying to create a new simulation.\n',
          'The error was.\n',
          str(e),
          '\n\n',
          traceback.format_exc()
        )

        error_dialog = wx.GenericMessageDialog(
          parent  = self,
          message = ''.join(error_msg),
          caption = 'Error',
          style   = wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP | wx.CENTRE
        )
        error_dialog.ShowModal()