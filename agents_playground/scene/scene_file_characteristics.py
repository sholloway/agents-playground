from dataclasses import dataclass

from agents_playground.fp import Maybe
from agents_playground.uom import DateTime

@dataclass
class SceneFileCharacteristics:
  author: Maybe[str] # Can be any string but intended to be First Name Last Name 
  license: Maybe[str] # The license type for this attribute. 
  contact: Maybe[str] # Contact information. Could be anything.
  creation_time: Maybe[DateTime] # 2024-01-21 hh:mm:ss
  updated_time: Maybe[DateTime] #YYYY-MM-DD hh:mm:ss