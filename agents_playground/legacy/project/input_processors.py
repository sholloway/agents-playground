from abc import ABC, abstractmethod
from gettext import dpgettext
from typing import Any

import dearpygui.dearpygui as dpg

from agents_playground.legacy.project.new_project_validation_error import NewProjectValidationError
from agents_playground.legacy.project.project_template_options import ProjectTemplateOptions
from agents_playground.simulation.tag import Tag

class InputProcessor(ABC):
  @abstractmethod
  def grab_value(self, template_options: ProjectTemplateOptions) -> None:
    """Fetches the value from the target input."""

  @abstractmethod
  def validate(self) -> None:
    """Runs any required validation on the input value."""
    
class TextInputProcessor(InputProcessor):
  def __init__(self, tag: Tag, error_msg: str, template_field_name: str) -> None:
    self._tag = tag 
    self._value: str | None = None 
    self._error_msg = error_msg
    self._template_field_name = template_field_name

  def grab_value(self, template_options: ProjectTemplateOptions) -> None:
    self._value = dpg.get_value(self._tag)
    setattr(template_options, self._template_field_name, self._value)


  def validate(self) -> None: 
    if self._value is None or self._value.strip() == '':
      raise NewProjectValidationError(self._error_msg)

class TextFieldProcessor(InputProcessor):
  def __init__(self, object: Any, field_name: str, error_msg: str, template_field_name: str) -> None:
    self._object: Any = object 
    self._field_name: str = field_name
    self._value: str | None = None 
    self._error_msg = error_msg
    self._template_field_name = template_field_name

  def grab_value(self, template_options: ProjectTemplateOptions) -> None:
    self._value =  getattr(self._object, self._field_name)
    setattr(template_options, self._template_field_name, self._value)

  def validate(self) -> None: 
    if self._value is None or self._value.strip() == '':
      raise NewProjectValidationError(self._error_msg)