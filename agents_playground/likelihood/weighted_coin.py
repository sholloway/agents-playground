from random import choices
from agents_playground.likelihood.coin import HEADS, TAILS, Coin


class WeightedCoin(Coin):
    def __init__(self, weight: float) -> None:
        self.weight = weight

    def flip(self) -> bool:
        """
        Flip a weighted coin based on the likelihood value, calculate whether to do an action or not.
        Returns True when heads is flipped.
        """
        return choices((HEADS, TAILS), cum_weights=(self.weight, 1.00), k=1)[0]


class SureThing(Coin):
    def flip(self) -> bool:
        """
        A coin that always lands heads.
        """
        return HEADS


class WillyLowman(Coin):
    """A rigged coin that always comes up Tails."""

    def flip(self) -> bool:
        """
        A coin that always lands heads.
        """
        return TAILS
