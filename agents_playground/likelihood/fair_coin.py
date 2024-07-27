from random import choices
from agents_playground.likelihood.coin import HEADS, TAILS, Coin


class FairCoin(Coin):
    def flip(self) -> bool:
        """
        Flip a coin to determine an outcome.
        Returns True for heads and False for tails..
        """
        return choices((HEADS, TAILS))[0]
