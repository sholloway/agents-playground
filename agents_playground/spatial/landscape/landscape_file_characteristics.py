from dataclasses import dataclass

from agents_playground.fp import Maybe
from agents_playground.uom import DateTime

@dataclass
class LandscapeFileCharacteristics:
  """
  Metadata about a landscape file.
  """
  author: Maybe[str] # Can be any string but intended to be First Name Last Name 
  license: Maybe[str] # The license type for this attribute. 
  contact: Maybe[str] # Contact information. Could be anything.
  creation_time: Maybe[DateTime] # When the file was initially created in the format YYYY-MM-DD hh:mm:ss.
  updated_time: Maybe[DateTime] # When the file was last updated in the format YYYY-MM-DD hh:mm:ss.