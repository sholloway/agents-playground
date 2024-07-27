from dataclasses import dataclass

from agents_playground.fp import Maybe, Nothing, wrap_field_as_maybe
from agents_playground.loaders import str_to_datetime
from agents_playground.uom import DateTime


@dataclass
class SceneFileCharacteristics:
    author: Maybe[str] = (
        Nothing()
    )  # Can be any string but intended to be First Name Last Name
    license: Maybe[str] = Nothing()  # The license type for this attribute.
    contact: Maybe[str] = Nothing()  # Contact information. Could be anything.
    creation_time: Maybe[DateTime] = Nothing()  # 2024-01-21 hh:mm:ss
    updated_time: Maybe[DateTime] = Nothing()  # YYYY-MM-DD hh:mm:ss

    def __post_init__(self) -> None:
        """
        Handle initialization use cases.
        """
        wrap_field_as_maybe(self, "author")
        wrap_field_as_maybe(self, "license")
        wrap_field_as_maybe(self, "contact")
        wrap_field_as_maybe(self, "creation_time", str_to_datetime)
        wrap_field_as_maybe(self, "updated_time", str_to_datetime)


"""
This is bombing because the initialization function has named parameters
for each of the fields. The updated_time doesn't exist in the dict when
it's being passed in.
"""
