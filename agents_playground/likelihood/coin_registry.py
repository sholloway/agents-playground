
from typing import Dict, Final

from agents_playground.likelihood.coin import Coin
from agents_playground.likelihood.fair_coin import FairCoin
from agents_playground.likelihood.weighted_coin import SureThing, WillyLowman

COIN_REGISTRY: Final[Dict[str, Coin]] = {
  'fair_coin': FairCoin(),
  'always_heads': SureThing(),
  'always_tails': WillyLowman()
}