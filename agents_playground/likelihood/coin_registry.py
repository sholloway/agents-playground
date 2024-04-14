
from enum import StrEnum
from typing import Dict, Final

from agents_playground.likelihood.coin import Coin
from agents_playground.likelihood.fair_coin import FairCoin
from agents_playground.likelihood.weighted_coin import SureThing, WillyLowman

class CoinType(StrEnum):
  FAIR = 'fair_coin'
  ALWAYS_HEADS = 'always_heads'
  ALWAYS_TAILS = 'always_tails'

COIN_REGISTRY: Final[Dict[str, Coin]] = {
  CoinType.FAIR: FairCoin(),
  CoinType.ALWAYS_HEADS: SureThing(),
  CoinType.ALWAYS_TAILS: WillyLowman()
}