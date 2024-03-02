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
  creation_time: Maybe[DateTime] # When the file was initially created in the format YYYY-MM-DD hh:mm:ss.micro
  updated_time: Maybe[DateTime] # When the file was last updated in the format YYYY-MM-DD hh:mm:ss.micro

# now = datetime.datetime.now(datetime.timezone.utc) -> datetime.datetime(2024, 3, 1, 12, 42, 54, 510655, tzinfo=datetime.timezone.utc)
# now has accessors such as now.year, now.day, and so on.
# now.strftime("%Y-%m-%d %H:%M:%S.%f %Z") -> '2024-03-01 12:42:54.510655 UTC'

# parsed_ts = datetime.datetime.strptime('2024-03-01 12:42:54.510655 UTC',"%Y-%m-%d %H:%M:%S.%f %Z")
# BUG: This isn't parsing the timezone...So you need to do the below. :(
# parsed_ts = datetime.datetime.strptime('2024-03-01 12:42:54.510655 UTC',"%Y-%m-%d %H:%M:%S.%f %Z").replace(tzinfo=datetime.timezone.utc)
  