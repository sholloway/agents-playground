from dataclasses import dataclass
import datetime as dt 

from agents_playground.fp import Maybe, Nothing, Something, wrap_field_as_maybe
from agents_playground.loaders import str_to_datetime
from agents_playground.uom import DateTime

@dataclass
class LandscapeFileCharacteristics:
  """
  Metadata about a landscape file.
  """
  author: Maybe[str] # Can be any string but intended to be First Name Last Name 
  license: Maybe[str] # The license type for this attribute. 
  contact: Maybe[str] # Contact information. Could be anything.
  creation_time: Maybe[DateTime] # When the file was initially created in the format YYYY-MM-DD hh:mm:ss.micro
  updated_time: Maybe[DateTime] # When the file was last updated in the format YYYY-MM-DD hh:mm:ss.micro

  def __post_init__(self) -> None:
    """
    Handle initialization use cases.
    """
    wrap_field_as_maybe(self, 'author')
    wrap_field_as_maybe(self, 'license')
    wrap_field_as_maybe(self, 'contact')
    wrap_field_as_maybe(self, 'creation_time', str_to_datetime)
    wrap_field_as_maybe(self, 'updated_time', str_to_datetime)