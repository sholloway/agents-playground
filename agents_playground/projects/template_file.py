from typing import NamedTuple


class TemplateFile(NamedTuple):
  template_name: str
  template_location: str
  target_location: str