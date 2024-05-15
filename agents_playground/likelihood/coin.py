from abc import abstractmethod
from typing import Protocol

HEADS = True
TAILS = False


class Coin(Protocol):
    """
    Contract for a coin that can be flipped to determine outcomes.
    """

    @abstractmethod
    def flip(self) -> bool:
        """
        Flip a coin to determine an outcome.
        Returns True for heads and False for tails..
        """
        ...
