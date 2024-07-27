from enum import Enum, auto
from typing import Protocol


class SensationType(Enum):
    Visual = auto()
    Audible = auto()
    Smell = auto()
    Tactile = auto()
    Taste = auto()
    Vestibular = auto()


class Sensation(Protocol):
    """
    A sensation is the detection of a stimuli by one of the Nervous Systems receptors.
    It is stored in the Sensory Memory and consumed by the Perception System.

    Examples:
    - The eyes see another agent.
    - The ears hear a sound.
    - The nose smells a smell.
    - The skin feels the temperature.
    - The mouth feels dry.
    """

    type: SensationType
