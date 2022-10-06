from dataclasses import dataclass, field
from typing import Dict, List, Union

from agents_playground.core.constants import UPDATE_BUDGET
from agents_playground.core.samples import Samples
from agents_playground.core.types import Sample

@dataclass
class SimulationStatistics:
  per_frame_samples: Dict[str, Samples] = field(init=False) 