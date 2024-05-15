import datetime
from enum import StrEnum

# This should be moved to a package with a wider scope.
DateTime = datetime.datetime


class SystemOfMeasurement(StrEnum):
    US_CUSTOMARY = (
        "US_CUSTOMARY"  # Often referred to as "Standard" in the United States.
    )
    METRIC = "METRIC"  # The International System of Units


class LengthUOM(StrEnum):
    # USCustomary Units: https://en.wikipedia.org/wiki/United_States_customary_units
    POINT = "POINT"
    PICA = "PICA"
    INCH = "INCH"
    FEET = "FEET"  # 0.3048 meters
    YARD = "YARD"
    MILE = "MILE"
    LEAGUE = "LEAGUE"

    # International System of Units (i.e. Metric)
    PICOMETER = "PICOMETER"
    NANOMETER = "NANOMETER"
    MICROMETER = "MICROMETER"
    MILLIMETER = "MILLIMETER"
    CENTIMETER = "CENTIMETER"
    DECIMETER = "DECIMETER"
    METER = "METER"  # 3.28084 feet.
    DECAMETER = "DECAMETER"
    HECTOMETER = "HECTOMETER"
    KILOMETER = "KILOMETER"
    MEGAMETER = "MEGAMETER"
    GIGAMETER = "GIGAMETER"
    TERAMETER = "TERAMETER"
